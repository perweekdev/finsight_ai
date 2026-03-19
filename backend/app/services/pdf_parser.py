# docling 기반 PDF 파싱 서비스
# docling: IBM 오픈소스, 레이아웃/표/이미지 구조를 마크다운으로 출력
# TODO: Day 1에 구현
from pathlib import Path


def parse_pdf(pdf_path: str) -> dict:
    """
    PDF를 파싱하여 마크다운 텍스트와 페이지 수를 반환합니다.

    Args:
        pdf_path: PDF 파일 경로

    Returns:
        {
            "full_text": str,   # 마크다운 형식 전체 텍스트
            "page_count": int,
        }
    """
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    full_text = result.document.export_to_markdown()

    # 페이지 수 추출 (docling result에서 가져오거나 추정)
    try:
        page_count = len(result.document.pages)
    except Exception:
        page_count = full_text.count("<!-- page") or 1

    return {
        "full_text": full_text,
        "page_count": page_count,
    }
