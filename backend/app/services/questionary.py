from app.services.llms import llama
from app.utils.general import (
    extract_and_validate_json_objects,
    split_text_into_chunks,
)


def resolve_the_final_answer(
    answers: list[str],
    question: str,
    resolve_as_json=False,
):
    pipe = llama.get_pipe()
    tokenizer = llama.get_tokenizer()
    print(f"\n--- Resolving the Final Answer ---\n")
    max_context_size = 2048  # Maximum context size of the model
    max_generated_tokens = 500  # Adjust as needed
    # Join all answers into a single string
    section_marker = "[SEP]"

    summarized_answers = (
        section_marker.join(answers) if len(answers) > 1 else answers[0]
    )
    summarized_answers = summarized_answers

    answers_tokens = len(tokenizer.encode(summarized_answers))

    json_strc = '{"Final Answer":"","Final Explanation":""}'

    finalising_instruction = f"""
    Prompt: Analyse carefully the provided answers, which all responding to this question: {question}. 
    Understand which information are usefull to answer the question from the provided answers, and extract these informations to return the best possible answer. Explain in a short summary your answer.    
    Its very important, that you responding in the same language as the question.
    Follow this JSON structure for your answer: {json_strc}.
    """

    # Tokenize the system instruction
    system_instructions_tokens = len(tokenizer.encode(finalising_instruction))

    max_input_tokens = (
        max_context_size - system_instructions_tokens - max_generated_tokens
    )

    if max_input_tokens <= 0:
        print(
            "The system instructions and the maximum generated tokens exceed the context window size."
        )
        return f"ERROR: The system instructions and the maximum generated tokens exceed the context window size."

    # If the combined tokens exceed the context window, split answers into chunks
    if answers_tokens > max_input_tokens and section_marker in summarized_answers:
        # in case the answers joined to one text, are too long for the model to handle it at once,
        # it will split the answers by the split marker and recursively call this func with the new splitted answers
        # (which does it 2 times per run, it calls 2 times this func recursivly, each call takes the half of the spltted answers).
        # the shortend answers will be concated into one array and repassed into this function.
        #
        # ---> this logic loops recursivly until the answers, joined to one txt, fit into the context window,
        # to resolve a final answer. (Which is the last else case of this statement chain)

        print(
            "\nSummarized answers exceed, joined to one text, the maximum window ctx tokens, splitting into smaller chunks.\n"
        )
        # recursively split input array by half, until it fits into the context window

        splitted_answers = summarized_answers.split(section_marker)

        middle = len(splitted_answers) // 2 + len(splitted_answers) % 2

        first_half = resolve_the_final_answer(
            splitted_answers[:middle], question, resolve_as_json=False
        )
        second_half = resolve_the_final_answer(
            splitted_answers[middle:], question, resolve_as_json=False
        )

        if first_half == "NOANSWER" and second_half == "NOANSWER":
            return "NOANSWER"

        concated_list = []

        if not first_half == "NOANSWER":
            concated_list.append(first_half)
        if not second_half == "NOANSWER":
            concated_list.append(second_half)

        return resolve_the_final_answer(
            concated_list, question, resolve_as_json=resolve_as_json
        )

    elif answers_tokens > max_input_tokens:
        # runs only if a single answer is passed and its too long for the model.
        #
        # The single Answer will joined to one tagless text and chunked with the tokenizer in smaller passable text chunks.
        # The resolving answers, for each chunkm, will be XML formatted and repassed to this func.
        print(
            "\nSummarized answer exceeds the maximum input tokens, splitting into smaller chunks.\n"
        )

        # removing tags from single answer and pass it as text content to the model
        sanitized_summarized_answers = summarized_answers

        answer_chunks = split_text_into_chunks(
            sanitized_summarized_answers,
            max_input_tokens,
            tokenizer=tokenizer,
        )

        # Recursively resolve the final answer with the new chunks
        new_answers = []

        for i, chunk in enumerate(answer_chunks):
            print(
                f"\n--- Summarizing Splitted Answer Chunk {i+1}/{len(answer_chunks)} ---\n"
            )
            try:
                # to prevent irritation, this complete_prmpt takes the prompt with the  tag,
                # because the model needs it to respond properly
                # but the single answers and respones are not passed with tags.

                complete_prmpt = f"""{finalising_instruction}{chunk}"""
                print(complete_prmpt)
                response = ""
                prinatble_rsp = ""

                streamed = pipe(
                    complete_prmpt,
                    max_new_tokens=max_generated_tokens,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )[-1]["generated_text"]

                data = extract_and_validate_json_objects(streamed)

                if len(data) == 0:
                    print(streamed)
                    raise Exception("No valid JSON objects found in the final answer.")

                data = data[-1]

                for key, value in data.items():
                    if "NOANSWER" in value or value.strip() == "":
                        continue

                    prinatble_rsp += f"\n{key}: {value}\n"
                    response += f"\n{key}: {value}"

                # important to append the response with tags,
                # because it will be passed to this func with shortened answers,
                # which can be prob handles through the first if statement above
                if not response == "":
                    print(f"{i+1})\n\n{prinatble_rsp}")
                    new_answers.append(f"{response}")

            except Exception as e:
                print(f"Failed to process chunk {i+1}")
                print(e)
                return f"ERROR: Failed to process chunk {i+1} {str(e)}"

        # Recursive call with the new summarized answers
        return (
            resolve_the_final_answer(
                new_answers, question, resolve_as_json=resolve_as_json
            )
            if len(new_answers)
            else "NOANSWER"
        )

    else:
        # If all answers from the passed array, joined to one text, fits into this context window, it will generate the final answer
        # but it resolves it as xml formatted response in case this funtion was called recursively,
        # so to resolve a better human readable response, use the "remove_xmt_html_tags" utility.
        try:
            sa = summarized_answers.replace(section_marker, "\n")
            finalising_instruction = f"{finalising_instruction}\n{sa}"
            response = ""
            prinatble_rsp = ""
            print(finalising_instruction)
            try:

                streamed = pipe(
                    finalising_instruction,
                    max_new_tokens=max_generated_tokens,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )[-1]["generated_text"]

            except IndexError:
                print("List index out of range, while resolving the final answer.")
                raise Exception(
                    "List index out of range, while resolving the final answer."
                )

            data = extract_and_validate_json_objects(streamed)

            if len(data) == 0:
                print(streamed)
                raise Exception("No valid JSON objects found in the final answer.")

            data = data[-1]

            for key, value in data.items():
                if "NOANSWER" in value or value.strip() == "":
                    print(key.upper(), "NO ANSWER FOUND")
                    return "NOANSWER"

                prinatble_rsp += f"\n{key}: {value}\n"
                response += f"\n{key}: {value}"

            # it needs to return the response with tags,
            # because the func is recursive,
            # in case the ctx window tkns exceeds the max and returning the response with tags,
            # makes it easier for the model to repsond properly

            return response if not resolve_as_json else data

        except Exception as e:
            print("Failed to generate the final answer")
            print(e)
            return f"ERROR: Failed to generate the final answer {str(e)}"


def find_answer_in_text(question: str, text_context: str = ""):
    pipe = llama.get_pipe()
    tokenizer = llama.get_tokenizer()

    json_structure = '{"Answer":"","Explanation":"","Text Excerpt":""}'

    system_instructions = f"""
    Prompt: Please answer the question: {question}, briefly and precisely. 
    Include a brief explanation of why you came to your answer and quote the relevant text excerpt from the context. 
    Do not include the question itself in your answer. 
    Your answer MUST be in the SAME LANGUAGE as the question you are answering. 
    Use ONLY the given text as context for your answer. 
    If you cannot answer the question based on the textual content, you MUST answer 'NOANSWER'. 
    If you can answer the question based on the text content, follow this json structure for your answer: {json_structure}.
    """

    # Berechne die Anzahl der Tokens in den Systemanweisungen
    system_instructions_tokens = len(tokenizer.encode(system_instructions))

    # Definiere die maximale Kontextgröße und die maximale Anzahl generierter Tokens
    max_context_size = 2048
    max_generated_tokens = 600  # Passe dies bei Bedarf an

    # Berechne die maximale Anzahl von Tokens für die Eingabe
    max_input_tokens = (
        max_context_size - system_instructions_tokens - max_generated_tokens
    )

    if max_input_tokens <= 0:
        print(
            "The system instructions and the maximum generated tokens exceed the context window size."
        )
        return "ERROR: The system instructions and the maximum generated tokens exceed the context window size."

    answers = []
    chunks = split_text_into_chunks(text_context, max_input_tokens, tokenizer=tokenizer)
    print(f"Total Chunks: {len(chunks)}")
    json_answers = []
    for i, chunk in enumerate(chunks):
        print(f"\n--- Prüfe Chunk {i+1} ---\n", end="\n", flush=True)
        try:
            response = f""  # "@@@"" used to split the answers for the final evaluation at the right point, without destroying the answers logic
            complete_prmpt = f"{system_instructions}\n{chunk}"
            prinatble_rsp = f"\nResponse from text chunk {i+1}:\n\n"

            streamed = pipe(
                complete_prmpt,
                max_new_tokens=max_generated_tokens,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )[-1]["generated_text"]

            data = extract_and_validate_json_objects(streamed)

            if len(data) == 0:
                continue

            data = data[-1]

            for key, value in data.items():
                if "NOANSWER" in value or value.strip() == "":
                    continue

                prinatble_rsp += f"\n{key}: {value}\n"
                response += f"\n{key}: {value}"

            if response == "":
                continue

            json_answers.append(data)

            if not response == "":
                print(prinatble_rsp)
                answers.append(f"""{response}""")

        except Exception as e:
            print("Failed to run model on chunk")
            print(e)
            return f"ERROR: Failed to run model on chunk {str(e)}"

    print(f"\n{len(answers)} answers found in the text.\n")
    if len(answers) > 0:
        print("\n\n", answers, "\n\n")

    if len(answers) == 0:
        print("No answers found in the text.")
        return "It seems there is no answer in the text."

    if len(answers) == 1:
        print("\n\nOnly one answer found in the text.")
        return json_answers[0]

    final = resolve_the_final_answer(answers, question, resolve_as_json=True)

    if final == "NOANSWER":
        print(answers)
        return "it seems there is no answer in the text."

    # response errored out, code logic failed not the model
    if isinstance(final, str) and final.startswith("ERROR"):
        print("\n\nFailed to resolve the final answer:", final)
        print("\n\nAnswers:", answers)
        print("\n\nfailed to resolve final answer, retrying....")
        final = resolve_the_final_answer(answers, question, resolve_as_json=True)

        if not isinstance(final, dict):
            print("\n\nFailed to resolve the final answer again..", answers)
            return "ERROR: Failed to resolve the final answer!"

        return final

    if isinstance(final, dict):
        print("\n\nFinal Answer:", final)
        print("\n\n", answers, "\n\n")
        return final

    print("Something went wrong...", final)
    return final


def initiate(question: str, text_context: str = ""):
    print(f"\n--- Initiating Questionary ---\n")

    if not text_context:
        print("No text context provided.")
        return "ERROR: No text context provided."

    if not question:
        print("No question provided.")
        return "ERROR: No question provided."

    rsp = find_answer_in_text(question, text_context)
    print(f"\n--- Questionary Completed ---\n")
    print(rsp)
    return rsp


__all__ = ["initiate"]
