"""
Daily News + English Word Learner
- NewsAPI로 관심 분야 뉴스를 가져오고
- Gemini(gemini-2.5-flash)로 구조화된 한국어 요약 + 난이도별 핵심 영단어 5개 추출
"""

DIFFICULTY_OPTIONS = ["초급", "중급", "고급"]

CATEGORY_OPTIONS: dict[str, dict[str, str]] = {
    "ai_tech": {
        "label": "🤖 AI / Tech",
        "query": "AI OR technology",
        "sources": "techcrunch,the-verge,wired,ars-technica,engadget",
    },
    "economy": {
        "label": "💰 Economy",
        "query": "economy OR market",
        "sources": "reuters,bloomberg,the-wall-street-journal,financial-times,fortune",
    },
    "politics": {
        "label": "🌍 Politics",
        "query": "politics",
        "sources": "reuters,the-washington-post,bbc-news,al-jazeera-english,the-guardian-uk",
    },
    "sports": {
        "label": "⚽ Sports",
        "query": "sports",
        "sources": "espn,bbc-sport,bleacher-report,fox-sports",
    },
    "climate": {
        "label": "🌱 Climate",
        "query": "climate OR environment",
        "sources": "reuters,bbc-news,national-geographic,new-scientist",
    },
}

DIFFICULTY_GUIDE = {
    "초급": (
        "기본적이고 일상적인 어휘 위주로 추출하세요. "
        "CEFR A2~B1 수준의 단어를 고르고, 너무 어렵거나 전문적인 용어는 피하세요. "
        "예문도 짧고 쉬운 문장으로 작성하세요."
    ),
    "중급": (
        "반드시 신문·잡지에 자주 등장하지만 한국 학습자가 의식적으로 학습해야 활용 가능한 "
        "어휘만 추출하세요. **CEFR B2 후반에서 C1 진입 수준**이 목표입니다. 너무 일상적인 "
        "단어, 한국 중·고등학교 어휘책에 실리는 단어, TOEIC 600점대 학습자가 이미 아는 단어는 "
        "전부 제외합니다.\n"
        "**자기 검증 규칙(Self-check)**: 각 단어를 선정하기 전에 스스로 질문하세요 — "
        "'한국의 대학생이 TOEIC 700~800점대일 때, 이 단어를 보고 1초 안에 뜻을 떠올릴 수 있는가?' "
        "→ YES 라면 그 단어는 **반드시 제외**하고 더 어려운 동의어·연관 표현으로 교체하세요.\n"
        "절대 포함하면 안 되는 단어 예시 (확장된 금지 목록):\n"
        "  · 기초 어휘: people, world, country, time, year, day, good, bad, big, small, new, old, "
        "make, use, get, go, come, see, know, think, say, tell, work, help, want, need, like, "
        "live, play, run, study, school, computer, internet, phone, family, friend, money, "
        "problem, change, important, best, very, really, also, however, because\n"
        "  · 흔한 중급(이미 너무 쉬움): expand, launch, ensure, decline, demand, witness, "
        "propose, criticize, establish, address(v), implement, impact, trend, transition, "
        "potential, framework, struggle, comprehensive, significant, emerging, enhance, "
        "regulate, diverse, sustainable, controversy, initiative, increase, decrease, improve, "
        "create, develop, provide, include, support, offer, focus, allow, consider, continue, "
        "according to, in addition\n"
        "포함해야 할 단어 예시 (B2 후반~C1):\n"
        "  · 동사: scrutinize, undermine, hinder, disrupt, bolster, foster, cultivate, "
        "navigate(비유적 의미), unveil, tackle, curb, oust, rebuke, advocate, downplay, "
        "spearhead, derail, overhaul, reignite, reshape\n"
        "  · 형용사: prevalent, controversial, ambiguous, persistent, deliberate, compelling, "
        "profound, pivotal, robust, viable, lucrative, daunting, contentious, unprecedented, "
        "imminent, pervasive, stark, sweeping, looming\n"
        "  · 명사: skepticism, breakthrough, allegation, scrutiny, surge, plunge, backlash, "
        "turmoil, momentum, fallout, hurdle, loophole, watershed, milestone, setback\n"
        "이 정도 난이도를 기준으로 삼되, 똑같은 단어만 반복하지 말고 기사 맥락에 맞게 다양하게 "
        "고르세요. 단어 선정이 어려우면 흔한 동사보다는 **저널리즘에서 자주 쓰는 비유적 동사** "
        "(예: spark, fuel, weigh on, hinge on, grapple with) 또는 **연어(collocation)** "
        "를 선택하세요. 예문은 격식 있는 뉴스/사설 문체로 작성합니다.\n"
        "**원문 보강 규칙**: 만약 뉴스 원문이 짧거나 단순해서 위 기준을 만족하는 어휘를 5개 "
        "추출할 수 없다면, 해당 뉴스의 **주제(분야)와 직접 관련된 영역**에서 기자·전문가가 "
        "실제로 자주 쓰는 B2 후반~C1 수준 어휘를 추가로 선정해 5개를 채우세요. 예) 기사가 "
        "AI 관련이면 deployment, scalability, oversight, mainstream(v), commodify 같은 어휘; "
        "경제 기사면 downturn, headwinds, tightening, sentiment, valuations 같은 어휘. "
        "단, 뉴스 맥락과 **완전히 무관한** 단어는 절대 포함하지 마세요. 보강한 단어의 예문은 "
        "해당 뉴스의 주제·고유명사를 자연스럽게 녹여 기사와 연결되도록 작성하세요."
    ),
    "고급": (
        "반드시 해당 기사 분야의 전문 용어(domain-specific jargon), 학술적 표현, "
        "저널리즘/격식체 고급 어휘, 또는 자주 쓰이지 않는 정교한 동사·형용사·관용 표현만 추출하세요. "
        "CEFR C1~C2 수준이어야 합니다.\n"
        "절대 포함하면 안 되는 단어 예시: coding, safety, connection, system, computer, "
        "company, market, people, world, change, problem, important, develop, create, "
        "use, make, work, help, study, report, government, country, news, technology 등 "
        "중·고등학생도 아는 일반 어휘는 모두 제외합니다.\n"
        "포함해야 할 단어 예시: proliferation, geopolitical, paradigm, scrutiny, "
        "leverage(동사), unprecedented, mitigate, exacerbate, ramifications, "
        "deterrent, contingent, divergence, insolvency, cohort, ubiquitous 처럼 "
        "신문 사설이나 학술지에 등장하는 수준의 어휘.\n"
        "각 단어 옆에 학습 가치를 보장할 수 있을 때만 선정하고, 기준에 맞지 않으면 차라리 "
        "다른 표현(구동사·관용어구)으로 대체하세요. 예문은 격식 있는 저널리즘 문체로 작성합니다.\n"
        "**원문 보강 규칙**: 만약 뉴스 원문이 짧거나 단순해서 위 기준을 만족하는 고급 어휘를 5개 "
        "추출할 수 없다면, 해당 뉴스의 **주제(분야)와 직접 관련된 영역**에서 전문가·기자·학자가 "
        "실제로 자주 쓰는 고급 어휘를 추가로 선정해 5개를 채우세요. 예) 기사가 AI 관련이면 "
        "inference, fine-tuning, hallucination, alignment, capability overhang 같은 AI 분야 "
        "고급 용어; 경제 기사면 yield curve, monetary tightening, recession risk, basis points "
        "같은 금융 전문어. 단, 뉴스 맥락과 **완전히 무관한** 단어(예: 정치 기사에 화학 용어)는 "
        "절대 포함하지 마세요. 보강한 단어의 예문은 해당 뉴스의 주제·고유명사를 자연스럽게 "
        "녹여서 기사와 연결되도록 작성하세요."
    ),
}

import json
import os
import random
from datetime import datetime

import google.generativeai as genai
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_API_URL = "https://newsapi.org/v2/everything"
GEMINI_MODEL = "gemini-2.5-flash"


def _is_quota_error(exc: Exception) -> bool:
    """429 / quota / rate-limit 계열 오류인지 판별."""
    msg = str(exc).lower()
    keywords = ("429", "quota", "resource_exhausted", "rate limit", "ratelimit", "exceeded")
    return any(k in msg for k in keywords)


def call_gemini_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
) -> str | None:
    """첫 번째 키로 호출하고, 429 등 쿼터 초과 시 두 번째 키로 자동 재시도."""
    keys = [k for k in (GEMINI_API_KEY, GEMINI_API_KEY_2) if k]
    if not keys:
        st.error("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return None

    last_exc: Exception | None = None
    for i, key in enumerate(keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=system_prompt,
                generation_config={
                    "temperature": temperature,
                    "response_mime_type": "application/json",
                },
            )
            response = model.generate_content(user_prompt)
            return (response.text or "").strip()
        except Exception as exc:
            last_exc = exc
            if _is_quota_error(exc) and i < len(keys) - 1:
                st.warning(
                    f"🔁 첫 번째 API 키 쿼터 초과 — 두 번째 키(GEMINI_API_KEY_2)로 재시도합니다."
                )
                continue
            break

    st.error(f"Gemini API 호출 중 오류: {last_exc}")
    return None


st.set_page_config(
    page_title="NewsVoca",
    page_icon="📰",
    layout="centered",
)


def inject_custom_css() -> None:
    """NewsVoca 전용 스타일을 주입 (Streamlit 기본 UI 숨김 + 모던 카드/버튼/탭)."""
    st.markdown(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ─── Streamlit 기본 UI 숨김 ─────────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] { display: none; }
        [data-testid="stToolbar"] { display: none; }

        /* ─── 전역 타이포 & 배경 ─────────────────────── */
        html, body, .stApp, [class*="css"] {
            font-family: 'Pretendard', 'Inter', -apple-system, BlinkMacSystemFont,
                         'Segoe UI', Roboto, sans-serif;
            color: #1f2937;
        }
        .stApp {
            background-color: #f8f9fa;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        /* ─── 앱 헤더 ─────────────────────── */
        .nv-header {
            padding: 0.25rem 0 1.1rem 0;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid #e5e7eb;
        }
        .nv-brand {
            display: flex;
            align-items: baseline;
            gap: 0.55rem;
            margin: 0;
        }
        .nv-logo {
            font-size: 1.6rem;
            line-height: 1;
        }
        .nv-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #111827;
            margin: 0;
            line-height: 1.1;
        }
        .nv-subtitle {
            margin: 0.3rem 0 0 0;
            color: #6b7280;
            font-size: 0.95rem;
            font-weight: 500;
        }

        /* ─── 카드(bordered container) ─────────────────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff;
            border: 1px solid #e5e7eb !important;
            border-radius: 14px !important;
            padding: 1.25rem 1.4rem !important;
            box-shadow: 0 1px 2px rgba(17, 24, 39, 0.04),
                        0 4px 14px rgba(17, 24, 39, 0.04);
            transition: box-shadow .2s ease, transform .15s ease, border-color .2s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 2px 6px rgba(17, 24, 39, 0.06),
                        0 10px 28px rgba(17, 24, 39, 0.06);
            border-color: #d1d5db !important;
        }
        /* 중첩 카드(단어/analysis 내부)는 그림자를 살짝 약하게 */
        [data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stVerticalBlockBorderWrapper"] {
            box-shadow: none;
            background: #fafbfc;
            border-radius: 10px !important;
            padding: 0.9rem 1.05rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stVerticalBlockBorderWrapper"]:hover {
            background: #f3f4f6;
            box-shadow: none;
        }

        /* 카드 내부 h3(뉴스 제목) 강조 */
        [data-testid="stVerticalBlockBorderWrapper"] h3 {
            font-size: 1.22rem;
            font-weight: 700;
            color: #111827;
            line-height: 1.45;
            margin: 0 0 0.4rem 0 !important;
            letter-spacing: -0.01em;
        }
        [data-testid="stVerticalBlockBorderWrapper"] h4 {
            font-size: 1rem;
            font-weight: 700;
            color: #1f2937;
            margin-top: 1rem !important;
            margin-bottom: 0.35rem !important;
        }

        /* 캡션(출처·날짜·예문) 회색 */
        [data-testid="stCaptionContainer"],
        .stCaption, small {
            color: #6b7280 !important;
            font-size: 0.83rem !important;
        }

        /* ─── 버튼 ─────────────────────── */
        .stButton, .stDownloadButton {
            width: 100%;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 500;
            padding: 0.55rem 1rem;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            color: #374151;
            transition: all .15s ease;
            box-shadow: none;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            white-space: nowrap;
        }
        .stButton > button > div,
        .stButton > button p {
            width: auto !important;
            margin: 0 !important;
            text-align: center !important;
            white-space: nowrap !important;
        }
        .stButton > button:hover {
            border-color: #9ca3af;
            background: #f9fafb;
            color: #111827;
        }
        .stButton > button:active { transform: translateY(1px); }
        .stButton > button:focus:not(:active) {
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }
        /* Primary 버튼 (선택된 분야/퀴즈 생성 등) */
        .stButton > button[kind="primary"] {
            background: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
            font-weight: 600;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
        }
        .stButton > button[kind="primary"]:hover {
            background: #1d4ed8;
            border-color: #1d4ed8;
            color: #ffffff;
        }

        /* ─── 탭 ─────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            width: 100%;
            gap: 0;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 1.2rem;
        }
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 0;
            justify-content: center;
            padding: 0.85rem 1.2rem;
            font-size: 1.05rem;
            font-weight: 500;
            color: #6b7280;
            background: transparent;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
        }
        .stTabs [data-baseweb="tab"] [data-testid="stMarkdownContainer"] p {
            font-size: 1.05rem !important;
            margin: 0 !important;
        }
        .stTabs [data-baseweb="tab"]:hover { color: #111827; }
        .stTabs [aria-selected="true"] {
            color: #2563eb !important;
            border-bottom: 2px solid #2563eb !important;
            font-weight: 600;
        }

        /* ─── 입력/선택 ─────────────────────── */
        [data-baseweb="select"] > div,
        .stTextInput > div > div,
        .stNumberInput > div > div {
            border-radius: 10px !important;
            border-color: #e5e7eb !important;
        }

        /* ─── Metric ─────────────────────── */
        [data-testid="stMetric"] {
            background: #ffffff;
            padding: 0.9rem 1.1rem;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(17, 24, 39, 0.03);
        }
        [data-testid="stMetricValue"] {
            font-size: 1.7rem !important;
            font-weight: 700;
            color: #111827;
        }
        [data-testid="stMetricLabel"] { color: #6b7280; }

        /* ─── 사이드바 ─────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #eceff3;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-weight: 700;
            color: #111827;
            letter-spacing: -0.01em;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            border: none;
            background: transparent;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            font-weight: 600;
            color: #1f2937;
        }

        /* ─── Info / Warning / Success ─────────────────────── */
        .stAlert {
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }

        /* ─── 구분선 ─────────────────────── */
        hr {
            border: none;
            border-top: 1px solid #eef0f3;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    if "articles" not in st.session_state:
        st.session_state.articles = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "중급"
    if "analysis" not in st.session_state:
        # {article_index: {"summary": dict, "words": [{"word","meaning","example"}]}}
        st.session_state.analysis = {}
    if "memorized" not in st.session_state:
        # {(article_index, word): {"word", "meaning", "article_title"}}
        # 키가 존재하면 외운 단어로 간주하고, 토글 시 키를 제거합니다.
        st.session_state.memorized = {}
    if "quiz_stats" not in st.session_state:
        # {word: {"correct": int, "wrong": int}}
        st.session_state.quiz_stats = {}
    if "quiz_history" not in st.session_state:
        # [{"timestamp": str, "score": int, "total": int}]
        st.session_state.quiz_history = []
    if "current_quiz" not in st.session_state:
        # {"questions": [...], "answers": [int|None, ...], "submitted": bool}
        st.session_state.current_quiz = None


def fetch_news(query: str, page_size: int = 5, sources: str | None = None) -> list[dict]:
    if not NEWS_API_KEY:
        st.error("NEWS_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return []

    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "relevancy",
        "apiKey": NEWS_API_KEY,
    }
    if sources:
        params["sources"] = sources
    try:
        resp = requests.get(NEWS_API_URL, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"뉴스를 가져오는 중 오류가 발생했습니다: {exc}")
        return []

    data = resp.json()
    if data.get("status") != "ok":
        st.error(f"NewsAPI 오류: {data.get('message', 'unknown error')}")
        return []
    return data.get("articles", [])


def analyze_article(
    title: str,
    description: str,
    content: str,
    difficulty: str = "중급",
) -> dict | None:
    article_text = "\n".join(
        part for part in [title, description, content] if part
    )

    difficulty_instruction = DIFFICULTY_GUIDE.get(difficulty, DIFFICULTY_GUIDE["중급"])

    system_prompt = (
        "You are a helpful assistant that summarizes English news articles in Korean "
        "and extracts important English vocabulary for Korean learners. "
        "Always respond in valid JSON only."
    )

    user_prompt = f"""다음 영어 뉴스 기사를 분석해주세요.

[기사]
{article_text}

[작업]
1) 한국어로 아래 3개 섹션을 작성하세요. **세 섹션 모두 불렛 포인트나 줄바꿈된 항목 나열이 아니라,
   문장이 자연스럽게 이어지는 하나의 단락(paragraph)** 으로 작성하세요. 각 단락은 2~4문장,
   문장은 자연스러운 연결어("또한", "특히", "이로 인해", "한편" 등)로 흐름 있게 서술합니다.

   - key_points: 기사의 진짜 핵심 사실을 담은 2~4문장 단락. 반드시 다음 요소를 자연스럽게 녹여서
     서술하세요: (a) 누가/무엇이/어디서/언제 무슨 일을 했는지, (b) 구체적인 숫자·금액·비율·날짜·
     고유명사(인물·기관·제품명), (c) 발표/결정/사건의 핵심 결론.
     절대 금지: 부수적 디테일, 서론적 배경 설명, "~할 수 있다·~로 보인다" 류 추측, 동어반복,
     "이 뉴스는 중요하다" 류 일반론. 기사 원문이 짧아 4문장을 채울 수 없다면 억지로 늘리지 말고
     2문장으로만 단락을 구성하세요.
   - background: 이 뉴스를 이해하기 위해 알아야 할 사전 지식·맥락을 2~3문장 단락으로 서술.
   - significance: 이 뉴스가 산업·사회·시장에 가지는 실질적 함의를 2~3문장 단락으로 서술.

   각 섹션 값은 반드시 **단일 문자열(string)** 이어야 하며, 배열이나 마크다운 불렛(-, *, 1.) 을
   포함해서는 안 됩니다.

2) 기사에서 중요한 영단어 5개를 추출하세요. 너무 쉬운 단어(the, is, and 등)는 제외하세요.
3) 단어 난이도 조건: [{difficulty}] {difficulty_instruction}
4) 각 단어에 대해 한국어 뜻과 영어 예문을 작성하세요. 예문은 가능하면 기사 맥락과 어울리도록 작성하세요.

[출력 형식 - JSON only]
{{
  "summary": {{
    "key_points": "두세 문장이 자연스럽게 이어지는 한 단락 텍스트.",
    "background": "두세 문장이 자연스럽게 이어지는 한 단락 텍스트.",
    "significance": "두세 문장이 자연스럽게 이어지는 한 단락 텍스트."
  }},
  "words": [
    {{"word": "example", "meaning": "예시, 사례", "example": "This is an example sentence."}},
    ...총 5개
  ]
}}
"""

    raw = call_gemini_json(system_prompt, user_prompt, temperature=0.4)
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        st.error("Gemini 응답을 JSON으로 파싱하지 못했습니다.")
        return None

    return {
        "summary": _normalize_summary(parsed.get("summary")),
        "words": parsed.get("words", []),
        "difficulty": difficulty,
    }


def _normalize_summary(summary) -> dict:
    """Gemini 응답의 summary를 항상 {key_points, background, significance} 단락 문자열로 정리."""

    def _to_paragraph(value) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return " ".join(str(v).strip() for v in value if str(v).strip())
        return str(value).strip()

    if isinstance(summary, dict):
        return {
            "key_points": _to_paragraph(summary.get("key_points")),
            "background": _to_paragraph(summary.get("background")),
            "significance": _to_paragraph(summary.get("significance")),
        }
    return {
        "key_points": _to_paragraph(summary),
        "background": "",
        "significance": "",
    }


def format_published_at(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def render_article(idx: int, article: dict) -> None:
    title = article.get("title") or "(제목 없음)"
    source = (article.get("source") or {}).get("name", "")
    published = format_published_at(article.get("publishedAt"))
    description = article.get("description") or ""
    url = article.get("url")

    with st.container(border=True):
        st.markdown(f"### {idx + 1}. {title}")
        meta_parts = [p for p in [source, published] if p]
        if meta_parts:
            st.caption(" · ".join(meta_parts))
        if description:
            st.write(description)
        if url:
            st.markdown(f"[원문 보기 ↗]({url})")

        if st.button("요약 + 단어 학습", key=f"analyze_{idx}", use_container_width=True):
            with st.spinner("AI가 요약하고 단어를 추출하는 중..."):
                result = analyze_article(
                    title=title,
                    description=description,
                    content=article.get("content") or "",
                    difficulty=st.session_state.difficulty,
                )
            if result:
                st.session_state.analysis[idx] = result

        if idx in st.session_state.analysis:
            render_analysis(idx, st.session_state.analysis[idx], article_title=title)


def render_analysis(idx: int, analysis: dict, article_title: str = "") -> None:
    st.divider()

    summary = analysis.get("summary", {})
    if isinstance(summary, dict):
        sections = [
            ("📌 핵심 내용", summary.get("key_points", "")),
            ("🌍 배경 & 맥락", summary.get("background", "")),
            ("💡 의미 & 영향", summary.get("significance", "")),
        ]
        for header, paragraph in sections:
            text = paragraph.strip() if isinstance(paragraph, str) else ""
            if not text:
                continue
            st.markdown(f"#### {header}")
            st.markdown(text)
    else:
        st.markdown("#### 📝 한국어 요약")
        st.markdown(str(summary))

    difficulty = analysis.get("difficulty", st.session_state.difficulty)
    st.markdown(f"#### 📚 학습 영단어  `난이도: {difficulty}`")
    for word_info in analysis.get("words", []):
        word = word_info.get("word", "")
        meaning = word_info.get("meaning", "")
        example = word_info.get("example", "")
        key = (idx, word)
        memorized = key in st.session_state.memorized

        with st.container(border=True):
            head_col, btn_col = st.columns([4, 1])
            with head_col:
                label = f"~~**{word}**~~" if memorized else f"**{word}**"
                st.markdown(f"{label} — {meaning}")
                if example:
                    st.caption(f"예문: {example}")
            with btn_col:
                btn_label = "✅ 외웠어요" if not memorized else "↩︎ 취소"
                if st.button(btn_label, key=f"mem_{idx}_{word}", use_container_width=True):
                    if memorized:
                        st.session_state.memorized.pop(key, None)
                    else:
                        st.session_state.memorized[key] = {
                            "word": word,
                            "meaning": meaning,
                            "article_title": article_title,
                        }
                    st.rerun()


def generate_quiz(word_items: list[dict], n_questions: int = 5) -> list[dict] | None:
    """외운 단어들로 Gemini에게 4지선다 퀴즈를 생성 요청."""
    if len(word_items) < 4:
        return None

    n_questions = min(n_questions, len(word_items))
    selected = random.sample(word_items, n_questions)

    word_list_text = "\n".join(
        f"- {w['word']}: {w['meaning']}" for w in selected
    )
    other_meanings = [w["meaning"] for w in word_items]

    system_prompt = (
        "You are a vocabulary quiz generator for Korean learners of English. "
        "Always respond in valid JSON only."
    )
    user_prompt = f"""다음은 학습자가 '외운 단어'로 표시한 영단어 목록입니다.
각 단어에 대해 4지선다 객관식 퀴즈를 만들어 주세요.

[외운 단어 목록]
{word_list_text}

[참고용 다른 뜻 풀(distractor 아이디어)]
{", ".join(other_meanings)}

[작업 규칙]
1) 위 목록에 있는 단어 {n_questions}개 각각에 대해 문제를 1개씩 만드세요 (총 {n_questions}문제).
2) 질문 형식: "'{{word}}'의 뜻으로 가장 알맞은 것은?"
3) 4개 선택지 중 **정답은 그 단어의 실제 한국어 뜻**입니다.
4) 나머지 3개 오답(distractor)은 다음 규칙으로 만드세요:
   - 같은 품사·비슷한 의미 영역에서 그럴듯하지만 분명히 다른 한국어 뜻을 생성
   - 정답과 글자 수나 느낌이 너무 다르지 않게, 한국어 자연스러운 표현으로
   - 정답과 의미가 거의 같은 동의어는 오답으로 쓰지 말 것 (학습자가 혼동해 억울하지 않도록)
5) 선택지 배열 순서는 섞어서 정답 위치를 무작위로 분산(0~3)시키세요.
6) correct_index는 choices 배열 내 정답의 0-based 인덱스입니다.

[출력 형식 - JSON only]
{{
  "questions": [
    {{
      "word": "영단어",
      "correct_meaning": "실제 한국어 뜻",
      "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],
      "correct_index": 0
    }}
  ]
}}
"""

    raw = call_gemini_json(system_prompt, user_prompt, temperature=0.8)
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        st.error("Gemini 퀴즈 응답을 JSON으로 파싱하지 못했습니다.")
        return None

    questions = parsed.get("questions", [])
    cleaned: list[dict] = []
    for q in questions:
        word = q.get("word", "")
        choices = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        if not word or not isinstance(choices, list) or len(choices) != 4:
            continue
        try:
            correct_index = int(correct_index)
        except (TypeError, ValueError):
            correct_index = 0
        if not 0 <= correct_index < 4:
            correct_index = 0
        cleaned.append({
            "word": word,
            "choices": choices,
            "correct_index": correct_index,
            "correct_meaning": q.get("correct_meaning", choices[correct_index]),
        })
    return cleaned or None


def render_quiz_tab() -> None:
    st.subheader("🎯 외운 단어 퀴즈")
    memorized_items = list(st.session_state.memorized.values())

    if len(memorized_items) < 4:
        st.info(
            f"퀴즈를 만들려면 최소 **4개** 이상의 외운 단어가 필요해요. "
            f"현재 외운 단어: **{len(memorized_items)}개**\n\n"
            f"뉴스 탭에서 단어를 더 외워보세요!"
        )
        return

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.caption(f"현재 외운 단어 **{len(memorized_items)}개** 중 랜덤으로 문제를 출제합니다.")
    with col_b:
        max_n = min(10, len(memorized_items))
        n_questions = st.number_input(
            "문제 수",
            min_value=4,
            max_value=max_n,
            value=min(5, max_n),
            step=1,
            label_visibility="collapsed",
        )

    new_col, reset_col = st.columns(2)
    with new_col:
        if st.button("🎲 새 퀴즈 생성", use_container_width=True, type="primary"):
            with st.spinner("AI가 퀴즈를 생성하는 중..."):
                questions = generate_quiz(memorized_items, n_questions=int(n_questions))
            if questions:
                st.session_state.current_quiz = {
                    "questions": questions,
                    "answers": [None] * len(questions),
                    "submitted": False,
                }
                st.rerun()
    with reset_col:
        if st.session_state.current_quiz and st.button(
            "🗑️ 퀴즈 초기화", use_container_width=True
        ):
            st.session_state.current_quiz = None
            st.rerun()

    quiz = st.session_state.current_quiz
    if not quiz:
        st.caption("위의 **새 퀴즈 생성** 버튼을 눌러 퀴즈를 시작하세요.")
        return

    questions = quiz["questions"]
    submitted = quiz["submitted"]

    st.divider()
    st.markdown(f"### 문제 ({len(questions)}개)")

    for i, q in enumerate(questions):
        with st.container(border=True):
            st.markdown(f"**Q{i + 1}. '{q['word']}'의 뜻으로 가장 알맞은 것은?**")
            key = f"quiz_q_{i}"
            if submitted:
                user_idx = quiz["answers"][i]
                correct_idx = q["correct_index"]
                for j, choice in enumerate(q["choices"]):
                    if j == correct_idx:
                        st.markdown(f"- ✅ **{choice}** (정답)")
                    elif j == user_idx and user_idx != correct_idx:
                        st.markdown(f"- ❌ ~~{choice}~~ (내가 선택)")
                    else:
                        st.markdown(f"- {choice}")
            else:
                choice = st.radio(
                    "보기",
                    options=list(range(4)),
                    format_func=lambda j, q=q: f"{['A','B','C','D'][j]}. {q['choices'][j]}",
                    index=quiz["answers"][i] if quiz["answers"][i] is not None else None,
                    key=key,
                    label_visibility="collapsed",
                )
                quiz["answers"][i] = choice

    if not submitted:
        if st.button("✅ 제출하기", use_container_width=True, type="primary"):
            unanswered = [i + 1 for i, a in enumerate(quiz["answers"]) if a is None]
            if unanswered:
                st.warning(f"아직 답하지 않은 문제가 있어요: {unanswered}")
            else:
                score = 0
                for i, q in enumerate(questions):
                    word = q["word"]
                    stat = st.session_state.quiz_stats.setdefault(
                        word, {"correct": 0, "wrong": 0}
                    )
                    if quiz["answers"][i] == q["correct_index"]:
                        stat["correct"] += 1
                        score += 1
                    else:
                        stat["wrong"] += 1
                quiz["submitted"] = True
                quiz["score"] = score
                st.session_state.quiz_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "score": score,
                    "total": len(questions),
                })
                st.rerun()
    else:
        score = quiz.get("score", 0)
        total = len(questions)
        pct = int(round(score / total * 100)) if total else 0
        st.success(f"🎉 결과: **{score} / {total}** ({pct}%)")


def render_stats_tab() -> None:
    st.subheader("📊 학습 통계")

    memorized_items = list(st.session_state.memorized.values())
    history = st.session_state.quiz_history
    stats = st.session_state.quiz_stats

    quiz_count = len(history)
    total_correct = sum(h["score"] for h in history)
    total_questions = sum(h["total"] for h in history)
    avg_accuracy = (
        int(round(total_correct / total_questions * 100)) if total_questions else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("전체 외운 단어", f"{len(memorized_items)}")
    c2.metric("퀴즈 횟수", f"{quiz_count}")
    c3.metric("평균 정답률", f"{avg_accuracy}%")

    st.divider()
    st.markdown("#### 🧩 취약 단어 TOP 5 (틀린 횟수 기준)")
    weak_sorted = sorted(
        ((w, s["wrong"], s["correct"]) for w, s in stats.items() if s["wrong"] > 0),
        key=lambda x: (-x[1], x[0]),
    )[:5]
    if not weak_sorted:
        st.caption("아직 틀린 단어가 없어요. 퀴즈를 풀어보세요!")
    else:
        for word, wrong, correct in weak_sorted:
            total = wrong + correct
            acc = int(round(correct / total * 100)) if total else 0
            meaning = ""
            for item in memorized_items:
                if item.get("word") == word:
                    meaning = item.get("meaning", "")
                    break
            with st.container(border=True):
                st.markdown(
                    f"**{word}**"
                    + (f" — {meaning}" if meaning else "")
                )
                st.caption(f"❌ 틀림 {wrong}회 · ✅ 맞음 {correct}회 · 정답률 {acc}%")

    st.divider()
    st.markdown("#### 🕒 최근 퀴즈 기록")
    if not history:
        st.caption("아직 푼 퀴즈가 없어요.")
    else:
        for h in reversed(history[-10:]):
            total = h["total"]
            score = h["score"]
            pct = int(round(score / total * 100)) if total else 0
            st.markdown(f"- `{h['timestamp']}`  →  **{score} / {total}** ({pct}%)")


def render_sidebar() -> None:
    with st.sidebar:
        st.header("ℹ️ 사용 안내")
        st.markdown(
            "- 관심 분야(예: `AI`, `sports`, `economy`)를 입력하고 검색하세요.\n"
            "- 단어 난이도를 선택하면 추출되는 어휘 수준이 달라집니다.\n"
            "- 각 뉴스의 **요약 + 단어 학습** 버튼을 누르면 AI가 분석합니다.\n"
            "- 외운 단어는 **외웠어요** 버튼으로 체크할 수 있어요."
        )

        memorized_items = list(st.session_state.memorized.values())
        st.metric("외운 단어 수", len(memorized_items))

        with st.expander(f"📖 외운 단어 목록 ({len(memorized_items)})", expanded=True):
            if not memorized_items:
                st.caption("아직 외운 단어가 없어요. 단어 옆 **외웠어요** 버튼을 눌러보세요.")
            else:
                for item in memorized_items:
                    word = item.get("word", "")
                    meaning = item.get("meaning", "")
                    src = item.get("article_title", "")
                    with st.container(border=True):
                        st.markdown(f"**{word}** — {meaning}")
                        if src:
                            st.caption(f"📰 {src}")

        if st.button("학습 기록 초기화", use_container_width=True):
            st.session_state.memorized = {}
            st.session_state.analysis = {}
            st.session_state.quiz_stats = {}
            st.session_state.quiz_history = []
            st.session_state.current_quiz = None
            st.rerun()


def main() -> None:
    init_session_state()
    inject_custom_css()

    st.markdown(
        """
        <div class="nv-header">
            <div class="nv-brand">
                <span class="nv-logo">📰</span>
                <h1 class="nv-title">NewsVoca</h1>
            </div>
            <p class="nv-subtitle">뉴스로 배우는 영어 단어</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_sidebar()

    tab_news, tab_quiz, tab_stats = st.tabs(["📰 뉴스", "🎯 퀴즈", "📊 통계"])

    with tab_news:
        difficulty = st.selectbox(
            "단어 난이도",
            options=DIFFICULTY_OPTIONS,
            index=DIFFICULTY_OPTIONS.index(st.session_state.difficulty),
        )
        st.session_state.difficulty = difficulty

        st.markdown("**관심 분야 선택**")
        cat_cols = st.columns(len(CATEGORY_OPTIONS))
        clicked_key: str | None = None
        for col, (key, cfg) in zip(cat_cols, CATEGORY_OPTIONS.items()):
            with col:
                is_selected = st.session_state.last_query == cfg["label"]
                if st.button(
                    cfg["label"],
                    key=f"cat_{key}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    clicked_key = key

        if clicked_key:
            cfg = CATEGORY_OPTIONS[clicked_key]
            with st.spinner(f"{cfg['label']} 관련 최신 뉴스를 가져오는 중..."):
                articles = fetch_news(cfg["query"], sources=cfg["sources"])
            st.session_state.articles = articles
            st.session_state.last_query = cfg["label"]
            st.session_state.analysis = {}

        if st.session_state.articles:
            st.markdown(
                f"### '{st.session_state.last_query}' 최신 뉴스 "
                f"{len(st.session_state.articles)}건"
            )
            for idx, article in enumerate(st.session_state.articles):
                render_article(idx, article)
        elif st.session_state.last_query:
            st.info("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
        else:
            st.info("위 입력창에 관심 분야를 입력하고 검색해보세요.")

    with tab_quiz:
        render_quiz_tab()

    with tab_stats:
        render_stats_tab()


if __name__ == "__main__":
    main()
