'use client';

import { useState, useEffect } from 'react';
import { borrowApi } from '@/lib/api';
import type { BorrowTransaction } from '@/lib/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface ReturnFormProps {
  onSuccess: () => void;
}

export default function ReturnForm({ onSuccess }: ReturnFormProps) {
  const [borrowId, setBorrowId] = useState('');
  const [activeBorrowings, setActiveBorrowings] = useState<BorrowTransaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    borrowApi.listActive(0, 100)
      .then((r) => setActiveBorrowings(r.data.items))
      .catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!borrowId.trim()) { setError('Borrow transaction ID is required.'); return; }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await borrowApi.return(borrowId.trim());
      setSuccess('Book returned successfully!');
      setBorrowId('');
      setActiveBorrowings((prev) => prev.filter((b) => b.id !== borrowId.trim()));
      onSuccess();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Failed to return book. Please check the transaction ID.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Borrow Transaction ID"
        value={borrowId}
        onChange={(e) => { setBorrowId(e.target.value); setError(null); }}
        placeholder="Enter transaction UUID..."
      />

      {activeBorrowings.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Or select from active borrowings:</p>
          <div className="max-h-48 overflow-y-auto space-y-1 rounded-lg border border-gray-200 p-2">
            {activeBorrowings.map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => setBorrowId(b.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  borrowId === b.id
                    ? 'bg-indigo-100 text-indigo-900'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <span className="font-medium">{b.book_title ?? b.book_id}</span>
                <span className="text-xs text-gray-500 ml-2">— {b.member_name ?? b.member_id}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
          {success}
        </div>
      )}
      <Button type="submit" loading={loading} className="w-full">
        Return Book
      </Button>
    </form>
  );
}
