'use client';

import { useState } from 'react';
import { borrowApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface BorrowFormProps {
  onSuccess: () => void;
}

export default function BorrowForm({ onSuccess }: BorrowFormProps) {
  const [memberId, setMemberId] = useState('');
  const [bookId, setBookId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!memberId.trim() || !bookId.trim()) {
      setError('Both Member ID and Book ID are required.');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const r = await borrowApi.borrow(bookId.trim(), memberId.trim());
      setSuccess(`Book borrowed successfully! Due: ${new Date(r.data.due_date).toLocaleDateString()}`);
      setMemberId('');
      setBookId('');
      onSuccess();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Failed to borrow book. Please check IDs and availability.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Member ID (UUID)"
        value={memberId}
        onChange={(e) => { setMemberId(e.target.value); setError(null); }}
        placeholder="e.g. 3f2a1b4c-..."
        hint="Enter the member's system UUID"
      />
      <Input
        label="Book ID (UUID)"
        value={bookId}
        onChange={(e) => { setBookId(e.target.value); setError(null); }}
        placeholder="e.g. 7d8e9f0a-..."
        hint="Enter the book's system UUID"
      />
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
        Borrow Book
      </Button>
    </form>
  );
}
