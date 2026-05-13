import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from content_gen import validate_content

_VALID_BODY_EN = "\n\n".join([
    "Intro text with enough content to pass the minimum length validation threshold.",
    "First section with substantial content that adds to the total character count.",
    "Second section continues with more meaningful text for padding purposes.",
    "Third section ensures we reach the minimum length requirement easily.",
    "Fourth section adding even more text to make sure validation passes.",
    "Fifth section wrapping up the main body with plenty of words here.",
    "Wrapping up everything nicely with a conclusion summary paragraph.",
]) + "\n\n"

_VALID_BODY_PT = "\n\n".join([
    "Texto de introdução com conteúdo suficiente para passar a validação.",
    "Primeira seção com conteúdo substancial para aumentar a contagem.",
    "Segunda seção continua com mais texto significativo de preenchimento.",
    "Terceira seção garante que atingimos o tamanho mínimo facilmente.",
    "Quarta seção adicionando ainda mais texto para passar validação.",
    "Quinta seção finalizando o corpo principal com muitas palavras aqui.",
    "Finalizando tudo com um parágrafo de conclusão bem resumido.",
]) + "\n\n"


def test_validate_content_english_valid():
    content = _make_content_en("Some padding text to ensure we reach the minimum length threshold for this test content.")
    errors = validate_content(content, "en")
    assert errors == [], f"Expected no errors, got: {errors}"


def test_validate_content_portuguese_valid():
    content = _make_content_pt("Texto de preenchimento para garantir que atingimos o tamanho mínimo necessário para passar.")
    errors = validate_content(content, "pt")
    assert errors == [], f"Expected no errors, got: {errors}"


def _make_content_en(body: str) -> str:
    parts = [
        "## Introduction",
        body,
        "## Morning Routine Hacks",
        body,
        "## Workplace Efficiency",
        body,
        "## Digital Detox Strategies",
        body,
        "## Evening Wind-Down Rituals",
        body,
        "## Building Lasting Habits",
        body,
        "## Conclusion",
        body,
        "## Next Steps",
        "- Step one\n- Step two\n- Step three\n- Step four\n- Step five",
    ]
    return "\n\n".join(parts)


def _make_content_pt(body: str) -> str:
    parts = [
        "## Introdução",
        body,
        "## Rotina Matinal",
        body,
        "## Eficiência no Trabalho",
        body,
        "## Estratégias de Desintoxicação Digital",
        body,
        "## Rituais Noturnos",
        body,
        "## Construindo Hábitos Duradouros",
        body,
        "## Conclusão",
        body,
        "## Próximos Passos",
        "- Passo um\n- Passo dois\n- Passo três\n- Passo quatro\n- Passo cinco",
    ]
    return "\n\n".join(parts)


def test_validate_content_missing_sections():
    content = "## Introduction\n\nToo short, no sections.\n"
    errors = validate_content(content, "en")
    assert "Missing ## Conclusion" in errors
    assert "Missing ## Next Steps" in errors
    assert any("Too few sections" in e for e in errors)


def test_validate_content_too_short():
    content = ""
    errors = validate_content(content, "en")
    assert any("Too short" in e for e in errors)


def test_validate_content_portuguese_missing():
    content = "## Introdução\n\nSó introdução.\n"
    errors = validate_content(content, "pt")
    assert "Missing ## Conclusão" in errors
    assert "Missing ## Próximos Passos" in errors


def test_validate_content_min_sections():
    content = "\n\n".join([
        "## Introduction",
        "padding" * 50,
        "## Section 1",
        "padding" * 50,
        "## Section 2",
        "padding" * 50,
        "## Section 3",
        "padding" * 50,
        "## Section 4",
        "padding" * 50,
        "## Section 5",
        "padding" * 50,
        "## Conclusion",
        "padding" * 50,
        "## Next Steps",
        "padding" * 50,
    ])
    errors = validate_content(content, "en")
    assert errors == [], f"Expected no errors, got: {errors}"
