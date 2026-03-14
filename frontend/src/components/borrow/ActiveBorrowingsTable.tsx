import type { BorrowTransaction } from '@/lib/types';
import type { Column } from '@/components/ui/Table';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import { formatDate } from '@/lib/utils';

interface ActiveBorrowingsTableProps {
  borrowings: BorrowTransaction[];
}

export default function ActiveBorrowingsTable({ borrowings }: ActiveBorrowingsTableProps) {
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
      key: 'borrow_date',
      header: 'Borrowed',
      render: (b) => formatDate(b.borrow_date),
    },
    {
      key: 'due_date',
      header: 'Due Date',
      render: (b) => formatDate(b.due_date),
    },
    {
      key: 'status',
      header: 'Status',
      render: (b) => <Badge status={b.status} />,
    },
  ];

  return (
    <Table
      columns={columns}
      data={borrowings}
      keyExtractor={(b) => b.id}
      emptyMessage="No active borrowings."
    />
  );
}
