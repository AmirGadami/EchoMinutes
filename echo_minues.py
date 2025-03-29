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


