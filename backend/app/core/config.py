from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    google_api_key: str
    groq_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    embedding_model: str = "models/gemini-embedding-001"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_chunks: int = 5
    max_norag_chars: int = 120000

    class Config:
        env_file = ".env"


settings = Settings()
