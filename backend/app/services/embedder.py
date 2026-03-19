# Google text-embedding-004 임베딩 서비스
import asyncio

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

_embedder = GoogleGenerativeAIEmbeddings(
    model=settings.embedding_model,
    google_api_key=settings.google_api_key,
)


async def embed_query(text: str) -> list[float]:
    """단일 텍스트 임베딩 (질문용)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _embedder.embed_query, text)


async def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    청크 리스트에 임베딩을 추가합니다.
    Rate Limit 방어: 20개씩 배치, 1초 딜레이

    Args:
        chunks: chunk_text()의 반환값

    Returns:
        embedding 필드가 추가된 청크 리스트
    """
    loop = asyncio.get_event_loop()
    texts = [c["content"] for c in chunks]
    embeddings: list[list[float]] = []

    for i in range(0, len(texts), 20):
        batch = texts[i : i + 20]
        batch_embeddings = await loop.run_in_executor(
            None, _embedder.embed_documents, batch
        )
        embeddings.extend(batch_embeddings)
        if i + 20 < len(texts):
            await asyncio.sleep(1)  # 15 RPM 무료 티어 보호

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb
    return chunks
