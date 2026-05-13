import re
from log import logger
from config import Niche
from ai_client import generate_text

MAX_RETRIES = 2
MIN_CONTENT_LENGTH = 500

SYSTEM_PROMPT_EN = """You are an expert ebook writer. Write concise, practical, and actionable short ebooks.
Use clear conversational tone. Focus on value per paragraph."""

SYSTEM_PROMPT_PT = """Você é um escritor expert de ebooks. Escreva ebooks curtos, práticos e acionáveis.
Use tom claro e conversacional. Foco em valor por parágrafo."""

CONTENT_PROMPT_EN = """Write a short ebook in English with EXACTLY this structure.
TITLE: {title}
SUBTITLE: {subtitle}
TOPIC: {content_brief}

FORMAT REQUIREMENTS (strict):
- Start with: ## Introduction
- Then 5 sections using: ## Section Title
- End with: ## Conclusion
- Then: ## Next Steps with 5 bullet points
- Use **bold** for key terms
- Use bullet lists (- ) for tips and action items
- Total: ~2000-2500 words
- Conversational practical tone
- No commentary outside the markdown"""

CONTENT_PROMPT_PT = """Escreva um ebook curto em Português com EXATAMENTE esta estrutura.
TÍTULO: {title}
SUBTÍTULO: {subtitle}
TÓPICO: {content_brief}

REQUISITOS DE FORMATO (rigoroso):
- Comece com: ## Introdução
- Então 5 seções usando: ## Título da Seção
- Termine com: ## Conclusão
- Então: ## Próximos Passos com 5 itens
- Use **negrito** para termos chave
- Use listas (- ) para dicas e ações
- Total: ~2000-2500 palavras
- Tom conversacional prático
- Sem comentários fora do markdown"""

def validate_content(content: str, lang: str) -> list[str]:
    errors = []
    if len(content) < MIN_CONTENT_LENGTH:
        errors.append(f"Too short ({len(content)} chars, min {MIN_CONTENT_LENGTH})")

    if lang == "en":
        if not re.search(r"^## Introduction", content, re.MULTILINE):
            errors.append("Missing ## Introduction")
        if not re.search(r"^## Conclusion", content, re.MULTILINE):
            errors.append("Missing ## Conclusion")
        if not re.search(r"^## Next Steps", content, re.MULTILINE):
            errors.append("Missing ## Next Steps")
    else:
        if not re.search(r"^## Introdução", content, re.MULTILINE):
            errors.append("Missing ## Introdução")
        if not re.search(r"^## Conclusão", content, re.MULTILINE):
            errors.append("Missing ## Conclusão")
        if not re.search(r"^## Próximos Passos", content, re.MULTILINE):
            errors.append("Missing ## Próximos Passos")

    sections = re.findall(r"^## ", content, re.MULTILINE)
    if len(sections) < 7:
        errors.append(f"Too few sections ({len(sections)}, need >= 7)")

    return errors


def generate_content(niche: Niche) -> str:
    if niche.lang == "en":
        prompt = CONTENT_PROMPT_EN.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_EN
    else:
        prompt = CONTENT_PROMPT_PT.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_PT

    last_errors = []
    for attempt in range(1, MAX_RETRIES + 1):
        content = generate_text(prompt, system_prompt=system)
        errors = validate_content(content, niche.lang)
        if not errors:
            return content
        last_errors = errors
        logger.warning(f"[{niche.id}] Validation failed (attempt {attempt}): {'; '.join(errors)}")

    raise ValueError(f"Content validation failed after {MAX_RETRIES} attempts: {'; '.join(last_errors)}")
