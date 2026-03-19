import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.repository import supabase_repo
from app.services.chunker import chunk_text
from app.services.embedder import embed_chunks
from app.services.pdf_parser import parse_pdf

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parsed = parse_pdf(tmp_path)
        doc_id = await supabase_repo.save_document(
            file.filename, parsed["full_text"], parsed["page_count"]
        )
        chunks = chunk_text(parsed["full_text"], doc_id)
        chunks_with_embeddings = await embed_chunks(chunks)
        await supabase_repo.save_chunks(chunks_with_embeddings)

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "pages": parsed["page_count"],
            "chunks": len(chunks),
        }
    finally:
        os.unlink(tmp_path)
