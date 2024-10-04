from app.services.llms import pipe, tokenizer
from app.utils.general import (
    extract_and_validate_json_objects,
    split_text_into_chunks,
)


def finalise_summarized_text(
    summarized_json: list[dict], title: str, return_json: bool = False
) -> dict | str | None:
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

    json_structure = '{"title": "","summary": ""}'

    finalise_summarized_text_instructions = f"""The text provided json object is an amalgamation of individual summaries of text sections that were part of a single long text with the title: "{title}". Combine all summaries from the provided json objects of the individual text sections into a final text summary that summarizes the original text as a whole as one single text. Always answer in the language of the text title. Answer only with the final summary, nothing else. Keep the summary as short as possible without removing important content. Return the final summary in a json object with the following schema: {json_structure}"""

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
        answer_chunks = split_text_into_chunks(joined_text, max_input_tokens)

        # Recursively resolve the final answer with the new chunks
        new_summaries = []
        for i, chunk in enumerate(answer_chunks):
            print(f"\n--- Summarizing Chunk {i+1} ---\n")
            try:
                streamed = pipe(
                    f"{finalise_summarized_text_instructions}\n{chunk}",
                    max_tokens=max_generated_tokens,
                )
                data = extract_and_validate_json_objects(streamed)

                if len(data) == 0:
                    print("No JSON object found in the response.")
                    continue

                data = data[0]

                text = ""

                for key, value in data.items():
                    if value != "":
                        text += f"{key}: {value}\n"

                print(f"\nIntermediate Summary {i+1}: {text}\n")

                new_summaries.append(data)

            except Exception as e:
                print(f"Failed to process chunk {i+1}")
                print(e)
                continue  # Proceed to the next chunk if an error occurs

        # Recursive call with the new summarized answers
        return (
            finalise_summarized_text(new_summaries, title, return_json=True)
            if return_json
            else finalise_summarized_text(new_summaries, title)
        )
    else:
        try:
            final_answer = pipe(
                f"{finalise_summarized_text_instructions}\n{joined_text}",
                max_tokens=max_generated_tokens,
            )
            data = extract_and_validate_json_objects(final_answer)
            final_answer_txt = ""

            if len(data) == 0:
                print("No JSON object found in the response.")
                raise Exception("No JSON object found in the response.")

            data = data[0]

            for key, value in data.items():
                if value != "":
                    final_answer_txt += f"{key}: {value}\n"

            print(f"\nFinal Summary: {final_answer_txt}\n")

            return final_answer_txt if not return_json else data

        except Exception as e:
            print("Failed to generate the final answer")
            print(e)
            return None


def summarize_text(text: str, title: str) -> str:
    """
    Summarize the input text using the model.

    Args:
        text (str): The input text to summarize.

    Returns:
        str: The summarized text.
    """
    json_structure = '{"title": "","summary": ""}'

    system_instructions = f"""Summarize the given text briefly and precisely with a short description. For the resulting summary, formulate a short title with a maximum of 5 words that describes your text summary. The text sections are parts of a larger text from a website, article or other source. The source of the original text has the following title: "{title}". Always answer in the language of the text. Only return the summary and the title of the summary in a json object which has this shema: {json_structure}, nothing else. Keep the summary as short as possible without removing important content."""

    system_instructions_tokens = len(tokenizer.encode(system_instructions))

    # Define the maximum context size and maximum generated tokens
    max_context_size = 2048
    max_generated_tokens = 300  # Adjust as needed

    # Calculate the maximum number of tokens for the input
    max_input_tokens = (
        max_context_size - system_instructions_tokens - max_generated_tokens
    )

    if max_input_tokens <= 0:
        print(
            "The system instructions and the maximum generated tokens exceed the context window size."
        )
        return None

    # Split the text into sections
    text_chunks = split_text_into_chunks(text, max_input_tokens)
    print(f"Text split into {len(text_chunks)} sections.")

    summarized_texts = []
    summarized_json = []
    for i, chunk in enumerate(text_chunks):
        print(f"\n--- Summarizing Chunk {i+1} ---\n", end="\n", flush=True)
        try:
            prompt = f"Prompt:{system_instructions}\nText: {chunk}"

            summarized_text = pipe(prompt, max_tokens=max_generated_tokens)

            print(f"\nSummarized Text {i+1}: {summarized_text}\n")

            data = extract_and_validate_json_objects(summarized_text)

            if len(data) == 0:
                print("No JSON object found in the response.")
                raise Exception("No JSON object found in the response.")

            data = data[0]

            summarized_json.append(data)

        except Exception as e:
            print(f"Failed to summarize chunk {i+1}")
            print(e)
            continue  # Proceed to the next chunk if an error occurs

    print(summarized_json)

    # Finalize the summarized texts
    summary = finalise_summarized_text(summarized_json, title, return_json=True)

    return (
        summary
        if isinstance(summary, dict)
        else {"Error": "Failed to generate the final summary."}
    )
