import json
from app.ai.providers.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.prompts import BOOK_ENRICHMENT_PROMPT, RECOMMENDATION_EXPLANATION_PROMPT, OVERDUE_REMINDER_PROMPT
from app.core.logging import get_logger

logger = get_logger(__name__)

class OpenAICompatibleProvider(AIProvider):
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.mock = MockAIProvider()
        self.model = "gpt-3.5-turbo"

    def enrich_book(self, title: str, author: str, category: str, text: str) -> dict:
        try:
            prompt = BOOK_ENRICHMENT_PROMPT.format(title=title, author=author, category=category or "", text=text or "")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI enrich_book failed, using mock: {e}")
            return self.mock.enrich_book(title, author, category, text)

    def explain_recommendation(self, member_interests: str, book_title: str, book_tags: str) -> str:
        try:
            prompt = RECOMMENDATION_EXPLANATION_PROMPT.format(
                member_interests=member_interests, book_title=book_title, book_tags=book_tags
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI explain_recommendation failed, using mock: {e}")
            return self.mock.explain_recommendation(member_interests, book_title, book_tags)

    def generate_reminder(self, member_name: str, book_title: str, due_date: str, overdue_days: int) -> str:
        try:
            prompt = OVERDUE_REMINDER_PROMPT.format(
                member_name=member_name, book_title=book_title, due_date=due_date, overdue_days=overdue_days
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI generate_reminder failed, using mock: {e}")
            return self.mock.generate_reminder(member_name, book_title, due_date, overdue_days)
