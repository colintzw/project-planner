import yaml
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

_KEY_FILE_LOCATION = "../keys.secret"
_KEY_CONFIG = yaml.safe_load(open(_KEY_FILE_LOCATION, "r"))


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
