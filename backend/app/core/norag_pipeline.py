# 비RAG 파이프라인: 문서 전문 → LLM 답변 / 구조화 분석
import json
import re
import time
from pathlib import Path
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.repository import supabase_repo


def _load_prompt(name: str) -> str:
    path = Path(__file__).parent.parent.parent / "prompts" / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _get_llm() -> Any:
    """Groq 우선, 실패 시 Gemini 폴백"""
    if settings.groq_api_key:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
            temperature=0.1,
        )
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
    )


def _get_model_name() -> str:
    if settings.groq_api_key:
        return "llama-3.1-8b-instant"
    return settings.gemini_model


def _max_chars() -> int:
    """LLM 종류에 따른 최대 문서 길이 반환"""
    return settings.max_groq_chars if settings.groq_api_key else settings.max_norag_chars


async def run_norag_query(question: str, document_id: str) -> dict:
    start = time.time()
    doc = await supabase_repo.get_document(document_id)
    truncated = doc["full_text"][: _max_chars()]

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
        "model": _get_model_name(),
    }


async def run_analysis(document_id: str) -> dict:
    start = time.time()
    doc = await supabase_repo.get_document(document_id)
    truncated = doc["full_text"][: _max_chars()]

    prompt_template = _load_prompt("analyze")
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = _get_llm()
    chain = prompt | llm
    response = await chain.ainvoke({"document": truncated})

    # JSON 추출 (```json ... ``` 또는 순수 { ... })
    text = response.content
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not json_match:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        analysis = json.loads(json_match.group(1) if json_match and json_match.lastindex else json_match.group()) if json_match else {}
    except (json.JSONDecodeError, AttributeError):
        analysis = {"overview": text}

    latency_ms = int((time.time() - start) * 1000)
    return {"analysis": analysis, "latency_ms": latency_ms}
