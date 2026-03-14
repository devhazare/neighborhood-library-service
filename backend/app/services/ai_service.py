from sqlalchemy.orm import Session
from app.core.config import Settings
from app.ai.providers.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.repositories import ai_repository
from app.core.logging import get_logger

logger = get_logger(__name__)

class AIService:
    def __init__(self, settings: Settings):
        if settings.OPENAI_API_KEY:
            from app.ai.providers.openai_provider import OpenAICompatibleProvider
            self.provider: AIProvider = OpenAICompatibleProvider(settings.OPENAI_API_KEY)
        else:
            self.provider = MockAIProvider()

    def enrich_book(self, db: Session, book_id: str, title: str, author: str, category: str, text: str) -> dict:
        result = self.provider.enrich_book(title, author, category, text)
        ai_repository.log_enrichment(db, "book", book_id, "enrich_book", text[:500] if text else "", result)
        return result

    def explain_recommendation(self, db: Session, book_id: str, member_interests: str, book_title: str, book_tags: str) -> str:
        result = self.provider.explain_recommendation(member_interests, book_title, book_tags)
        ai_repository.log_enrichment(db, "book", book_id, "recommendation", member_interests, {"explanation": result})
        return result

    def generate_reminder(self, db: Session, borrow_id: str, member_name: str, book_title: str, due_date: str, overdue_days: int) -> str:
        result = self.provider.generate_reminder(member_name, book_title, due_date, overdue_days)
        ai_repository.log_enrichment(db, "borrow", borrow_id, "reminder", f"{member_name}/{book_title}", {"reminder": result})
        return result
