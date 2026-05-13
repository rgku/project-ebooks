import re
from log import logger
from config import Niche
from ai_client import generate_text

MAX_RETRIES = 3
MIN_CONTENT_LENGTH = 9000

SYSTEM_PROMPT_EN = """You are a bestselling ebook ghostwriter. Write exceptionally comprehensive, thorough, and value-packed ebooks. Each ebook must feel like a complete course — rich with frameworks, case studies, worksheets, troubleshooting guides, and advanced strategies. The reader must feel they got 10x the value of what they paid. Every claim needs evidence, every technique needs a step-by-step walkthrough, and every concept needs a real-world example."""

SYSTEM_PROMPT_PT = """Você é um ghostwriter de ebooks best-seller. Escreva ebooks excepcionalmente completos, aprofundados e repletos de valor. Cada ebook deve parecer um curso completo — rico em frameworks, estudos de caso, guias de exercícios, solução de problemas e estratégias avançadas. O leitor precisa sentir que recebeu 10x o valor do que pagou. Toda afirmação precisa de evidência, toda técnica precisa de um passo a passo, e todo conceito precisa de um exemplo real."""

CONTENT_PROMPT_EN = """Write a comprehensive ebook in English with EXACTLY this structure.
TITLE: {title}
SUBTITLE: {subtitle}
TOPIC: {content_brief}

CRITICAL: This ebook MUST be at least 5000 words. 7000-10000 words is ideal.
You need 12-16 main content sections to reach this length.
Each section must have 5-10 detailed paragraphs with deep practical content.

STRUCTURE (strict):
- Start with: ## Introduction (5+ paragraphs — hook, who this is for, what they'll gain)
- Then 12-16 sections using: ## Section Title (each 6+ paragraphs)
  For each section include: core concept, step-by-step guidance, practical example, common mistakes, pro tips
- End with: ## Conclusion (4+ paragraphs — summarize, reinforce key message, call to action)
- Then: ## Next Steps with 8-12 detailed actionable bullet points
- Then: ## Further Reading with 4-6 resource recommendations

REQUIRED ELEMENTS throughout:
- Use **bold** for key terms and frameworks
- Use bullet lists (- ) for tips, steps, and action items
- Include at least 4 real-world examples or case studies
- Include a troubleshooting/pro tips section addressing reader objections
- Include practical exercises or reflection prompts
- Conversational but authoritative tone, like a trusted coach
- No commentary outside the markdown"""

CONTENT_PROMPT_PT = """Escreva um ebook completo em Português com EXATAMENTE esta estrutura.
TÍTULO: {title}
SUBTÍTULO: {subtitle}
TÓPICO: {content_brief}

CRÍTICO: Este ebook deve ter PELO MENOS 5000 palavras. 7000-10000 palavras é o ideal.
Você precisa de 12-16 seções principais de conteúdo para atingir este comprimento.
Cada seção deve ter 5-10 parágrafos detalhados com conteúdo prático profundo.

ESTRUTURA (rigoroso):
- Comece com: ## Introdução (5+ parágrafos — gancho, para quem é, o que vão aprender)
- Então 12-16 seções usando: ## Título da Seção (cada 6+ parágrafos)
  Para cada seção inclua: conceito central, passo a passo, exemplo prático, erros comuns, dicas de expert
- Termine com: ## Conclusão (4+ parágrafos — resumo, reforço da mensagem, chamada para ação)
- Então: ## Próximos Passos com 8-12 itens detalhados e acionáveis
- Então: ## Leitura Complementar com 4-6 recomendações de recursos

ELEMENTOS OBRIGATÓRIOS em todo o texto:
- Use **negrito** para termos chave e frameworks
- Use listas (- ) para dicas, passos e ações
- Inclua pelo menos 4 exemplos reais ou estudos de caso
- Inclua uma seção de dicas de especialista/solução de problemas
- Inclua exercícios práticos ou prompts de reflexão
- Tom conversacional mas autoritativo, como um coach de confiança
- Sem comentários fora do markdown"""

def _find_section(content: str, keywords: list[str]) -> bool:
    for h2 in re.findall(r"^## (.+)$", content, re.MULTILINE):
        h2_lower = h2.lower().strip()
        for kw in keywords:
            if kw.lower() in h2_lower:
                return True
    return False


def validate_content(content: str, lang: str) -> list[str]:
    errors = []
    if len(content) < MIN_CONTENT_LENGTH:
        errors.append(f"Too short ({len(content)} chars, min {MIN_CONTENT_LENGTH})")

    if lang == "en":
        if not _find_section(content, ["Introduction", "Intro"]):
            errors.append("Missing Introduction section")
        if not _find_section(content, ["Conclusion", "Conclude", "Summary"]):
            errors.append("Missing Conclusion section")
        if not _find_section(content, ["Next Steps", "Next", "What's Next"]):
            errors.append("Missing Next Steps section")
    else:
        if not _find_section(content, ["Introdução", "Introducao", "Intro"]):
            errors.append("Missing Introdução section")
        if not _find_section(content, ["Conclusão", "Conclusao", "Concluir"]):
            errors.append("Missing Conclusão section")
        if not _find_section(content, ["Próximos Passos", "Proximos Passos", "Próximo", "Proximo"]):
            errors.append("Missing Próximos Passos section")

    sections = re.findall(r"^## ", content, re.MULTILINE)
    if len(sections) < 6:
        errors.append(f"Too few sections ({len(sections)}, need >= 6)")

    return errors


def generate_content(niche: Niche) -> str:
    if niche.lang == "en":
        prompt = CONTENT_PROMPT_EN.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_EN
    else:
        prompt = CONTENT_PROMPT_PT.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_PT

    last_content = None
    last_errors = []
    for attempt in range(1, MAX_RETRIES + 1):
        content = generate_text(prompt, system_prompt=system)
        errors = validate_content(content, niche.lang)
        if not errors:
            return content
        last_content = content
        last_errors = errors
        logger.warning(f"[{niche.id}] Validation failed (attempt {attempt}): {'; '.join(errors)}")

    if last_content and len(last_content) >= MIN_CONTENT_LENGTH * 0.5:
        logger.warning(f"[{niche.id}] Accepting content with minor issues: {'; '.join(last_errors)}")
        return last_content

    raise ValueError(f"Content validation failed after {MAX_RETRIES} attempts: {'; '.join(last_errors)}")
