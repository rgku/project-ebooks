import re
import random
from log import logger
from config import Niche
from ai_client import generate_text

MAX_RETRIES = 3
MIN_CONTENT_LENGTH = 20000

SYSTEM_PROMPT_EN = """You are a bestselling ebook ghostwriter. Write exceptionally comprehensive, thorough, and value-packed ebooks. Each ebook must feel like a complete course — rich with frameworks, case studies, worksheets, troubleshooting guides, and advanced strategies. The reader must feel they got 10x the value of what they paid. Every claim needs evidence, every technique needs a step-by-step walkthrough, and every concept needs a real-world example.

YOUR VOICE: {voice}

This is your author persona. Write consistently in this voice throughout the entire ebook."""

SYSTEM_PROMPT_PT = """Você é um ghostwriter de ebooks best-seller. Escreva ebooks excepcionalmente completos, aprofundados e repletos de valor. Cada ebook deve parecer um curso completo — rico em frameworks, estudos de caso, guias de exercícios, solução de problemas e estratégias avançadas. O leitor precisa sentir que recebeu 10x o valor do que pagou. Toda afirmação precisa de evidência, toda técnica precisa de um passo a passo, e todo conceito precisa de um exemplo real.

SUA VOZ: {voice}

Esta é sua persona de autor. Escreva consistentemente nesta voz durante todo o ebook."""

CONTENT_PROMPT_EN = """Write a comprehensive ebook in English with EXACTLY this structure.
TITLE: {title}
SUBTITLE: {subtitle}
TOPIC: {content_brief}

CRITICAL: This ebook MUST be at least 8000 words. 10000-15000 words is ideal.
You need 18-25 main content sections to reach this length.
Each section must have 6-12 detailed paragraphs with deep practical content.

STRUCTURE (strict):
- Start with: ## Introduction (6+ paragraphs — compelling story or scenario, never a definition)
- Then 18-25 sections using: ## Section Title (each 6+ paragraphs)
  For each section include: core concept, step-by-step guidance, specific real-world example with names/numbers, common mistakes, pro tips
- End with: ## Conclusion (5+ paragraphs — summarize, reinforce key message, personal reflection)
- Then: ## Next Steps with 10-15 detailed actionable bullet points
- Then: ## Further Reading with 5-7 resource recommendations

REQUIRED ELEMENTS throughout:
- Use **bold** sparingly — only for absolute key terms
- Use bullet lists (- ) for tips, steps, and action items
- Include at least 6 specific real-world examples with names, ages, or numbers
- Each section must have a transition sentence connecting to the previous section
- Vary sentence length — mix short punchy sentences with longer detailed ones
- Use occasional rhetorical questions and conversational asides ("here's the thing", "let me be honest")
- Include a troubleshooting/pro tips section addressing reader objections
- Include practical exercises or reflection prompts
- Conversational but authoritative tone, like a trusted coach
- No commentary outside the markdown
- Open with a compelling story — never start with "In this chapter" or a definition"""

CONTENT_PROMPT_PT = """Escreva um ebook completo em Português com EXATAMENTE esta estrutura.
TÍTULO: {title}
SUBÍTULO: {subtitle}
TÓPICO: {content_brief}

CRÍTICO: Este ebook deve ter PELO MENOS 8000 palavras. 10000-15000 palavras é o ideal.
Você precisa de 18-25 seções principais de conteúdo para atingir este comprimento.
Cada seção deve ter 6-12 parágrafos detalhados com conteúdo prático profundo.

ESTRUTURA (rigoroso):
- Comece com: ## Introdução (6+ parágrafos — história ou cenário convincente, nunca uma definição)
- Então 18-25 seções usando: ## Título da Seção (cada 6+ parágrafos)
  Para cada seção inclua: conceito central, passo a passo, exemplo real específico com nomes/números, erros comuns, dicas de expert
- Termine com: ## Conclusão (5+ parágrafos — resumo, reforço da mensagem, reflexão pessoal)
- Então: ## Próximos Passos com 10-15 itens detalhados e acionáveis
- Então: ## Leitura Complementar com 5-7 recomendações de recursos

ELEMENTOS OBRIGATÓRIOS em todo o texto:
- Use **negrito** moderadamente — apenas para termos realmente chave
- Use listas (- ) para dicas, passos e ações
- Inclua pelo menos 6 exemplos reais específicos com nomes, idades ou números
- Cada seção deve ter uma frase de transição conectando à seção anterior
- Varie o comprimento das frases — misture frases curtas e impactantes com longas e detalhadas
- Use perguntas retóricas ocasionais e apartes conversacionais ("é o seguinte", "vou ser sincero")
- Inclua uma seção de dicas de especialista/solução de problemas
- Inclua exercícios práticos ou prompts de reflexão
- Tom conversacional mas autoritativo, como um coach de confiança
- Sem comentários fora do markdown
- Abra com uma história convincente — nunca comece com "Neste capítulo" ou uma definição"""

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
    if len(sections) < 12:
        errors.append(f"Too few sections ({len(sections)}, need >= 12)")

    return errors


def _append_worksheet(content: str, lang: str) -> str:
    if lang == "en":
        ws = """
## Self-Assessment Quiz

Take a moment to reflect on where you are right now. Rate yourself 1 (low) to 5 (high) on each:

**Before reading this book:**
- How confident are you in applying what was covered? __/5
- How clear are your next steps? __/5
- How ready are you to take action? __/5

**Key takeaways — write down 3 things that stood out:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Your first action — what will you do in the next 24 hours?**
___________________________________________________

## Quick Reference Card

Keep these key principles handy:

1. Start small — one change at a time
2. Be consistent — progress compounds daily
3. Track your results — what gets measured improves
4. Adjust as needed — no plan survives reality unchanged
5. Celebrate wins — momentum feeds on success

"""
    else:
        ws = """
## Questionário de Autoavaliação

Reserve um momento para refletir sobre onde você está agora. Avalie de 1 (baixo) a 5 (alto):

**Antes de ler este ebook:**
- Quão confiante você se sente para aplicar o que aprendeu? __/5
- Quão claros estão seus próximos passos? __/5
- Quão pronto você está para agir? __/5

**Principais aprendizados — escreva 3 coisas que mais chamaram atenção:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Sua primeira ação — o que você fará nas próximas 24 horas?**
___________________________________________________

## Cartão de Referência Rápida

Mantenha estes princípios-chave à mão:

1. Comece pequeno — uma mudança de cada vez
2. Seja consistente — o progresso se acumula diariamente
3. Acompanhe seus resultados — o que é medido melhora
4. Ajuste conforme necessário — nenhum plano sobrevive à realidade
5. Celebre vitórias — o impulso se alimenta do sucesso

"""
    import re as _re
    match = list(_re.finditer(r"^## (Further Reading|Leitura Complementar|Continue Learning|Books & Tools|Recursos Recomendados|Continue Aprendendo)", content, _re.MULTILINE))
    if match:
        pos = match[0].start()
        content = content[:pos] + ws + content[pos:]
    else:
        content += ws
    return content


def _append_action_plan(content: str, lang: str) -> str:
    if lang == "en":
        plan = """
## Your 30-Day Action Plan

Week 1 — Foundation: Focus on understanding the core principles. Read one section per day and take notes. Try one technique each day, no matter how small.

Week 2 — Building Momentum: Expand to 2-3 techniques daily. Track what works and what doesn't. Adjust your approach based on results.

Week 3 — Deepening Practice: Combine techniques for compound效果. Challenge yourself with harder applications. Reflect on your progress weekly.

Week 4 — Mastery & Automation: These practices should now feel natural. Identify which techniques give you the most results and double down on those. Plan how to sustain these habits long-term.

"""
    else:
        plan = """
## Seu Plano de 30 Dias

Semana 1 — Fundação: Foco em entender os princípios básicos. Leia uma seção por dia e faça anotações. Experimente uma técnica por dia, por menor que seja.

Semana 2 — Construindo Momentum: Expanda para 2-3 técnicas diárias. Acompanhe o que funciona e o que não funciona. Ajuste sua abordagem com base nos resultados.

Semana 3 — Aprofundando a Prática: Combine técnicas para efeito composto. Desafie-se com aplicações mais difíceis. Reflita sobre seu progresso semanalmente.

Semana 4 — Maestria e Automação: Estas práticas devem agora parecer naturais. Identifique quais técnicas trazem mais resultados e invista nelas. Planeje como sustentar estes hábitos a longo prazo.

"""
    import re as _re
    match = list(_re.finditer(r"^## (Further Reading|Leitura Complementar|Continue Learning|Books & Tools|Recursos Recomendados|Continue Aprendendo)", content, _re.MULTILINE))
    if match:
        pos = match[0].start()
        content = content[:pos] + plan + content[pos:]
    else:
        content += plan
    return content


def _de_ai(content: str, lang: str) -> str:
    content = _rename_headers(content, lang)
    content = _reduce_bold(content, ratio=0.3)
    content = _add_discourse_markers(content)
    content = _humanize_lists(content)
    content = _add_author_note(content, lang)
    content = _append_worksheet(content, lang)
    content = _append_action_plan(content, lang)
    return content


def _rename_headers(content: str, lang: str) -> str:
    import random
    EN_RENAMES = {
        "## Introduction": ["## Getting Started", "## Before We Begin", "## Why This Matters", "## Your Journey Begins"],
        "## Conclusion": ["## Wrapping Up", "## Final Thoughts", "## Bringing It All Together", "## Your Path Forward"],
        "## Next Steps": ["## Your Action Plan", "## Putting It Into Practice", "## Start Today", "## Your Next Move"],
        "## Further Reading": ["## Recommended Resources", "## Continue Learning", "## Books & Tools", "## Explore More"],
    }
    PT_RENAMES = {
        "## Introdução": ["## Primeiros Passos", "## Por Que Isso Importa", "## Sua Jornada Começa", "## Preparando o Terreno"],
        "## Conclusão": ["## Considerações Finais", "## Fechando com Chave de Ouro", "## Seu Caminho Adiante", "## Resumindo Tudo"],
        "## Próximos Passos": ["## Seu Plano de Ação", "## Colocando em Prática", "## Comece Hoje", "## Do Conhecimento à Ação"],
        "## Leitura Complementar": ["## Recursos Recomendados", "## Continue Aprendendo", "## Livros e Ferramentas", "## Aprofunde Seu Conhecimento"],
    }
    renames = EN_RENAMES if lang == "en" else PT_RENAMES
    import re as _re
    for old, choices in renames.items():
        if old in content:
            content = content.replace(old, random.choice(choices), 1)
    return content


def _reduce_bold(content: str, ratio: float = 0.3) -> str:
    import random
    import re as _re
    def _maybe_unbold(m: _re.Match) -> str:
        return m.group(1) if random.random() < ratio else m.group(0)
    return _re.sub(r"\*\*(.+?)\*\*", _maybe_unbold, content)


def _add_discourse_markers(content: str) -> str:
    import random
    import re as _re
    markers = [
        "\n\nHere's the thing: ",
        "\n\nLet me be honest with you: ",
        "\n\nYou might be wondering... ",
        "\n\nThink about it for a moment. ",
        "\n\nThe truth is, it's simpler than you think. ",
        "\n\nIf there's one thing I want you to take away, it's this: ",
        "\n\nI've seen this play out many times. ",
    ]
    headings = list(_re.finditer(r"^## .+$", content, _re.MULTILINE))
    if len(headings) >= 3:
        insert_after = random.choice(headings[1:-1])
        pos = insert_after.end()
        content = content[:pos] + random.choice(markers) + content[pos:]
    return content


def _humanize_lists(content: str) -> str:
    import re as _re
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("- ") or lines[i].strip().startswith("* "):
            list_start = i
            bullet_items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                bullet_items.append(lines[i].strip()[2:])
                i += 1
            if len(bullet_items) > 5:
                import random
                keep = bullet_items[:4]
                prose = " ".join(bullet_items[4:])
                for item in keep:
                    result.append(f"- {item}")
                result.append("")
                result.append(prose)
                result.append("")
            else:
                for item in bullet_items:
                    result.append(f"- {item}")
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


def _add_author_note(content: str, lang: str) -> str:
    import re as _re
    if lang == "en":
        note = "\n\n## A Note From the Author\n\nI wrote this book because I believe everyone deserves access to practical, no-fluff guidance. My hope is that the strategies here make a real difference in your life. Remember: the best knowledge is the kind you actually use.\n\n"
    else:
        note = "\n\n## Uma Nota do Autor\n\nEscrevi este ebook porque acredito que todos merecem acesso a um guia prático e direto ao ponto. Minha esperança é que as estratégias aqui façam uma diferença real na sua vida. Lembre-se: o melhor conhecimento é aquele que você realmente coloca em prática.\n\n"
    match = list(_re.finditer(r"^## (Conclusão|Conclusion|Wrapping Up|Final Thoughts|Considerações Finais|Bringing It All Together|Seu Caminho Adiante)", content, _re.MULTILINE))
    if match:
        pos = match[0].start()
        content = content[:pos] + note + content[pos:]
    return content


DESCRIPTION_PROMPT_EN = """Write a compelling 2-3 sentence commercial description for an ebook that will be sold on Gumroad.
Title: {title}
Subtitle: {subtitle}
Topic: {content_brief}
Write in a persuasive, benefit-driven tone. No markdown. No line breaks. Just plain text."""

DESCRIPTION_PROMPT_PT = """Escreva uma descrição comercial convincente de 2-3 frases para um ebook que será vendido no Gumroad.
Título: {title}
Subtítulo: {subtitle}
Tópico: {content_brief}
Escreva em tom persuasivo e focado em benefícios. Sem markdown. Sem quebras de linha. Apenas texto simples."""


def generate_description(niche: Niche) -> str:
    voice = niche.voice or "Natural, conversational, authoritative"
    if niche.lang == "en":
        prompt = DESCRIPTION_PROMPT_EN.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_EN.format(voice=voice)
    else:
        prompt = DESCRIPTION_PROMPT_PT.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_PT.format(voice=voice)
    return generate_text(prompt, system_prompt=system, max_tokens=500).strip()


def generate_content(niche: Niche) -> str:
    voice = niche.voice or "Natural, conversational, authoritative"
    if niche.lang == "en":
        prompt = CONTENT_PROMPT_EN.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_EN.format(voice=voice)
    else:
        prompt = CONTENT_PROMPT_PT.format(title=niche.title, subtitle=niche.subtitle, content_brief=niche.content_brief)
        system = SYSTEM_PROMPT_PT.format(voice=voice)

    last_content = None
    last_errors = []
    for attempt in range(1, MAX_RETRIES + 1):
        content = generate_text(prompt, system_prompt=system)
        errors = validate_content(content, niche.lang)
        if not errors:
            return _de_ai(content, niche.lang)
        last_content = content
        last_errors = errors
        logger.warning(f"[{niche.id}] Validation failed (attempt {attempt}): {'; '.join(errors)}")

    if last_content and len(last_content) >= MIN_CONTENT_LENGTH * 0.5:
        logger.warning(f"[{niche.id}] Accepting content with minor issues: {'; '.join(last_errors)}")
        return _de_ai(last_content, niche.lang)

    raise ValueError(f"Content validation failed after {MAX_RETRIES} attempts: {'; '.join(last_errors)}")
