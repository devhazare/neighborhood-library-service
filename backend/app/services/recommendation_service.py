from sqlalchemy.orm import Session
from app.repositories import borrow_repository, book_repository, member_repository
from app.core.exceptions import NotFoundError
from app.schemas.ai import RecommendationItem
from app.schemas.book import BookResponse
from typing import List

def recommend_books(db: Session, member_id: str, ai_service) -> List[RecommendationItem]:
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    history = borrow_repository.get_by_member(db, member_id)
    borrowed_book_ids = {txn.book_id for txn in history}
    
    categories = []
    tags_list = []
    authors = []
    for txn in history:
        book = book_repository.get_by_id(db, txn.book_id)
        if book:
            if book.category:
                categories.append(book.category)
            if book.tags and isinstance(book.tags, list):
                tags_list.extend(book.tags)
            if book.author:
                authors.append(book.author)
    
    member_interests = ", ".join(set(categories + tags_list[:5]))
    if not member_interests:
        member_interests = "general fiction"
    
    all_books = book_repository.list_all(db, 0, 200)
    candidates = [b for b in all_books if b.id not in borrowed_book_ids and b.available_copies > 0]
    
    def score_book(book):
        score = 0
        if book.category in categories:
            score += 3
        if book.author in authors:
            score += 2
        if book.tags and isinstance(book.tags, list):
            for tag in book.tags:
                if tag in tags_list:
                    score += 1
        return score
    
    candidates.sort(key=score_book, reverse=True)
    top = candidates[:10]
    
    results = []
    for book in top:
        book_tags_str = ", ".join(book.tags) if book.tags and isinstance(book.tags, list) else ""
        reason = ai_service.explain_recommendation(db, book.id, member_interests, book.title, book_tags_str)
        results.append(RecommendationItem(book=BookResponse.model_validate(book), reason=reason))
    
    return results
