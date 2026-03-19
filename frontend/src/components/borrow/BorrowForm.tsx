'use client';

import { useState, useEffect } from 'react';
import { borrowApi, membersApi, booksApi } from '@/lib/api';
import type { Member, Book } from '@/lib/types';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface BorrowFormProps {
  onSuccess: () => void;
}

export default function BorrowForm({ onSuccess }: BorrowFormProps) {
  const [memberId, setMemberId] = useState('');
  const [bookId, setBookId] = useState('');
  const [members, setMembers] = useState<Member[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load members and books on mount
  useEffect(() => {
    async function loadData() {
      setLoadingData(true);
      try {
        const [membersRes, booksRes] = await Promise.all([
          membersApi.search({ status: 'active', limit: 500 }),
          booksApi.search({ available_only: true, limit: 500 }),
        ]);
        setMembers(membersRes.data.items);
        setBooks(booksRes.data.items);
      } catch {
        setError('Failed to load members and books.');
      } finally {
        setLoadingData(false);
      }
    }
    loadData();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!memberId || !bookId) {
      setError('Please select both a member and a book.');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const r = await borrowApi.borrow(bookId, memberId);
      setSuccess(`Book borrowed successfully! Due: ${new Date(r.data.due_date).toLocaleDateString()}`);
      setMemberId('');
      setBookId('');
      // Refresh books list to update availability
      const booksRes = await booksApi.search({ available_only: true, limit: 500 });
      setBooks(booksRes.data.items);
      onSuccess();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Failed to borrow book. Please check availability.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  if (loadingData) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Member Dropdown */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Select Member
        </label>
        <select
          value={memberId}
          onChange={(e) => { setMemberId(e.target.value); setError(null); }}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="">-- Select a member --</option>
          {members.map((m) => (
            <option key={m.id} value={m.id}>
              {m.full_name} ({m.membership_id}) - {m.email || 'No email'}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          {members.length} active member{members.length !== 1 ? 's' : ''} available
        </p>
      </div>

      {/* Book Dropdown */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Select Book
        </label>
        <select
          value={bookId}
          onChange={(e) => { setBookId(e.target.value); setError(null); }}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="">-- Select a book --</option>
          {books.map((b) => (
            <option key={b.id} value={b.id}>
              {b.title} by {b.author} ({b.available_copies} available)
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          {books.length} book{books.length !== 1 ? 's' : ''} with available copies
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
          {success}
        </div>
      )}

      {/* Submit Button */}
      <Button type="submit" loading={loading} className="w-full" disabled={!memberId || !bookId}>
        Borrow Book
      </Button>
    </form>
  );
}
