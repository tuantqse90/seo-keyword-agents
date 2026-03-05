from collections.abc import AsyncGenerator

from app.config import settings
from app.services.prompt_builder import load_system_prompt


async def stream_claude_response(user_message: str) -> AsyncGenerator[str, None]:
    """Stream LLM response, yielding text chunks. Supports Anthropic and DeepSeek."""
    system_prompt = load_system_prompt()

    if settings.llm_provider == "deepseek":
        async for chunk in _stream_deepseek(system_prompt, user_message):
            yield chunk
    else:
        async for chunk in _stream_anthropic(system_prompt, user_message):
            yield chunk


async def get_claude_response(user_message: str) -> str:
    """Get full LLM response (non-streaming)."""
    system_prompt = load_system_prompt()

    if settings.llm_provider == "deepseek":
        return await _get_deepseek(system_prompt, user_message)
    else:
        return await _get_anthropic(system_prompt, user_message)


# ── Anthropic ──

async def _stream_anthropic(system_prompt: str, user_message: str) -> AsyncGenerator[str, None]:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    async with client.messages.stream(
        model=settings.claude_model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def _get_anthropic(system_prompt: str, user_message: str) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    message = await client.messages.create(
        model=settings.claude_model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


# ── DeepSeek (OpenAI-compatible) ──

async def _stream_deepseek(system_prompt: str, user_message: str) -> AsyncGenerator[str, None]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    stream = await client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=8192,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


async def _get_deepseek(system_prompt: str, user_message: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    response = await client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=8192,
    )
    return response.choices[0].message.content
