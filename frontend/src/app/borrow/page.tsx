'use client';

import { useState, useEffect, useCallback } from 'react';
import type { BorrowTransaction } from '@/lib/types';
import { borrowApi } from '@/lib/api';
import ActiveBorrowingsTable from '@/components/borrow/ActiveBorrowingsTable';
import OverdueTable from '@/components/borrow/OverdueTable';
import BorrowForm from '@/components/borrow/BorrowForm';
import ReturnForm from '@/components/borrow/ReturnForm';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { cn } from '@/lib/utils';
import ProtectedRoute from '@/components/ProtectedRoute';

type Tab = 'active' | 'overdue' | 'borrow' | 'return';

const tabs: { id: Tab; label: string }[] = [
  { id: 'active', label: 'Active Borrowings' },
  { id: 'overdue', label: 'Overdue' },
  { id: 'borrow', label: 'Borrow a Book' },
  { id: 'return', label: 'Return a Book' },
];

export default function BorrowPage() {
  const [activeTab, setActiveTab] = useState<Tab>('active');
  const [activeBorrowings, setActiveBorrowings] = useState<BorrowTransaction[]>([]);
  const [overdueBorrowings, setOverdueBorrowings] = useState<BorrowTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [active, overdue] = await Promise.all([
        borrowApi.listActive(0, 200),
        borrowApi.listOverdue(0, 200),
      ]);
      setActiveBorrowings(active.data.items);
      setOverdueBorrowings(overdue.data.items);
    } catch {
      setError('Failed to load borrowing data. Is the API running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8 space-y-4">
        {/* Tab Bar */}
        <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
          {tabs.map((t) => (
            <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === t.id
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            )}
          >
            {t.label}
            {t.id === 'overdue' && overdueBorrowings.length > 0 && (
              <span className="ml-1.5 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">
                {overdueBorrowings.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'active' && (
        <Card
          title="Active Borrowings"
          subtitle={`${activeBorrowings.length} currently borrowed`}
        >
          {loading ? (
            <div className="flex justify-center py-8"><LoadingSpinner /></div>
          ) : error ? (
            <p className="text-red-600 text-sm">{error}</p>
          ) : (
            <ActiveBorrowingsTable borrowings={activeBorrowings} />
          )}
        </Card>
      )}

      {activeTab === 'overdue' && (
        <Card
          title="Overdue Books"
          subtitle={`${overdueBorrowings.length} overdue`}
        >
          {loading ? (
            <div className="flex justify-center py-8"><LoadingSpinner /></div>
          ) : error ? (
            <p className="text-red-600 text-sm">{error}</p>
          ) : (
            <OverdueTable borrowings={overdueBorrowings} />
          )}
        </Card>
      )}

      {activeTab === 'borrow' && (
        <div className="max-w-md">
          <Card title="Borrow a Book" subtitle="Enter the member and book IDs to process a loan">
            <BorrowForm onSuccess={load} />
          </Card>
        </div>
      )}

      {activeTab === 'return' && (
        <div className="max-w-md">
          <Card title="Return a Book" subtitle="Select or enter a transaction to process a return">
            <ReturnForm onSuccess={load} />
          </Card>
        </div>
      )}
      </div>
    </ProtectedRoute>
  );
}
