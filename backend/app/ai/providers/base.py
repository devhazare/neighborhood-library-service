from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def enrich_book(self, title: str, author: str, category: str, text: str) -> dict:
        pass

    @abstractmethod
    def explain_recommendation(self, member_interests: str, book_title: str, book_tags: str) -> str:
        pass

    @abstractmethod
    def generate_reminder(self, member_name: str, book_title: str, due_date: str, overdue_days: int) -> str:
        pass

    @abstractmethod
    def extract_pdf_metadata(self, text: str) -> dict:
        pass

