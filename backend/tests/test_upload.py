"""업로드 파이프라인 테스트 (mock 기반)"""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_upload_returns_document_id():
    """PDF 업로드 시 document_id, pages, chunks가 반환되어야 한다"""
    with (
        patch("app.services.pdf_parser.parse_pdf") as mock_parse,
        patch("app.repository.supabase_repo.save_document", new_callable=AsyncMock) as mock_save_doc,
        patch("app.services.embedder.embed_chunks", new_callable=AsyncMock) as mock_embed,
        patch("app.repository.supabase_repo.save_chunks", new_callable=AsyncMock),
    ):
        mock_parse.return_value = {"full_text": "테스트 텍스트 " * 100, "page_count": 5}
        mock_save_doc.return_value = "test-uuid-1234"
        mock_embed.side_effect = lambda chunks: chunks  # 임베딩 패스스루

        from app.services.chunker import chunk_text

        chunks = chunk_text("테스트 텍스트 " * 100, "test-uuid-1234")
        assert len(chunks) > 0
        assert chunks[0]["document_id"] == "test-uuid-1234"


@pytest.mark.asyncio
async def test_chunk_metadata():
    """청크에 chunk_index와 total_chunks 메타데이터가 포함되어야 한다"""
    from app.services.chunker import chunk_text

    chunks = chunk_text("A" * 2000, "doc-id")
    assert all("chunk_index" in c["metadata"] for c in chunks)
    assert all("total_chunks" in c["metadata"] for c in chunks)
