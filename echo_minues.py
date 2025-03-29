import os
import torch
from openai import OpenAI
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextStreamer,
    BitsAndBytesConfig
)

from config import AUDIO_MODEL,LLM_MODEL,AUDIO_NAME

OPENAI_API_TOKEN = os.getenv('OPENAI_API_KEY')

def transcrib_audio(audio_path):
    openai = OpenAI()
    with open(audio_path,'rb') as audio_file:
        transcription = openai.audio.transcriptions.create(
            model = AUDIO_MODEL,
            file = AUDIO_NAME,
            response_format = 'text',
        )
    return transcription

def generate_minutes(transcription_text):
    system_message = (
        "You are an assistant that produces minutes of meetings from transcripts, "
        "with summary, key discussion points, takeaways and action items with owners, in markdown."
    )

    user_prompt = (
        f"Below is an extract transcript of a Denver council meeting. Please write minutes in markdown, "
        f"including a summary with attendees, location and date; discussion points; takeaways; and action items with owners.\n\n"
        f"{transcription_text}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4"
    )

    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")
    streamer = TextStreamer(tokenizer)

    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL,
        device_map="auto",
        quantization_config=quant_config
    )

    outputs = model.generate(inputs, max_new_tokens=2000, streamer=streamer)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
