## FinSight AI

금융 리포트 PDF를 업로드하면 기업 분석과 질의응답을 제공하는 AI 서비스

### Overview

FinSight AI는 증권사 리포트, DART 공시 등 **비정형 금융 PDF**를 분석하여
핵심 투자 정보를 자동으로 구조화하고, 질문 기반으로 빠르게 탐색할 수 있도록 도와줍니다.

**RAG (검색 기반)** vs **비RAG (전체 컨텍스트)** 방식을 동시에 제공하여
AI 응답 방식의 차이를 직접 비교할 수 있습니다.

### Tech Stack

* **Frontend**: React, Vite, Axios
* **Backend**: FastAPI, LangChain
* **AI(LLM)**: Gemini(2.0 Flash), Groq API
* **Database**: Supabase (PostgreSQL + pgvector)
* **Infra**: Docker, GCP Cloud Run, Vercel