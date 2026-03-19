# RAG 파이프라인: 질문 임베딩 → pgvector 검색 → LLM 답변 + 출처
import time
from pathlib import Path
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.repository import supabase_repo
from app.services.embedder import embed_query


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


async def run_rag_query(question: str, document_id: str) -> dict:
    start = time.time()

    query_embedding = await embed_query(question)
    chunks = await supabase_repo.similarity_search(
        query_embedding, document_id, k=settings.top_k_chunks
    )

    context_parts = [
        f"[청크 {i + 1}] {chunk['content']}"
        for i, chunk in enumerate(chunks)
    ]
    context = "\n\n".join(context_parts) if context_parts else "관련 청크를 찾지 못했습니다."

    prompt_template = _load_prompt("qa_rag")
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = _get_llm()
    chain = prompt | llm
    response = await chain.ainvoke({"context": context, "question": question})

    latency_ms = int((time.time() - start) * 1000)
    return {
        "answer": response.content,
        "sources": [
            {
                "index": i + 1,
                "content": c["content"],
                "similarity": c["similarity"],
            }
            for i, c in enumerate(chunks)
        ],
        "mode": "rag",
        "latency_ms": latency_ms,
        "model": _get_model_name(),
    }
