import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

import nltk, torch
from transformers import AutoTokenizer, pipeline, PretrainedConfig
from app.core.config import settings

nltk.download("punkt")
nltk.download("punkt_tab")

# nltk.download('punkt')
# nltk.download('punkt_tab')

tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL_ID, token=settings.HF_TKN)
config = PretrainedConfig.from_pretrained(settings.LLM_MODEL_ID, token=settings.HF_TKN)

config_dict = config.to_dict()

config_dict["top_p"] = 0.8
config_dict["top_k"] = 20
config_dict["temperature"] = 0.7

# experiment with different values for the repetition_penalty.
config_dict["repetition_penalty"] = 1.2
# repetition_penalty: contrls how much the model will avoid repeating the same token in the output
# (expoentialy scales the prob of tkn if its already in the output)
config_dict["typical_p"] = 0.8
# typical_p: controlls how prob the next token can be (bsed on tkn ctx),
# if its to random it'll denies the tkn


config.from_dict(config_dict)

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

print("\n----- Model Configs ------\n")

for key, value in config_dict.items():
    if key in relevant_keys:
        if key in special_keys:
            if isinstance(value, int):
                # Konvertiere einzelne Token-IDs in Strings
                display_value = tokenizer.decode([value])
            elif isinstance(value, list):
                # Konvertiere Listen von Token-IDs in Strings
                display_value = tokenizer.decode(value)
            else:
                # Falls der Wert weder int noch Liste ist, gebe ihn direkt aus
                display_value = value
        else:
            display_value = value
        print(f"{key.upper()}: {display_value}")

print("\n----- Model Configs End ------\n")

# Initialize the text-generation pipeline
pipe = pipeline(
    "text-generation",
    tokenizer=tokenizer,
    model=settings.LLM_MODEL_ID,
    framework="pt",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    token=settings.HF_TKN,
    config=config,
)

__all__ = ["pipe", "tokenizer", "config"]
