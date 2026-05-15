import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from unittest.mock import patch
from content_gen import validate_content, generate_description
from config import Niche

_BODY_PAD = "paragraph " * 400  # ~4000 chars per section
_VALID_BODY_EN = "\n\n".join([_BODY_PAD] * 10) + "\n\n"
_VALID_BODY_PT = "\n\n".join([_BODY_PAD] * 10) + "\n\n"


def test_validate_content_english_valid():
    content = _make_content_en(_BODY_PAD)
    errors = validate_content(content, "en")
    assert errors == [], f"Expected no errors, got: {errors}"


def test_validate_content_portuguese_valid():
    content = _make_content_pt(_BODY_PAD)
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
        "## Social Connection",
        body,
        "## Mindful Living",
        body,
        "## Daily Practices",
        body,
        "## Long-Term Growth",
        body,
        "## Advanced Strategies",
        body,
        "## Troubleshooting Guide",
        body,
        "## Conclusion",
        body,
        "## Next Steps",
        "- Step one\n- Step two\n- Step three\n- Step four\n- Step five\n- Step six\n- Step seven\n- Step eight",
        "## Further Reading",
        "- Book 1\n- Book 2\n- Book 3\n- Podcast 1",
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
        "## Conexão Social",
        body,
        "## Vida Consciente",
        body,
        "## Práticas Diárias",
        body,
        "## Crescimento a Longo Prazo",
        body,
        "## Estratégias Avançadas",
        body,
        "## Guia de Solução de Problemas",
        body,
        "## Conclusão",
        body,
        "## Próximos Passos",
        "- Passo um\n- Passo dois\n- Passo três\n- Passo quatro\n- Passo cinco\n- Passo seis\n- Passo sete\n- Passo oito",
        "## Leitura Complementar",
        "- Livro 1\n- Livro 2\n- Livro 3\n- Podcast 1",
    ]
    return "\n\n".join(parts)


def test_validate_content_missing_sections():
    content = "## Introduction\n\nToo short, no sections.\n"
    errors = validate_content(content, "en")
    assert "Missing Conclusion section" in errors
    assert "Missing Next Steps section" in errors
    assert any("Too few sections" in e for e in errors)


def test_validate_content_too_short():
    content = ""
    errors = validate_content(content, "en")
    assert any("Too short" in e for e in errors)


def test_validate_content_portuguese_missing():
    content = "## Introdução\n\nSó introdução.\n"
    errors = validate_content(content, "pt")
    assert "Missing Conclusão section" in errors
    assert "Missing Próximos Passos section" in errors


def test_validate_content_min_sections():
    content = "\n\n".join([
        "## Introduction",
        "padding " * 500,
        "## Section 1",
        "padding " * 500,
        "## Section 2",
"padding " * 500,
        "## Section 2",
        "padding " * 500,
        "## Section 3",
        "padding " * 500,
        "## Section 4",
        "padding " * 500,
        "## Section 5",
        "padding " * 500,
        "## Section 6",
        "padding " * 500,
        "## Section 7",
        "padding " * 500,
        "## Conclusion",
        "padding " * 500,
        "## Next Steps",
        "padding " * 500,
        "## Further Reading",
        "padding " * 500,
        "## Section 4",
        "padding " * 200,
        "## Section 5",
        "padding " * 200,
        "## Section 6",
        "padding " * 200,
        "## Section 7",
        "padding " * 200,
        "## Conclusion",
        "padding " * 200,
        "## Next Steps",
        "padding " * 200,
    ])
    errors = validate_content(content, "en")
    assert errors == [], f"Expected no errors, got: {errors}"


@patch("content_gen.generate_text")
def test_generate_description_en(mock_gen):
    mock_gen.return_value = "A practical guide to transforming your mornings."
    niche = Niche(id="test", title="Test Title", subtitle="Test Sub", lang="en", cover_keywords="test", content_brief="test brief", color1="#000", color2="#fff")
    desc = generate_description(niche)
    assert "transforming your mornings" in desc
    assert desc == mock_gen.return_value


@patch("content_gen.generate_text")
def test_generate_description_pt(mock_gen):
    mock_gen.return_value = "Um guia pratico para transformar suas manhas."
    niche = Niche(id="test", title="Test Title", subtitle="Test Sub", lang="pt", cover_keywords="teste", content_brief="teste breve", color1="#000", color2="#fff")
    desc = generate_description(niche)
    assert "transformar suas manhas" in desc
    assert desc == mock_gen.return_value
