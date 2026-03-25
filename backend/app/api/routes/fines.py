"""
Fines Management Router

This module provides endpoints for managing library fines including:
- Viewing unpaid fines
- Paying fines
- Getting fines summary for members
- Fines statistics and reports
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.exceptions import NotFoundError, ValidationError, BusinessRuleError
from app.models.user import User
from app.schemas.borrow import (
    BorrowResponse,
    BorrowListResponse,
    PayFineRequest,
    FinesSummary,
)
from app.services import borrow_service

router = APIRouter(prefix="/api/v1/fines", tags=["fines"])


@router.get("", response_model=BorrowListResponse)
def list_all_unpaid_fines(
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum fine amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum fine amount"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all transactions with unpaid fines.

    Supports filtering by member and fine amount range.
    """
    txns = borrow_service.get_unpaid_fines(db, member_id)

    # Apply amount filtering if specified
    if min_amount is not None or max_amount is not None:
        filtered_txns = []
        for txn in txns:
            fine_amount = txn.fine_amount or Decimal("0")
            if min_amount is not None and fine_amount < Decimal(str(min_amount)):
                continue
            if max_amount is not None and fine_amount > Decimal(str(max_amount)):
                continue
            filtered_txns.append(txn)
        txns = filtered_txns

    total = len(txns)
    txns = txns[skip:skip + limit]

    enriched = borrow_service.enrich_transactions(db, txns)
    items = [BorrowResponse(**data) for data in enriched]
    return BorrowListResponse(items=items, total=total)


@router.get("/summary", response_model=dict)
def get_fines_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get overall fines summary statistics.

    Returns total unpaid fines, count of transactions with fines, etc.
    """
    all_unpaid = borrow_service.get_unpaid_fines(db)

    total_amount = sum((txn.fine_amount or Decimal("0")) for txn in all_unpaid)
    transaction_count = len(all_unpaid)

    # Group by member
    member_fines = {}
    for txn in all_unpaid:
        member_id = txn.member_id
        if member_id not in member_fines:
            member_fines[member_id] = Decimal("0")
        member_fines[member_id] += txn.fine_amount or Decimal("0")

    return {
        "total_unpaid_amount": float(total_amount),
        "total_transactions_with_fines": transaction_count,
        "members_with_unpaid_fines": len(member_fines),
        "average_fine_amount": float(total_amount / transaction_count) if transaction_count > 0 else 0,
    }


@router.post("/pay", response_model=BorrowResponse)
def pay_fine(
    pay_request: PayFineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pay a fine for a borrow transaction.

    Marks the fine as paid and updates the transaction status.
    """
    txn = borrow_service.pay_fine(db, pay_request.borrow_id)
    data = borrow_service.enrich_transaction(db, txn)
    return BorrowResponse(**data)


@router.post("/pay-bulk", response_model=dict)
def pay_multiple_fines(
    borrow_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pay multiple fines at once.

    Returns a summary of paid fines and any errors encountered.
    """
    results = {
        "paid": [],
        "errors": [],
        "total_paid_amount": Decimal("0"),
    }

    for borrow_id in borrow_ids:
        try:
            txn = borrow_service.pay_fine(db, borrow_id)
            results["paid"].append(borrow_id)
            results["total_paid_amount"] += txn.fine_amount or Decimal("0")
        except NotFoundError as e:
            results["errors"].append({"borrow_id": borrow_id, "error": str(e)})
        except BusinessRuleError as e:
            results["errors"].append({"borrow_id": borrow_id, "error": str(e)})

    results["total_paid_amount"] = float(results["total_paid_amount"])
    return results


@router.get("/members/{member_id}", response_model=FinesSummary)
def get_member_fines_detail(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed fines summary for a specific member.

    Includes total fines, paid fines, and outstanding balance.
    """
    return borrow_service.get_member_fines(db, member_id)


@router.get("/members/{member_id}/history", response_model=BorrowListResponse)
def get_member_fines_history(
    member_id: str,
    include_paid: bool = Query(True, description="Include paid fines in history"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get fines history for a specific member.

    Returns all transactions that have or had fines associated.
    """
    # Get all transactions with fines for the member
    from app.models.borrow_transaction import BorrowTransaction
    from sqlalchemy import or_

    query = db.query(BorrowTransaction).filter(
        BorrowTransaction.member_id == member_id,
        BorrowTransaction.fine_amount > 0
    )

    if not include_paid:
        query = query.filter(BorrowTransaction.fine_paid == False)

    total = query.count()
    txns = query.offset(skip).limit(limit).all()

    enriched = borrow_service.enrich_transactions(db, txns)
    items = [BorrowResponse(**data) for data in enriched]
    return BorrowListResponse(items=items, total=total)

