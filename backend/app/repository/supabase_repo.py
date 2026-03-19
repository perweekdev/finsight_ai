# Supabase DB 접근 레이어 — 모든 DB I/O는 이 모듈에서만
import asyncio
from typing import Optional

from supabase import create_client, Client

from app.core.config import settings

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client


async def save_document(filename: str, full_text: str, page_count: int) -> str:
    """문서 메타데이터 + 전문 저장, document_id 반환"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _insert() -> str:
        result = (
            client.table("documents")
            .insert(
                {
                    "filename": filename,
                    "full_text": full_text,
                    "pages": page_count,
                }
            )
            .execute()
        )
        return result.data[0]["id"]

    return await loop.run_in_executor(None, _insert)


async def save_chunks(chunks: list[dict]) -> None:
    """청크 + 임베딩 배치 저장 (50개씩)"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _bulk_insert() -> None:
        for i in range(0, len(chunks), 50):
            client.table("chunks").insert(chunks[i : i + 50]).execute()

    await loop.run_in_executor(None, _bulk_insert)


async def similarity_search(
    query_embedding: list[float],
    document_id: str,
    k: int = 5,
) -> list[dict]:
    """코사인 유사도 기반 청크 검색 (match_chunks RPC)"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _search() -> list[dict]:
        result = client.rpc(
            "match_chunks",
            {
                "query_embedding": query_embedding,
                "match_count": k,
                "match_document_id": document_id,
            },
        ).execute()
        return result.data

    return await loop.run_in_executor(None, _search)


async def get_document(document_id: str) -> dict:
    """document_id로 문서 조회"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _get() -> dict:
        result = (
            client.table("documents")
            .select("*")
            .eq("id", document_id)
            .single()
            .execute()
        )
        return result.data

    return await loop.run_in_executor(None, _get)


async def update_company_name(document_id: str, company_name: str) -> None:
    """분석 후 기업명 업데이트"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _update() -> None:
        client.table("documents").update({"company": company_name}).eq(
            "id", document_id
        ).execute()

    await loop.run_in_executor(None, _update)


async def log_query(
    document_id: str,
    mode: str,
    question: str,
    answer: str,
    latency_ms: int,
    model_used: str,
) -> None:
    """RAG/비RAG 쿼리 성능 로그 저장"""
    loop = asyncio.get_running_loop()
    client = _get_client()

    def _log() -> None:
        client.table("query_logs").insert(
            {
                "document_id": document_id,
                "mode": mode,
                "question": question,
                "answer": answer,
                "latency_ms": latency_ms,
                "model_used": model_used,
            }
        ).execute()

    await loop.run_in_executor(None, _log)
