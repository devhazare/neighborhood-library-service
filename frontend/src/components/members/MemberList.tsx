import type { Member } from '@/lib/types';
import type { Column } from '@/components/ui/Table';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { formatDate } from '@/lib/utils';

interface MemberListProps {
  members: Member[];
  onEdit: (member: Member) => void;
  onViewDetails: (member: Member) => void;
}

export default function MemberList({ members, onEdit, onViewDetails }: MemberListProps) {
  const columns: Column<Member>[] = [
    {
      key: 'membership_id',
      header: 'Membership ID',
      render: (m) => (
        <span className="font-mono text-sm font-medium text-gray-900">{m.membership_id}</span>
      ),
    },
    {
      key: 'full_name',
      header: 'Name',
      render: (m) => <span className="font-medium text-gray-900">{m.full_name}</span>,
    },
    { key: 'email', header: 'Email', render: (m) => m.email ?? '—' },
    { key: 'phone', header: 'Phone', render: (m) => m.phone ?? '—' },
    {
      key: 'status',
      header: 'Status',
      render: (m) => <Badge status={m.status} />,
    },
    {
      key: 'joined_date',
      header: 'Joined',
      render: (m) => formatDate(m.joined_date),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (m) => (
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={() => onViewDetails(m)}>
            Details
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onEdit(m)}>
            Edit
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={members}
      keyExtractor={(m) => m.id}
      emptyMessage="No members found. Add one to get started."
    />
  );
}
