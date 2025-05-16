import asyncio
from abc import ABC, abstractmethod

import yaml
from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

_KEY_FILE_LOCATION = "../keys.secret"
_KEY_CONFIG = yaml.safe_load(open(_KEY_FILE_LOCATION, "r"))


class PromptInput(BaseModel, ABC):
    @abstractmethod
    def to_prompt(self) -> str:
        "Format members to a prompt for the LLM to consume"
        pass


def initialize_model(
    model_name: str = "qwen/qwen3-4b:free", use_free_key: bool = True
) -> OpenAIModel:
    api_key = (
        _KEY_CONFIG["openrouter"]["free_key"]
        if use_free_key
        else _KEY_CONFIG["openrouter"]["api_key"]
    )

    return OpenAIModel(
        model_name=model_name,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
    )


async def print_buffer(buffer, delay):
    for char in buffer:
        print(char, end="", flush=True)
        await asyncio.sleep(delay)
    print()  # Final newline after buffer


async def stream_print_queue(queue, queue_end_signal, delay=0.05):
    buffer = ""  # Accumulate characters between newlines

    while True:
        chunk = await queue.get()
        queue.task_done()

        if chunk == queue_end_signal:
            if buffer:
                # Print remaining buffer
                await print_buffer(buffer, delay)
            break

        for char in chunk:
            if char == "\n":
                # Flush buffer and print newline
                await print_buffer(buffer, delay)
                buffer = ""  # Reset after newline
            else:
                buffer += char
