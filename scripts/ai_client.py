import requests
import config

def generate_text(prompt: str, system_prompt: str | None = None, max_tokens: int | None = None) -> str:
    api_key = config.get_api_key()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        f"{config.OPENROUTER_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.OPENROUTER_TEXT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens or config.MAX_TOKENS,
            "temperature": config.TEMP,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
