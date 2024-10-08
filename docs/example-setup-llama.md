# Basic Example of Llama 3.2 8B

## Install Dependencies

```bash
%%capture
%pip install -U bitsandbytes
%pip install transformers==4.44.2
%pip install -U accelerate
%pip install -U peft
%pip install -U trl
```

## Init Huggingface

```python
from huggingface_hub import login
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()

hf_token = user_secrets.get_secret("HUGGINGFACE_TOKEN")
login(token = hf_token)
```

## Setup Base Model

```python
base_model_url = "/kaggle/input/llama-3.2/transformers/3b-instruct/1"
new_model_url = "/kaggle/input/fine-tune-llama-3-2-on-customer-support/llama-3.2-3b-it-Ecommerce-ChatBot/"


from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from peft import PeftModel
import torch
from trl import setup_chat_format


# Reload tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(base_model_url)

base_model_reload= AutoModelForCausalLM.from_pretrained(
    base_model_url,
    low_cpu_mem_usage=True,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map="auto",
)

# Merge adapter with base model
base_model_reload, tokenizer = setup_chat_format(base_model_reload, tokenizer)
model = PeftModel.from_pretrained(base_model_reload, new_model_url)

model = model.merge_and_unload()

instruction = """You are a top-rated customer service agent named John.
    Be polite to customers and answer all their questions.
    """

messages = [
    {"role": "system", "content": instruction},
    {"role": "user", "content": "I have to see what payment payment modalities are accepted"}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

inputs = tokenizer(
    prompt,
    return_tensors='pt',
    padding=True,
    truncation=True
).to("cuda")

outputs = model.generate(
    **inputs,
    max_new_tokens=150,
    num_return_sequences=1
)

text = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print(text.split("assistant")[1])
```
