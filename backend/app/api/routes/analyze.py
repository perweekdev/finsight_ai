from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.norag_pipeline import run_analysis
from app.repository import supabase_repo

router = APIRouter()


class AnalyzeRequest(BaseModel):
    document_id: str


@router.post("/analyze")
async def analyze_document(req: AnalyzeRequest) -> dict:
    doc = await supabase_repo.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    result = await run_analysis(req.document_id)

    if result["analysis"].get("company_name"):
        await supabase_repo.update_company_name(
            req.document_id, result["analysis"]["company_name"]
        )

    return result
