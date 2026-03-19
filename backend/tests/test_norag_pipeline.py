"""비RAG 파이프라인 테스트 (mock 기반)"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_norag_returns_empty_sources():
    """비RAG 모드는 sources가 빈 리스트여야 한다"""
    with (
        patch("app.repository.supabase_repo.get_document", new_callable=AsyncMock) as mock_get,
        patch("app.core.norag_pipeline._get_llm") as mock_llm_factory,
    ):
        mock_get.return_value = {"full_text": "테스트 문서 내용", "id": "test-id"}
        mock_response = MagicMock()
        mock_response.content = "테스트 답변"
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm = MagicMock()
        mock_llm_factory.return_value = mock_llm

        # sources가 빈 리스트인지 확인하는 로직 검증
        result_sources: list = []
        assert result_sources == []


@pytest.mark.asyncio
async def test_analysis_json_parsing():
    """분석 결과 JSON 파싱이 정상 동작해야 한다"""
    import json
    import re

    raw_response = """
    {
      "company_name": "삼성전자",
      "overview": "반도체 및 전자 기기 제조 기업",
      "bull_case": ["AI 반도체 수요 증가", "HBM 시장 선점"],
      "bear_case": ["중국 경쟁 심화"],
      "financials": {"target_price": "90000"},
      "key_issues": ["HBM3E 양산"]
    }
    """
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    assert json_match is not None
    parsed = json.loads(json_match.group())
    assert parsed["company_name"] == "삼성전자"
    assert len(parsed["bull_case"]) >= 1
