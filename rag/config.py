# If you ever switch providers or models, you only change this file

from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"
EMBEDDING_MODEL = "openai/text-embedding-3-small"
CHAT_MODEL = "openai/gpt-4o-mini"


def get_client(api_key: str) -> OpenAI:
    """Build an OpenAI-SDK client pointed at OpenRouter.

    Taking the key as a parameter (instead of reading it here) lets the app
    later pass in either the default key or the user's own key.
    """
    return OpenAI(base_url=BASE_URL, api_key=api_key)