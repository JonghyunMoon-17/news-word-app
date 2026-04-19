"""
Daily News + English Word Learner
- NewsAPI로 관심 분야 뉴스를 가져오고
- OpenAI(gpt-4o-mini)로 구조화된 한국어 요약 + 난이도별 핵심 영단어 5개 추출
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
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_API_URL = "https://newsapi.org/v2/everything"
OPENAI_MODEL = "gpt-4o-mini"


st.set_page_config(
    page_title="Daily News + English Word Learner",
    page_icon="📰",
    layout="centered",
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
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)

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

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
    except Exception as exc:
        st.error(f"OpenAI API 호출 중 오류: {exc}")
        return None

    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        st.error("OpenAI 응답을 JSON으로 파싱하지 못했습니다.")
        return None

    return {
        "summary": _normalize_summary(parsed.get("summary")),
        "words": parsed.get("words", []),
        "difficulty": difficulty,
    }


def _normalize_summary(summary) -> dict:
    """OpenAI 응답의 summary를 항상 {key_points, background, significance} 단락 문자열로 정리."""

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
                    st.markdown(f"**{word}** — {meaning}")
                    if src:
                        st.caption(f"📰 {src}")
                    st.markdown("---")

        if st.button("학습 기록 초기화", use_container_width=True):
            st.session_state.memorized = {}
            st.session_state.analysis = {}
            st.rerun()


def main() -> None:
    init_session_state()

    st.title("📰 Daily News + English Word Learner")
    st.caption("관심 분야의 최신 뉴스로 영어 단어까지 함께 학습해보세요.")

    render_sidebar()

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
            if st.button(cfg["label"], key=f"cat_{key}", use_container_width=True):
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


if __name__ == "__main__":
    main()
