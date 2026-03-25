# Duplicate Borrow Protection - Quick Reference

## ✅ YES, Duplicate Borrowing is Prevented!

Your system has **robust protection** to prevent the same member from borrowing the same book multiple times simultaneously.

---

## How It Works

### Scenario 1: Member Tries to Borrow Same Book Twice ❌

```
Alice borrows "Harry Potter" → ✅ SUCCESS (status: borrowed)
Alice tries to borrow "Harry Potter" again → ❌ BLOCKED

Error: "Member already has this book borrowed. Please return it before borrowing again."
```

### Scenario 2: Member Returns and Borrows Again ✅

```
Alice borrows "Harry Potter" → ✅ SUCCESS (status: borrowed)
Alice returns "Harry Potter" → ✅ SUCCESS (status: returned)
Alice borrows "Harry Potter" again → ✅ SUCCESS (new transaction, status: borrowed)
```

### Scenario 3: Different Members, Same Book ✅

```
Alice borrows "Harry Potter" (copy 1) → ✅ SUCCESS
Bob borrows "Harry Potter" (copy 2) → ✅ SUCCESS

Both have different copies of the same book.
```

### Scenario 4: Overdue Book Still Blocks ❌

```
Alice borrows "Harry Potter" → ✅ SUCCESS (status: borrowed)
[Time passes, book becomes overdue] (status: overdue)
Alice tries to borrow "Harry Potter" again → ❌ BLOCKED

Error: "Member already has this book borrowed. Please return it before borrowing again."
```

---

## Implementation Details

### 🛡️ Layer 1: Application Check (Service Layer)

**File:** `backend/app/services/borrow_service.py` (lines 38-41)

```python
def borrow_book(db: Session, book_id: str, member_id: str):
    # ... other validation ...
    
    # Check for duplicate borrowing
    existing_borrow = borrow_repository.get_active_borrow_by_member_and_book(
        db, member_id, book_id
    )
    if existing_borrow:
        raise BusinessRuleError(
            "Member already has this book borrowed. "
            "Please return it before borrowing again."
        )
    
    # ... proceed with borrowing ...
```

**What it checks:**
- Queries database for any active borrow (status = `borrowed` OR `overdue`)
- Returns user-friendly error message
- Fails fast before any database writes

---

### 🔒 Layer 2: Database Constraint (Model Layer)

**File:** `backend/app/models/borrow_transaction.py` (lines 37-42)

```python
__table_args__ = (
    # ... other indexes ...
    
    # Partial unique index for preventing duplicate active borrowings
    sa.Index(
        "ix_unique_active_borrow_orm",
        "member_id", "book_id",
        unique=True,
        postgresql_where=sa.text("status IN ('borrowed', 'overdue')")
    ),
)
```

**What it does:**
- Creates a **unique composite index** on `(member_id, book_id)`
- **Only applies when** `status IN ('borrowed', 'overdue')`
- Database-level enforcement (cannot be bypassed)
- After book is returned (status = 'returned'), index no longer applies

---

## API Response Examples

### ❌ Duplicate Borrow Attempt

**Request:**
```bash
POST /api/v1/borrow/borrow
Content-Type: application/json

{
  "book_id": "abc-123",
  "member_id": "def-456"
}
```

**Response:** `400 Bad Request`
```json
{
  "detail": "Member already has this book borrowed. Please return it before borrowing again.",
  "type": "business_rule_error"
}
```

### ✅ Successful Borrow After Return

**Request 1: Borrow**
```bash
POST /api/v1/borrow/borrow
{ "book_id": "abc-123", "member_id": "def-456" }
```
**Response:** `201 Created` ✅

**Request 2: Return**
```bash
POST /api/v1/borrow/return
{ "borrow_id": "xyz-789" }
```
**Response:** `200 OK` ✅

**Request 3: Borrow Again**
```bash
POST /api/v1/borrow/borrow
{ "book_id": "abc-123", "member_id": "def-456" }
```
**Response:** `201 Created` ✅ (New transaction created)

---

## Testing

### Run the Tests

```bash
cd backend

# Run all duplicate protection tests
pytest tests/test_duplicate_borrow_protection.py -v

# Run specific test
pytest tests/test_duplicate_borrow_protection.py::TestDuplicateBorrowProtection::test_cannot_borrow_same_book_twice -v
```

### Test Coverage

✅ **test_cannot_borrow_same_book_twice** - Verifies duplicate is blocked  
✅ **test_can_borrow_after_return** - Verifies reborrowing works  
✅ **test_different_members_can_borrow_same_book** - Multiple members OK  
✅ **test_overdue_book_still_blocks_duplicate** - Overdue status also blocks  

---

## Database Query Example

### Check for Active Borrow

```sql
SELECT * 
FROM borrow_transactions 
WHERE member_id = 'def-456' 
  AND book_id = 'abc-123' 
  AND status IN ('borrowed', 'overdue');
```

If this returns **any row**, the member already has the book and cannot borrow again.

### View the Unique Index

```sql
-- PostgreSQL
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'borrow_transactions' 
  AND indexname = 'ix_unique_active_borrow_orm';
```

---

## Related Business Rules

The duplicate protection is part of a comprehensive set of borrowing rules:

1. ✅ **No duplicate active borrows** (same member + same book)
2. ✅ **Maximum active borrowings** (default: 5 books per member)
3. ✅ **Outstanding fines check** (must clear fines before borrowing)
4. ✅ **Member status check** (must be 'active')
5. ✅ **Book availability check** (must have available copies)

All configured in `backend/app/core/config.py`:
```python
MAX_ACTIVE_BORROWINGS: int = 5
MAX_BORROW_DAYS: int = 14
FINE_PER_DAY: float = 0.50
MAX_FINE_AMOUNT: float = 25.00
```

---

## Summary

✅ **Duplicate borrowing is fully prevented**  
✅ **Two layers of protection** (application + database)  
✅ **Members can reborrow after returning**  
✅ **Different members can borrow different copies**  
✅ **Overdue books still block duplicates**  
✅ **Comprehensive test coverage**  

**Your system is secure!** 🔒

