from dataclasses import dataclass
from typing import List, Optional
import os

@dataclass
class Niche:
    id: str
    title: str
    subtitle: str
    lang: str
    cover_keywords: str
    content_brief: str
    color1: str
    color2: str

NICHES_EN: List[Niche] = [
    Niche(
        id="morning-routine",
        title="The 5 AM Miracle: Transform Your Mornings",
        subtitle="Win the Morning, Win Your Day",
        lang="en",
        cover_keywords="sunrise morning calm peaceful minimal productivity desk coffee",
        content_brief="A practical guide to crafting a powerful morning routine. Cover waking up early without struggle, morning exercise, mindfulness, journaling, and planning the day. Focus on actionable habits that boost productivity and mental clarity from the first hour.",
        color1="#1E3A5F",
        color2="#2563EB",
    ),
    Niche(
        id="anxiety-relief",
        title="Stop Overthinking: A Practical Guide to Peace of Mind",
        subtitle="Quiet Your Mind, Find Your Calm",
        lang="en",
        cover_keywords="calm peaceful nature zen meditation minimal serene landscape",
        content_brief="A guide to managing anxiety and breaking the overthinking cycle. Cover cognitive techniques, breathing exercises, thought reframing, grounding methods, and daily practices for mental peace. Practical tools anyone can use immediately.",
        color1="#4C1D95",
        color2="#7C3AED",
    ),
    Niche(
        id="side-hustle",
        title="The Side Hustle Blueprint: Extra Income in 30 Days",
        subtitle="Turn Your Skills Into Cash",
        lang="en",
        cover_keywords="money growth laptop freelance modern professional startup minimal",
        content_brief="A step-by-step guide to starting a side hustle. Cover freelancing platforms, digital products, service-based businesses, time management for side work, and scaling from zero to consistent income. Realistic advice for busy professionals.",
        color1="#064E3B",
        color2="#059669",
    ),
    Niche(
        id="fat-loss",
        title="Intermittent Fasting for Busy People",
        subtitle="Burn Fat Without Burning Out",
        lang="en",
        cover_keywords="fresh healthy food bowl ingredients colorful fitness modern kitchen",
        content_brief="A beginner-friendly guide to intermittent fasting for weight loss. Cover different fasting methods, meal planning, managing hunger, exercise during fasting, and sustainable habits. Science-based practical approach for busy schedules.",
        color1="#7C2D12",
        color2="#EA580C",
    ),
    Niche(
        id="copywriting",
        title="Copywriting Secrets That Sell",
        subtitle="Words That Turn Readers Into Buyers",
        lang="en",
        cover_keywords="creative writing typewriter modern office minimalist professional",
        content_brief="A practical guide to persuasive copywriting. Cover headlines that hook, benefit-driven copy, storytelling frameworks, calls-to-action that convert, and email sequences. Actionable templates and real examples for marketers and entrepreneurs.",
        color1="#881337",
        color2="#DC2626",
    ),
    Niche(
        id="dating-confidence",
        title="The Art of Charisma: Attract Anyone Naturally",
        subtitle="Unlock Your Natural Magnetism",
        lang="en",
        cover_keywords="romantic sunset couple silhouette warm confident connection",
        content_brief="A guide to building dating confidence and authentic charisma. Cover conversation skills, body language, emotional intelligence, overcoming rejection fear, and building genuine connections. Practical advice for men and women seeking meaningful relationships.",
        color1="#831843",
        color2="#DB2777",
    ),
    Niche(
        id="digital-detox",
        title="Digital Detox: Reclaim Your Focus",
        subtitle="Break Free From Screen Addiction",
        lang="en",
        cover_keywords="nature unplugged disconnect phone away peace forest calm",
        content_brief="A practical guide to reducing screen time and digital dependency. Cover smartphone addiction breaking techniques, social media boundaries, focus restoration practices, and creating offline habits. Science-backed strategies for mental clarity.",
        color1="#1E3A5F",
        color2="#2563EB",
    ),
    Niche(
        id="sleep-better",
        title="Sleep Better Tonight: Science-Backed Solutions",
        subtitle="Wake Up Refreshed Every Morning",
        lang="en",
        cover_keywords="bedroom cozy calm night sleep peaceful dark minimal serene",
        content_brief="A comprehensive guide to improving sleep quality naturally. Cover sleep hygiene, circadian rhythm optimization, evening routines, diet and sleep connection, and natural remedies for insomnia. Evidence-based advice for deep restorative sleep.",
        color1="#4C1D95",
        color2="#7C3AED",
    ),
    Niche(
        id="confidence",
        title="Unshakeable Confidence: Own Your Power",
        subtitle="Stop Doubting, Start Living",
        lang="en",
        cover_keywords="confident person silhouette sunrise mountain top powerful inspiring",
        content_brief="A guide to building unshakeable self-confidence. Cover imposter syndrome, public speaking, body language, assertive communication, and overcoming self-doubt. Practical exercises backed by psychology research.",
        color1="#064E3B",
        color2="#059669",
    ),
    Niche(
        id="minimalism",
        title="Minimalist Living: Less Stuff, More Life",
        subtitle="Declutter Your Space, Simplify Your Mind",
        lang="en",
        cover_keywords="minimalist white room clean organized simple peaceful interior design",
        content_brief="A beginner-friendly guide to minimalist living. Cover decluttering methods, mindful consumption, organizing spaces, digital minimalism, and intentional living. Focus on practical steps to reduce possessions and increase happiness.",
        color1="#7C2D12",
        color2="#EA580C",
    ),
    Niche(
        id="negotiation",
        title="Negotiate Anything: Get What You Want",
        subtitle="Master the Art of Win-Win Deals",
        lang="en",
        cover_keywords="handshake business deal professional confident corporate minimal",
        content_brief="A practical guide to effective negotiation skills for everyday life. Cover salary negotiation, business deals, persuasion techniques, reading people, and creating win-win outcomes. Real-world scripts and strategies for any situation.",
        color1="#881337",
        color2="#DC2626",
    ),
    Niche(
        id="habit-stacking",
        title="Atomic Habits: Small Changes, Big Results",
        subtitle="Transform Your Life One Tiny Habit at a Time",
        lang="en",
        cover_keywords="domino effect chain reaction progress growth success minimal abstract",
        content_brief="A guide to building lasting habits through small incremental changes. Cover habit stacking technique, identity-based habits, environment design, accountability systems, and overcoming plateaus. Research-based approach for sustainable personal transformation.",
        color1="#831843",
        color2="#DB2777",
    ),
]

NICHES_PT: List[Niche] = [
    Niche(
        id="renda-extra",
        title="Renda Extra Online: Do Zero ao Primeiro Dinheiro",
        subtitle="Comece a Ganhar Hoje Mesmo",
        lang="pt",
        cover_keywords="dinheiro online notebook freelancer profissional moderno minimalista",
        content_brief="Um guia pratico para gerar renda extra online. Cobre freelancing, produtos digitais, marketing de afiliados, criacao de conteudo e economias no dia a dia. Foco em metodos comprovados que qualquer um pode comecar sem investimento inicial.",
        color1="#1E3A5F",
        color2="#2563EB",
    ),
    Niche(
        id="concurso-publico",
        title="Tecnicas Infalliveis para Passar em Concursos",
        subtitle="Estude Menos, Aprenda Mais",
        lang="pt",
        cover_keywords="estudo livros concurso foco aprovacao disciplina organizacao",
        content_brief="Um guia completo de preparacao para concursos publicos. Cobre tecnicas de estudo comprovadas, gestao de tempo, revisao inteligente, saude mental durante a preparacao e estrategias para a prova. Metodos usados por aprovados nos concursos mais concorridos.",
        color1="#4C1D95",
        color2="#7C3AED",
    ),
    Niche(
        id="emagrecimento",
        title="Dieta Inteligente: Emagreca Sem Sofrer",
        subtitle="Resultados Reais com Habitos Sustentaveis",
        lang="pt",
        cover_keywords="emagrecimento saudavel alimentos naturais frutasexercicio bem-estar",
        content_brief="Um guia pratico de emagrecimento sem dietas radicais. Cobre reeducacao alimentar, jejum intermitente, exercicios eficientes, controle de ansiedade alimentar e receitas saudaveis. Abordagem sustentavel para resultados duradouros.",
        color1="#7C2D12",
        color2="#EA580C",
    ),
    Niche(
        id="quitacao-dividas",
        title="Como Sair das Dividas em 12 Meses",
        subtitle="Recupere Seu Controle Financeiro",
        lang="pt",
        cover_keywords="liberdade financeira dividas controle economias planejamento futuro",
        content_brief="Um plano passo a passo para quitar dividas e recuperar a saude financeira. Cobre negociacao com credores, metodos de priorizacao de dividas, corte de gastos, geracao de renda extra e prevencao de novo endividamento. Estrategias reais para o cenario brasileiro.",
        color1="#064E3B",
        color2="#059669",
    ),
    Niche(
        id="receitas-fit",
        title="Receitas Fit: Comida Saudavel no Dia a Dia",
        subtitle="Sabor sem Culpa",
        lang="pt",
        cover_keywords="receitas saudaveis ingredientes frescos coloridos alimentos naturais cozinha",
        content_brief="Um livro de receitas fit para o dia a dia. Cobre cafe da manha proteico, almocos equilibrados, jantares leves e lanches saudaveis. Cada receita leva menos de 20 minutos e usa ingredientes acessiveis no Brasil.",
        color1="#881337",
        color2="#DC2626",
    ),
    Niche(
        id="ansiedade-br",
        title="Controle a Ansiedade: Tecnicas que Funcionam",
        subtitle="Acalme Sua Mente, Viva Melhor",
        lang="pt",
        cover_keywords="mente calma paz meditacao natureza tranquilidade bem-estar equilibrio",
        content_brief="Um guia pratico para controlar a ansiedade no dia a dia. Cobre tecnicas de respiracao, reestruturacao cognitiva, mindfulness, organizacao da rotina e quando buscar ajuda profissional. Abordagem pratica adaptada a realidade brasileira.",
        color1="#831843",
        color2="#DB2777",
    ),
    Niche(
        id="marketing-digital-br",
        title="Marketing Digital para Iniciantes",
        subtitle="Construa Seu Negocio Online",
        lang="pt",
        cover_keywords="marketing digital redes sociais crescimento online profissional moderno",
        content_brief="Um guia introdutorio ao marketing digital para brasileiros. Cobre redes sociais, criacao de conteudo, email marketing, anuncios online e metricas essenciais. Estrategias praticas para quem quer comecar do zero no digital.",
        color1="#1E3A5F",
        color2="#2563EB",
    ),
    Niche(
        id="produtividade-br",
        title="Mais Produtividade: Menos Horas, Mais Resultados",
        subtitle="Trabalhe Inteligente, Nao Duro",
        lang="pt",
        cover_keywords="produtividade organizacao mesa trabalho foco eficiencia minimalista",
        content_brief="Um guia de produtividade adaptado a realidade brasileira. Cobre metodos como Pomodoro e GTD, gestao de tempo, eliminacao de distracoes, rotinas eficientes e equilibrio entre vida pessoal e profissional. Dicas acionaveis para resultados imediatos.",
        color1="#4C1D95",
        color2="#7C3AED",
    ),
    Niche(
        id="relacionamentos",
        title="Relacionamentos Saudaveis: Comunicacao que Conecta",
        subtitle="Aprenda a se Comunicar com Empatia",
        lang="pt",
        cover_keywords="casal conversa conexao amor dialogo respeito comprensao",
        content_brief="Um guia para construir relacionamentos saudaveis atraves da comunicacao. Cobre escuta ativa, expressao de sentimentos, resolucao de conflitos, limites saudaveis e fortalecimento de vinculos. Conselhos praticos para casais e familias.",
        color1="#7C2D12",
        color2="#EA580C",
    ),
    Niche(
        id="autocuidado-br",
        title="Guia Completo de Autocuidado",
        subtitle="Cuide de Quem Realmente Importa: Voce",
        lang="pt",
        cover_keywords="autocuidado spa velas paz relaxamento bem-estar cuidado pessoal",
        content_brief="Um guia completo de autocuidado para a vida corrida. Cobre saude fisica, saude mental, alimentacao consciente, exercicios, sono reparador e momentos de lazer. Rotinas praticas para incluir autocuidado na agenda lotada.",
        color1="#064E3B",
        color2="#059669",
    ),
    Niche(
        id="inteligencia-emocional",
        title="Inteligencia Emocional: Domine suas Emocoes",
        subtitle="O Segredo do Sucesso Pessoal e Profissional",
        lang="pt",
        cover_keywords="equilibrio emocional mente coracao inteligencia autoconhecimento crescimento",
        content_brief="Um guia para desenvolver inteligencia emocional. Cobre autoconhecimento, regulacao emocional, empatia, habilidades sociais e motivacao. Baseado na ciencia da inteligencia emocional aplicada a vida pessoal e profissional no contexto brasileiro.",
        color1="#881337",
        color2="#DC2626",
    ),
    Niche(
        id="orcamento-domestico",
        title="Organize seu Orcamento domestico",
        subtitle="Gaste Melhor, Viva Tranquilo",
        lang="pt",
        cover_keywords="orcamento planejamento financeiro controle gastos economia lar",
        content_brief="Um guia pratico para organizar as financas domesticas. Cobre criacao de orcamento mensal, categorizacao de gastos, poupanca, corte de despesas desnecessarias e metas financeiras familiares. Metodos simples que funcionam no dia a dia brasileiro.",
        color1="#831843",
        color2="#DB2777",
    ),
]

PRICE_EN_USD = 499
PRICE_PT_BRL = 997

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_TEXT_MODEL = "deepseek/deepseek-chat"
OPENROUTER_IMAGE_MODEL = "google/gemini-2.5-flash-image"  # no image models available on account, fallback used
MAX_TOKENS = 32768
TEMP = 0.7

COVER_IMAGE_WIDTH = 1748
COVER_IMAGE_HEIGHT = 2480
COVER_PROMPT_TEMPLATE = (
    "Create a professional ebook cover image with the following theme: {keywords}. "
    "Style: modern, clean, visually striking. Use a 2:3 portrait aspect ratio. "
    "No text on the image."
)

PAGE_FORMAT = "A5"

MARKETS = [
    {
        "name": "en",
        "niches": NICHES_EN,
        "price": PRICE_EN_USD,
        "currency": "usd",
    },
    {
        "name": "pt",
        "niches": NICHES_PT,
        "price": PRICE_PT_BRL,
        "currency": "brl",
    },
]

def get_api_key() -> Optional[str]:
    return os.getenv("OPENROUTER_API_KEY")
