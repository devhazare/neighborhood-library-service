'use client';

import { useState } from 'react';
import type { BorrowTransaction } from '@/lib/types';
import type { Column } from '@/components/ui/Table';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { borrowApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';

interface OverdueTableProps {
  borrowings: BorrowTransaction[];
}

export default function OverdueTable({ borrowings }: OverdueTableProps) {
  const [reminderMessages, setReminderMessages] = useState<Record<string, string>>({});
  const [loadingId, setLoadingId] = useState<string | null>(null);

  async function generateReminder(id: string) {
    setLoadingId(id);
    try {
      const r = await borrowApi.generateReminder(id);
      setReminderMessages((prev) => ({ ...prev, [id]: r.data.message }));
    } catch {
      setReminderMessages((prev) => ({ ...prev, [id]: 'Failed to generate reminder.' }));
    } finally {
      setLoadingId(null);
    }
  }

  const columns: Column<BorrowTransaction>[] = [
    {
      key: 'book_title',
      header: 'Book',
      render: (b) => (
        <span className="font-medium text-gray-900">{b.book_title ?? b.book_id}</span>
      ),
    },
    {
      key: 'member_name',
      header: 'Member',
      render: (b) => b.member_name ?? b.member_id,
    },
    {
      key: 'due_date',
      header: 'Due Date',
      render: (b) => formatDate(b.due_date),
    },
    {
      key: 'overdue_days',
      header: 'Days Overdue',
      render: (b) => (
        <span className="font-semibold text-red-600">{b.overdue_days} day{b.overdue_days !== 1 ? 's' : ''}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (b) => <Badge status={b.status} />,
    },
    {
      key: 'reminder',
      header: 'Reminder',
      render: (b) => (
        <div className="space-y-1">
          <Button
            size="sm"
            variant={b.reminder_sent ? 'secondary' : 'danger'}
            loading={loadingId === b.id}
            onClick={() => generateReminder(b.id)}
          >
            {b.reminder_sent ? 'Resend' : 'Send Reminder'}
          </Button>
          {reminderMessages[b.id] && (
            <p className="text-xs text-gray-600 max-w-xs">{reminderMessages[b.id]}</p>
          )}
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={borrowings}
      keyExtractor={(b) => b.id}
      emptyMessage="No overdue books. 🎉"
    />
  );
}
