# 텍스트 청킹 서비스
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings


def chunk_text(full_text: str, document_id: str) -> list[dict]:
    """
    전체 텍스트를 청크로 분할합니다.

    Args:
        full_text: 파싱된 전체 텍스트
        document_id: 문서 ID (메타데이터 태깅용)

    Returns:
        청크 딕셔너리 리스트
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_text(full_text)
    return [
        {
            "document_id": document_id,
            "chunk_index": i,
            "content": chunk,
            "metadata": {"chunk_index": i, "total_chunks": len(chunks)},
        }
        for i, chunk in enumerate(chunks)
    ]
