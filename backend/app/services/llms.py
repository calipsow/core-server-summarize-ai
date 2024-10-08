import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

import nltk, torch
from trl import setup_chat_format
from transformers import (
    AutoTokenizer,
    pipeline,
    PretrainedConfig,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    PretrainedConfig,
    Pipeline,
    AutoModelForCausalLM,
    PreTrainedModel,
)
from app.core.config import settings


# nltk.download("punkt")
# nltk.download("punkt_tab")

# nltk.download('punkt')
# nltk.download('punkt_tab')

# tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL_ID, token=settings.HF_TKN)
# config = PretrainedConfig.from_pretrained(settings.LLM_MODEL_ID, token=settings.HF_TKN)

# config_dict = config.to_dict()

# config_dict["top_p"] = 0.8
# config_dict["top_k"] = 20
# config_dict["temperature"] = 0.7

# experiment with different values for the repetition_penalty.
# config_dict["repetition_penalty"] = 1.2
# repetition_penalty: contrls how much the model will avoid repeating the same token in the output
# (expoentialy scales the prob of tkn if its already in the output)
# config_dict["typical_p"] = 0.8
# typical_p: controlls how prob the next token can be (bsed on tkn ctx),
# if its to random it'll denies the tkn


# config.from_dict(config_dict)

relevant_keys = [
    "top_p",
    "top_k",
    "temperature",
    "repetition_penalty",
    "typical_p",
    "bos_token_id",
    "eos_token_id",
    "sep_token_id",
    "num_beams",
]

special_keys = ["bos_token_id", "eos_token_id", "sep_token_id"]

# print("\n----- Model Configs ------\n")

# for key, value in config_dict.items():
# if key in relevant_keys:
# if key in special_keys:
# if isinstance(value, int):
# Konvertiere einzelne Token-IDs in Strings
# display_value = tokenizer.decode([value])
# elif isinstance(value, list):
# Konvertiere Listen von Token-IDs in Strings
# display_value = tokenizer.decode(value)
# else:
# Falls der Wert weder int noch Liste ist, gebe ihn direkt aus
# display_value = value
# else:
# display_value = value
# print(f"{key.upper()}: {display_value}")

# print("\n----- Model Configs End ------\n")

# Initialize the text-generation pipeline
# pipe = pipeline(
#    "text-generation",
#    tokenizer=tokenizer,
#    model=settings.LLM_MODEL_ID,
#    framework="pt",
#    torch_dtype=torch.bfloat16,
#    device_map="auto",
#    token=settings.HF_TKN,
#    config=config,
# )

# __all__ = ["pipe", "tokenizer", "config"]


############## TYPES ##############
from dataclasses import dataclass
from typing import Literal


# from dataclasses import asdict
@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str

    def __post_init__(self):
        if not isinstance(self.role, str) or self.role not in (
            "system",
            "user",
            "assistant",
        ):
            print(f"Invalid role: {str(self.role)} for chat message")
            raise ValueError(f"Invalid role: {self.role}")

        if not isinstance(self.content, str):
            print(f"Invalid content type: {type(self.content)} for chat message")
            raise TypeError(f"Invalid content type: {type(self.content)}")


############## TYPES END ##############


class LLamaModel:
    def __init__(self):
        self.pipe: Pipeline | None = None
        self.tokenizer: (PreTrainedTokenizer | PreTrainedTokenizerFast) | None = None
        self.config: PretrainedConfig | None = None
        self.occurred_errors = []
        self.last_error = None
        self.current_pipe_setting = "text-generation"
        self.__initiate()

    def __handle_errors(self, e: Exception, step: str, custom_message: str = None):
        print(f"An error occurred in step {step}: {e}")
        self.occurred_errors.append(
            {"error": e, "step": step, "custom_message": custom_message}
        )
        self.last_error = e
        return "An error occurred."

    def __initiate(self):
        if self.pipe and self.tokenizer and self.config:
            return print("Model already initiated.")

        print("Loading nltk...")
        nltk.download("punkt")
        nltk.download("punkt_tab")
        print("Nltk loaded.")

        exception = self.__load_tokenizer()
        if exception:
            raise Exception(self.last_error)
        exception = self.__load_config()
        if exception:
            raise Exception(self.last_error)
        exception = self.__load_pipe()
        if exception:
            raise Exception(self.last_error)

        print("Model initiated.")

        self.current_pipe_setting = "text-generation"

    def __load_tokenizer(self):
        print("Loading tokenizer...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL_ID, token=settings.HF_TKN
            )
            return print("Tokenizer loaded.")
        except Exception as e:
            return self.__handle_errors(
                e, "loading_tokenizer", "Failed to load tokenizer."
            )

    def __load_config(self):
        print(f"Init configs for model {settings.LLM_MODEL_ID}...")
        try:
            config = PretrainedConfig.from_pretrained(
                settings.LLM_MODEL_ID, token=settings.HF_TKN
            )
            config_dict = config.to_dict()
            config_dict["top_p"] = 0.8
            config_dict["top_k"] = 20
            config_dict["temperature"] = 0.7
            config_dict["repetition_penalty"] = 1.2
            config_dict["typical_p"] = 0.8
            config.from_dict(config_dict)

            self.__print_configs(config_dict)

            self.config = config
            return print("Config loaded.")
        except Exception as e:
            return self.__handle_errors(e, "loading_config", "Failed to load config.")

    def __load_pipe(self, task: str = "text-generation"):

        if not self.tokenizer:
            if self.__load_tokenizer() == "An error occurred.":
                return self.__handle_errors(
                    self.last_error,
                    "loading_pipe",
                    "Failed to load pipeline, because cant load tokenizer...",
                )

        if not self.config:
            if self.__load_config() == "An error occurred.":
                return self.__handle_errors(
                    self.last_error,
                    "loading_pipe",
                    "Failed to load pipeline, because cant load config...",
                )

        print("Loading pipeline...")
        try:
            self.pipe = pipeline(
                task,
                tokenizer=self.tokenizer,
                model=settings.LLM_MODEL_ID,
                framework="pt",
                torch_dtype=torch.bfloat16,
                device_map="auto",
                token=settings.HF_TKN,
                config=self.config,
            )
            return print("Pipeline loaded.")
        except Exception as e:
            return self.__handle_errors(e, "loading_pipe", "Failed to load pipeline.")

    def __initiate_custom_pipe_without_configs(self, task: str):
        raise Exception("Not implemented yet.")
        if not self.tokenizer:
            if self.__load_tokenizer() == "An error occurred.":
                return self.__handle_errors(
                    self.last_error,
                    "loading_pipe",
                    "Failed to load pipeline, because cant load tokenizer...",
                )

        if not self.config:
            if self.__load_config() == "An error occurred.":
                return self.__handle_errors(
                    self.last_error,
                    "loading_pipe",
                    "Failed to load pipeline, because cant load config...",
                )

        print("Loading pipeline...")
        try:
            pipe = pipeline(
                task,
                model=settings.LLM_MODEL_ID,
                torch_dtype=torch.bfloat16,
                token=settings.HF_TKN,
            )
            print("Pipeline loaded.")
            return pipe
        except Exception as e:
            return self.__handle_errors(
                e, "initiate_custom_pipe_without_configs", "Failed to load pipeline."
            )

    def __print_configs(
        self,
        config_dict: dict,
        relevant_keys: list[str] = relevant_keys,
        special_keys: list[str] = special_keys,
    ):
        print("\n----- Model Configs ------\n")
        for key, value in config_dict.items():
            if key in relevant_keys:
                if key in special_keys:
                    if isinstance(value, int):
                        display_value = self.tokenizer.decode([value])
                    elif isinstance(value, list):
                        display_value = self.tokenizer.decode(value)
                    else:
                        display_value = value
                else:
                    display_value = value
                print(f"{key.upper()}: {display_value}")
        print("\n----- Model Configs End ------\n")

    def __initiate_custom_configs(self, config_dict: dict):
        config = PretrainedConfig.from_dict(config_dict)
        configs = config.to_dict()

        configs["top_p"] = config_dict.get("top_p", 0.8)
        configs["top_k"] = config_dict.get("top_k", 20)
        configs["temperature"] = config_dict.get("temperature", 0.7)
        configs["repetition_penalty"] = config_dict.get("repetition_penalty", 1.2)
        configs["typical_p"] = config_dict.get("typical_p", 0.8)

        config.from_dict(configs)

        self.__print_configs(configs)

        self.config = config

    def get_pipe(self):
        if not self.pipe:
            self.__initiate()

        return self.pipe

    def get_tokenizer(self):
        if not self.tokenizer:
            self.__initiate()

        return self.tokenizer

    def get_config(self):
        if not self.config:
            self.__initiate()

        return self.config

    def generate_chat_based_assistant(
        self, instruction: str
    ) -> tuple[PreTrainedModel, PreTrainedTokenizer, list[dict[str, str]]] | str:
        """
        Example:
        instruction = 'You are a top-rated customer service agent named John.
                Be polite to customers and answer all their questions.'

        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": "I have to see what payment payment modalities are accepted"}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer(prompt, return_tensors='pt', padding=True, truncation=True).to("cuda")

        outputs = model.generate(**inputs, max_new_tokens=150, num_return_sequences=1)

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(text.split("assistant")[1])

        """
        try:
            print("Generating chat-based assistant...")

            print("Loading model...")
            tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL_ID, token=settings.HF_TKN
            )

            print("Setting device...")
            device_index = torch.cuda.current_device()
            torch.cuda.set_device(device_index)

            print("initiating model...")
            model = AutoModelForCausalLM.from_pretrained(
                settings.LLM_MODEL_ID,
                low_cpu_mem_usage=True,
                return_dict=True,
                torch_dtype=torch.float16,
                device_map="auto",
            )

            print("applying chat format configurations...")
            model, tokenizer = setup_chat_format(model, tokenizer)

            print("prepare template messages using the provided system instructions...")
            # template messages
            messages = [
                {"role": "system", "content": instruction},
            ]

            print("done!")
            return (
                model,
                tokenizer,
                messages,
            )

        except Exception as e:
            return self.__handle_errors(
                e,
                "generate_chat_based_assistant",
                "Failed to generate chat-based assistant.",
            )


class LLMUtils:

    def __check_messages(self, messages: list[dict[str, str]]):
        try:
            [Message(**message) for message in messages if isinstance(message, dict)]
        except ValueError:
            print("Invalid messages")
            return "Invalid messages"
        except TypeError:
            print("Invalid messages")
            return "Invalid messages"
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred."

        return None

    def generate_output_from_model(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        messages: list[dict[str, str]],
        max_new_tokens: int = 150,
    ):
        print("validate messages...")

        if self.__check_messages(messages):
            raise Exception("Invalid messages")

        print("Generating output from model...")

        print("applying chat template...")

        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        print("tokenizing prompt...")
        inputs = tokenizer(
            prompt, return_tensors="pt", padding=True, truncation=True
        ).to("cuda")
        
        
        print("generating outputs...")
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens, num_return_sequences=1
        )

        print("decoding outputs...")
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print("done!")
        return text.split("assistant")[1]

    def generate_output_from_pipe(
        self,
        pipe: Pipeline,
        tokenizer: PreTrainedTokenizer,
        complete_prompt: str,
        max_new_tokens: int = 150,
    ):
        print("Generating output from pipe...")

        streamed = pipe(
            complete_prompt,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )[-1]["generated_text"]

        print("done!")
        return streamed


llama = LLamaModel()
utils = LLMUtils()

__all__ = ["llama", "utils"]
