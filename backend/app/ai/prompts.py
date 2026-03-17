BOOK_ENRICHMENT_PROMPT = """You are a librarian assistant. Given the following book information, provide an enrichment in JSON format.

Book Title: {title}
Author: {author}
Category: {category}
Additional Text: {text}

Respond ONLY with valid JSON in this exact format:
{{
  "summary": "A 2-3 sentence summary of the book",
  "genre": "Primary genre",
  "tags": ["tag1", "tag2", "tag3"],
  "reading_level": "Elementary/Middle School/High School/Adult",
  "recommended_for": "Description of who would enjoy this book"
}}"""

RECOMMENDATION_EXPLANATION_PROMPT = """You are a helpful librarian. A member with the following interests: {member_interests}
has been recommended the book "{book_title}" with tags: {book_tags}.

Write a 1-2 sentence personalized explanation of why this book is recommended for them."""

OVERDUE_REMINDER_PROMPT = """Write a polite, friendly overdue book reminder for a library member.

Member Name: {member_name}
Book Title: {book_title}
Due Date: {due_date}
Days Overdue: {overdue_days}

Keep it under 3 sentences. Be friendly and encouraging."""

PDF_METADATA_EXTRACTION_PROMPT = """You are a librarian assistant. Extract book metadata from the following PDF text (from the first few pages of a book).

PDF Text:
{text}

Respond ONLY with valid JSON in this exact format (use null for fields you cannot determine):
{{
  "title": "The book title",
  "author": "Author name(s)",
  "isbn": "ISBN number if found",
  "publisher": "Publisher name if found",
  "published_year": 2024,
  "category": "Primary category/genre"
}}

Important: Extract accurate information only. Use null for any field you cannot confidently determine from the text."""

