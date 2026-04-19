# 📰 Daily News + English Word Learner

관심 분야의 최신 뉴스를 한국어로 요약해주고, 그 뉴스에서 중요한 영단어를 추출해 학습할 수 있는 Streamlit 웹앱입니다.

## ✨ 주요 기능

- 관심 분야 키워드 입력 → NewsAPI로 최신 뉴스 5개 검색
- 각 뉴스마다 OpenAI(`gpt-4o-mini`)로 한국어 3줄 요약
- 핵심 영단어 5개를 뜻 + 예문과 함께 추출
- 단어별 "외웠어요" 체크 기능

## 🛠️ 기술 스택

- Python 3.10+
- Streamlit
- OpenAI API (`gpt-4o-mini`)
- NewsAPI (https://newsapi.org)
- python-dotenv

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 발급

- **OpenAI API Key**: https://platform.openai.com/api-keys
- **NewsAPI Key**: https://newsapi.org/register

### 3. `.env` 파일 설정

프로젝트 루트의 `.env` 파일을 열고 API 키를 입력하세요.

```env
OPENAI_API_KEY=sk-...
NEWS_API_KEY=...
```

> ⚠️ `.env` 파일은 `.gitignore`에 포함되어 있어 git에 커밋되지 않습니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 로 접속하세요.

## 📁 파일 구조

```
app_pj/
├── app.py              # 메인 Streamlit 앱
├── requirements.txt    # 패키지 목록
├── .env                # API 키 (git 제외)
├── .gitignore
└── README.md
```
