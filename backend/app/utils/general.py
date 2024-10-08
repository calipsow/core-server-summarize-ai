import nltk, json
from bs4 import BeautifulSoup


def extract_and_validate_json_objects(input_string: str) -> list[dict]:
    try:
        if not isinstance(input_string, str):
            print("Input string is not a string.", input_string)
            raise Exception("Input string is not a string.")
        valid_json_objects = []
        idx = 0
        length = len(input_string)

        while idx < length:
            if input_string[idx] == "{":
                brace_count = 1
                end_idx = idx + 1
                while end_idx < length and brace_count > 0:
                    if input_string[end_idx] == "{":
                        brace_count += 1
                    elif input_string[end_idx] == "}":
                        brace_count -= 1
                    end_idx += 1
                obj_str = input_string[idx:end_idx]
                try:
                    json_obj = json.loads(obj_str)
                    valid_json_objects.append(json_obj)
                except json.JSONDecodeError:
                    pass

                idx = end_idx
            else:
                idx += 1

        return valid_json_objects

    except Exception as e:
        print("Couldnt resolve json objects, due to crappy code from GPT!!!")
        print("Failed on string:", input_string, e)
        raise Exception("Couldnt resolve json objects, due to crappy code from GPT!!!")


def split_text_into_chunks(text, max_input_tokens, tokenizer=None):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    current_tokens = 0
    addtnl_string = ""
    addtnl_string_tokens = len(tokenizer.encode(addtnl_string))
    max_input_tokens -= addtnl_string_tokens

    for sentence in sentences:
        sentence_tokens = len(tokenizer.encode(sentence))
        if current_tokens + sentence_tokens <= max_input_tokens:
            current_chunk += " " + sentence
            current_tokens += sentence_tokens
        else:
            chunks.append(f"""{current_chunk.strip()}""")
            current_chunk = sentence
            current_tokens = sentence_tokens

    if current_chunk:
        chunks.append(f"""{current_chunk.strip()}""")

    return chunks


def remove_html_xml_tags(input_string: str) -> str:
    if not isinstance(input_string, str):
        print('Got Non String passed to remove_html_xml_tags, rtrn ""')
        return ""

    # Parse the input string using BeautifulSoup
    soup = BeautifulSoup(input_string, "html.parser")
    # Extract text from the parsed HTML/XML, which removes the tags
    cleaned_string = soup.get_text()
    return cleaned_string


def concat_json_objects_by_keys(json_objects: list[dict]) -> dict | None:
    """
    Concatenate JSON objects by keys to one dict.

    Args:
        json_objects (list[dict]): The list of JSON objects to filter.

    Returns:
        list[dict]: The filtered list of JSON objects.
    """
    if len(json_objects) == 0:
        return {}

    if len(json_objects) == 1:
        return json_objects[0]

    concated_json = {}
    try:

        for json_obj in json_objects:

            for key, value in json_obj.items():

                if value == "":
                    continue

                elif key in concated_json:
                    concated_json[key] += f" {str(value)}"

                else:
                    concated_json[key] = str(value)

        return concated_json

    except Exception as e:
        print("Failed to concat json objects", e)
        print(json_objects)
        return None
