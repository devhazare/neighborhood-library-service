from app.ai.providers.base import AIProvider

class MockAIProvider(AIProvider):
    def enrich_book(self, title: str, author: str, category: str, text: str) -> dict:
        return {
            "summary": f"'{title}' by {author} is an engaging book that explores compelling themes and ideas.",
            "genre": category or "General Fiction",
            "tags": ["recommended", "popular", category.lower() if category else "fiction"],
            "reading_level": "Adult",
            "recommended_for": "Readers who enjoy thoughtful narratives and well-crafted stories.",
        }

    def explain_recommendation(self, member_interests: str, book_title: str, book_tags: str) -> str:
        return (
            f"Based on your reading history, '{book_title}' aligns well with your interests. "
            f"You'll likely enjoy this book given its themes that match your preferences."
        )

    def generate_reminder(self, member_name: str, book_title: str, due_date: str, overdue_days: int) -> str:
        if overdue_days > 0:
            return (
                f"Dear {member_name}, the book '{book_title}' was due on {due_date} and is now "
                f"{overdue_days} day(s) overdue. Please return it at your earliest convenience. Thank you!"
            )
        return (
            f"Dear {member_name}, friendly reminder that '{book_title}' is due on {due_date}. "
            f"Please return it on time. Thank you!"
        )

    def extract_pdf_metadata(self, text: str) -> dict:
        # Mock implementation - returns sample data for testing
        return {
            "title": "Sample Book Title",
            "author": "Sample Author",
            "isbn": None,
            "publisher": None,
            "published_year": None,
            "category": "General",
        }

