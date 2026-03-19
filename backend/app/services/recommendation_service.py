from sqlalchemy.orm import Session
from app.repositories import borrow_repository, book_repository, member_repository
from app.core.exceptions import NotFoundError
from app.schemas.ai import RecommendationItem
from app.schemas.book import BookResponse
from typing import List, Set, Dict
from app.models.book import Book

def recommend_books(db: Session, member_id: str, ai_service) -> List[RecommendationItem]:
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")

    history = borrow_repository.get_by_member(db, member_id)
    borrowed_book_ids: Set[str] = {txn.book_id for txn in history}

    # Fetch all borrowed books in a single query to avoid N+1
    borrowed_books: List[Book] = []
    if borrowed_book_ids:
        borrowed_books = db.query(Book).filter(Book.id.in_(borrowed_book_ids)).all()

    # Build lookup for borrowed books
    borrowed_books_map: Dict[str, Book] = {b.id: b for b in borrowed_books}

    categories: List[str] = []
    tags_list: List[str] = []
    authors: List[str] = []

    for txn in history:
        book = borrowed_books_map.get(txn.book_id)
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
    
    # Get all available books in a single query
    all_books = book_repository.list_all(db, 0, 200)
    candidates = [b for b in all_books if b.id not in borrowed_book_ids and b.available_copies > 0]
    
    # Convert to sets for O(1) lookup
    category_set = set(categories)
    author_set = set(authors)
    tag_set = set(tags_list)

    def score_book(book: Book) -> int:
        score = 0
        if book.category in category_set:
            score += 3
        if book.author in author_set:
            score += 2
        if book.tags and isinstance(book.tags, list):
            for tag in book.tags:
                if tag in tag_set:
                    score += 1
        return score
    
    candidates.sort(key=score_book, reverse=True)
    top = candidates[:10]
    
    results: List[RecommendationItem] = []
    for book in top:
        book_tags_str = ", ".join(book.tags) if book.tags and isinstance(book.tags, list) else ""
        reason = ai_service.explain_recommendation(db, book.id, member_interests, book.title, book_tags_str)
        results.append(RecommendationItem(book=BookResponse.model_validate(book), reason=reason))
    
    return results
