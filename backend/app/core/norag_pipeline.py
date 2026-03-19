# 비RAG 파이프라인: 문서 전문 → Gemini 답변 / 구조화 분석
# TODO: Day 2에 구현
import json
import re
import time
from pathlib import Path
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.repository import supabase_repo


def _load_prompt(name: str) -> str:
    path = Path(__file__).parent.parent.parent / "prompts" / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _get_llm() -> Any:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
    )


async def run_norag_query(question: str, document_id: str) -> dict:
    start = time.time()
    doc = await supabase_repo.get_document(document_id)
    truncated = doc["full_text"][: settings.max_norag_chars]

    prompt_template = _load_prompt("qa_norag")
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = _get_llm()
    chain = prompt | llm
    response = await chain.ainvoke({"document": truncated, "question": question})

    latency_ms = int((time.time() - start) * 1000)
    return {
        "answer": response.content,
        "sources": [],
        "mode": "norag",
        "latency_ms": latency_ms,
        "model": settings.gemini_model,
    }


async def run_analysis(document_id: str) -> dict:
    start = time.time()
    doc = await supabase_repo.get_document(document_id)
    truncated = doc["full_text"][: settings.max_norag_chars]

    prompt_template = _load_prompt("analyze")
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = _get_llm()
    chain = prompt | llm
    response = await chain.ainvoke({"document": truncated})

    json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
    try:
        analysis = json.loads(json_match.group()) if json_match else {}
    except json.JSONDecodeError:
        analysis = {"overview": response.content}

    latency_ms = int((time.time() - start) * 1000)
    return {"analysis": analysis, "latency_ms": latency_ms}
