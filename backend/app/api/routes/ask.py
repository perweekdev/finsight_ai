from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.norag_pipeline import run_norag_query
from app.core.rag_pipeline import run_rag_query
from app.repository import supabase_repo

router = APIRouter()


class AskRequest(BaseModel):
    document_id: str
    question: str
    mode: str = "rag"  # "rag" | "norag"


@router.post("/ask")
async def ask_question(req: AskRequest) -> dict:
    if req.mode not in ("rag", "norag"):
        raise HTTPException(status_code=400, detail="mode는 'rag' 또는 'norag'이어야 합니다.")

    doc = await supabase_repo.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    if req.mode == "rag":
        result = await run_rag_query(req.question, req.document_id)
    else:
        result = await run_norag_query(req.question, req.document_id)

    await supabase_repo.log_query(
        document_id=req.document_id,
        mode=req.mode,
        question=req.question,
        answer=result["answer"],
        latency_ms=result["latency_ms"],
        model_used=result["model"],
    )
    return result
