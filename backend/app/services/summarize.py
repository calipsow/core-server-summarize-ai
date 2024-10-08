from app.services.llms import llama, utils
from app.utils.general import (
    extract_and_validate_json_objects,
    split_text_into_chunks,
    concat_json_objects_by_keys,
)


def finalise_summarized_text(summarized_json: list[dict], title: str) -> dict | None:
    """
    Finalize the summarized text by joining the individual chunks.

    Args:
        summarized_texts (list[dict]): The list of summarized text chunks,
        title (str): The title of the original text.
        return_json (bool): Whether to return the final summary as a JSON object or a string. Defaults to False.
    Returns:

        (dict): The finalized summarized text in a JSON object.

        (None): If the finalization fails.
    """

    json_structure = '{"Title":"","Final Summary":""}'

    finalise_summarized_text_instructions = f"""
    Prompt: Analyse carefully the text summaries, each summarize a single text section of one large text with the title: {title}. Understand which informations are important and most relevant from each summary. Then validate your extracted informations carefully and generate, one final summary for the original text. It is absolutely important, that you use the same language as the title of the original text and that you follow this JSON structure for your answer: {json_structure}."""

    result = llama.generate_chat_based_assistant(finalise_summarized_text_instructions)

    if isinstance(result, str):
        print(result)
        raise Exception("Failed to load the summarization pipeline or tokenizer.")

    model, tokenizer, messages = result

    print("unpack summarized_json list dicts to one string...")
    # join json objects to one string
    joined_text = ""
    for data in summarized_json:
        if not isinstance(data, dict):
            continue
        for key, value in data.items():
            if value != "":
                joined_text += f"{key}: {value}\n"

    system_instructions_tokens = len(
        tokenizer.encode(finalise_summarized_text_instructions)
    )

    # Define the maximum context size and maximum generated tokens
    max_context_size = 2048
    max_generated_tokens = 500  # Adjust as needed

    # Calculate the maximum number of tokens for the input
    max_input_tokens = (
        max_context_size - system_instructions_tokens - max_generated_tokens
    )

    if max_input_tokens <= 0:
        print(
            "The system instructions and the maximum generated tokens exceed the context window size."
        )
        return None

    summary_tokens = len(tokenizer.encode(joined_text))

    final_answer = None

    if summary_tokens > max_input_tokens:
        print(
            "Summarized answers exceed the maximum input tokens, splitting into smaller chunks."
        )
        # Split the answers into smaller chunks
        answer_chunks = split_text_into_chunks(
            joined_text, max_input_tokens, tokenizer=tokenizer
        )

        # Recursively resolve the final answer with the new chunks
        new_summaries = []
        for i, chunk in enumerate(answer_chunks):
            print(f"\n--- Summarizing Summary Chunk {i+1} ---\n")
            prompt = f"{finalise_summarized_text_instructions}{chunk}"
            try:
                print(f"Prompt tokens total: {len(tokenizer.encode(prompt))}\n")

                print(f"Max Generated Tokens: {max_generated_tokens}\n")

                print(
                    f"Context window size: {len(tokenizer.encode(prompt)) + max_generated_tokens}\n"
                )

                if len(messages) > 1:
                    messages[1] = {"role": "user", "content": chunk}
                else:
                    messages.append({"role": "user", "content": chunk})

                print(f"Messages: {messages}")

                streamed = utils.generate_output_from_model(
                    model=model,
                    tokenizer=tokenizer,
                    messages=messages,
                    max_new_tokens=max_generated_tokens,
                )

                data = extract_and_validate_json_objects(streamed)

                if len(data) == 0:
                    print("No JSON object found in the response.")
                    print(streamed)
                    continue

                data = concat_json_objects_by_keys(data)

                if not data:
                    print(f"\n\nFailed to extract summarized text on chunk {i+1}\n\n")
                    print(streamed)
                    continue

                print(f"\nIntermediate Summary {i+1}: {data}\n")

                new_summaries.append(data)

            except Exception as e:
                print(f"Failed to process chunk {i+1}")
                print(e)
                continue  # Proceed to the next chunk if an error occurs

        # Recursive call with the new summarized answers
        print(
            f"\n\nRecursive call with the new summarized answers: {new_summaries}\n\n"
        )
        finalized_summary = finalise_summarized_text(new_summaries, title)

        if not finalized_summary:
            print("Failed to finalize the summarized text.")
            return None

        return finalized_summary

    else:
        prompt = f"{finalise_summarized_text_instructions}{joined_text}"
        try:
            print(f"Prompt tokens total: {len(tokenizer.encode(prompt))}\n")
            print(f"Max Generated Tokens: {max_generated_tokens}\n")

            print(
                f"Context window size: {len(tokenizer.encode(prompt)) + max_generated_tokens}\n"
            )

            if len(messages) > 1:
                messages[1] = {"role": "user", "content": joined_text}
            else:
                messages.append({"role": "user", "content": joined_text})

            print(f"Messages: {messages}")

            streamed = utils.generate_output_from_model(
                model=model,
                tokenizer=tokenizer,
                messages=messages,
                max_new_tokens=max_generated_tokens,
            )

            print(streamed)

            data = extract_and_validate_json_objects(streamed)

            if len(data) == 0:
                print("No JSON object found in the response.")
                raise Exception("No JSON object found in the response.")

            data = concat_json_objects_by_keys(data)

            if not data:
                e = f"\n\nFailed to extract summary from text\n\n"
                raise Exception(e)

            return data

        except Exception as e:
            print("Failed to generate the final answer")
            print(e)
            return None


def summarize_text(text: str, title: str) -> dict | None:
    """
    Summarize the input text using the model.

    Args:
        text (str): The input text to summarize.

    Returns:
        str: The summarized text.
    """
    system_instructions = """
    Prompt: Understand and analyse the text carefully. Extract the informations which are most important and use them to summarize the text. It is very important, that you use the same language as the text. Follow this JSON structure for your answer: {"Title":"","Summary":""}."""

    result = llama.generate_chat_based_assistant(system_instructions)

    if isinstance(result, str):
        print(result)
        raise Exception("Failed to load the summarization pipeline or tokenizer.")

    model, tokenizer, messages = result

    print(f"Tokenize System Instructions...")

    system_instructions_tokens = len(tokenizer.encode(system_instructions))

    # Define the maximum context size and maximum generated tokens
    max_context_size = 1845

    max_generated_tokens = 300  # Adjust as needed

    print(f"Calculate the maximum number of tokens for the input...")

    # Calculate the maximum number of tokens for the input
    max_input_tokens = (
        max_context_size - system_instructions_tokens - max_generated_tokens
    )

    if max_input_tokens <= 0:
        print(
            "The system instructions and the maximum generated tokens exceed the context window size."
        )
        return None

    print(
        f"Max Input Tokens: {max_input_tokens}, split the text into sections based on that..."
    )

    text_chunks = split_text_into_chunks(text, max_input_tokens, tokenizer=tokenizer)

    print(f"Text split into {len(text_chunks)} sections.")

    summarized_json = []

    for i, chunk in enumerate(text_chunks):
        print(f"\n--- Summarizing Text Section {i+1} ---\n", end="\n")
        try:
            prompt = f"{system_instructions}{chunk}"

            print(f"Prompt tokens total: {len(tokenizer.encode(prompt))}\n")

            print(f"Max Generated Tokens: {max_generated_tokens}\n")

            print(
                f"Total context window size: {len(tokenizer.encode(prompt)) + max_generated_tokens}\n"
            )

            if len(tokenizer.encode(prompt)) + max_generated_tokens > max_context_size:
                print(f"Prompt tokens total exceeds the context window size.\n")
                raise Exception("Prompt tokens total exceeds the context window size.")

            if len(messages) > 1:
                messages[1] = {"role": "user", "content": chunk}

            else:
                messages.append({"role": "user", "content": chunk})

            summarized_text = utils.generate_output_from_model(
                model=model,
                tokenizer=tokenizer,
                messages=messages,
                max_new_tokens=max_generated_tokens,
            )

            print(
                f"\n--------------- Summarized Text: --------------------\n{summarized_text}\n"
            )

            data = extract_and_validate_json_objects(summarized_text)

            if len(data) == 0:
                print("No JSON object found in the response.")
                print(summarized_text)
                raise Exception("No JSON object found in the response.")

            data = concat_json_objects_by_keys(data)

            if not data:
                print(f"\n\nFailed to extract summarized text on chunk {i+1}\n\n")
                print(summarized_text)
                continue

            print(f"\nIntermediate Summary {i+1}: {data}\n")

            summarized_json.append(data)

        except Exception as e:
            print(f"Failed to summarize chunk {i+1}")
            print(e)
            continue  # Proceed to the next chunk if an error occurs

    print(summarized_json)

    # Finalize the summarized texts
    print(f"Finalize the summarized texts...")

    summary = finalise_summarized_text(summarized_json, title)

    print(f"Summarization done! Returning summary: \n\n{summary}")

    return summary


def initiate(text: str, title: str) -> dict:
    """
    Initiate the summarization process.

    Args:
        text (str): The input text to summarize.
        title (str): The title of the input text.

    Returns:
        dict: The summarized text.
    """
    result = summarize_text(text, title)

    if not result:
        return {"error": "Failed to summarize the text."}

    return result


__all__ = ["initiate"]
