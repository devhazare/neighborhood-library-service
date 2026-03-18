'use client';

import { useState, useEffect } from 'react';
import type { Member, BorrowTransaction } from '@/lib/types';
import { membersApi } from '@/lib/api';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { formatDate } from '@/lib/utils';

interface MemberDetailProps {
  member: Member;
}

export default function MemberDetail({ member }: MemberDetailProps) {
  const [borrowings, setBorrowings] = useState<BorrowTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    membersApi
      .getBorrowedBooks(member.id)
      .then((r) => setBorrowings(r.data.items || []))
      .catch(() => setBorrowings([]))
      .finally(() => setLoading(false));
  }, [member.id]);

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Membership ID</p>
          <p className="font-mono font-medium text-gray-900">{member.membership_id}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Status</p>
          <Badge status={member.status} />
        </div>
        {member.email && (
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Email</p>
            <p className="font-medium text-gray-900">{member.email}</p>
          </div>
        )}
        {member.phone && (
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Phone</p>
            <p className="font-medium text-gray-900">{member.phone}</p>
          </div>
        )}
        {member.address && (
          <div className="col-span-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Address</p>
            <p className="font-medium text-gray-900">{member.address}</p>
          </div>
        )}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Joined</p>
          <p className="font-medium text-gray-900">{formatDate(member.joined_date)}</p>
        </div>
      </div>

      {/* Borrowing History */}
      <div>
        <h4 className="text-sm font-semibold text-gray-800 mb-3">Borrowing History</h4>
        {loading ? (
          <LoadingSpinner size="sm" />
        ) : borrowings.length === 0 ? (
          <p className="text-sm text-gray-400">No borrowing history.</p>
        ) : (
          <div className="space-y-2">
            {borrowings.map((b) => (
              <div
                key={b.id}
                className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 text-sm"
              >
                <div>
                  <p className="font-medium text-gray-900">{b.book_title ?? b.book_id}</p>
                  <p className="text-xs text-gray-500">
                    Borrowed {formatDate(b.borrow_date)} · Due {formatDate(b.due_date)}
                  </p>
                </div>
                <Badge status={b.status} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
