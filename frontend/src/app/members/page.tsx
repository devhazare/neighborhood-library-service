'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Member, MemberCreate } from '@/lib/types';
import { membersApi } from '@/lib/api';
import MemberList from '@/components/members/MemberList';
import MemberForm from '@/components/members/MemberForm';
import MemberDetail from '@/components/members/MemberDetail';
import RecommendationsPanel from '@/components/members/RecommendationsPanel';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [filtered, setFiltered] = useState<Member[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [formOpen, setFormOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Member | null>(null);
  const [detailTarget, setDetailTarget] = useState<Member | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await membersApi.list(0, 200);
      setMembers(r.data.items);
      setFiltered(r.data.items);
    } catch {
      setError('Failed to load members. Is the API running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      q
        ? members.filter(
            (m) =>
              m.full_name.toLowerCase().includes(q) ||
              m.membership_id.toLowerCase().includes(q) ||
              m.email?.toLowerCase().includes(q) ||
              m.phone?.includes(q)
          )
        : members
    );
  }, [search, members]);

  async function handleCreate(data: MemberCreate) {
    await membersApi.create(data);
    setFormOpen(false);
    await load();
  }

  async function handleUpdate(data: MemberCreate) {
    if (!editTarget) return;
    await membersApi.update(editTarget.id, data);
    setEditTarget(null);
    await load();
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex-1 min-w-48">
          <Input
            placeholder="Search by name, membership ID, email…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button onClick={() => setFormOpen(true)}>+ Add Member</Button>
      </div>

      <p className="text-sm text-gray-500">
        Showing {filtered.length} of {members.length} members
      </p>

      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="rounded-xl bg-red-50 border border-red-200 p-6 text-center">
          <p className="text-red-700">{error}</p>
          <Button variant="secondary" size="sm" className="mt-3" onClick={load}>
            Retry
          </Button>
        </div>
      ) : (
        <MemberList
          members={filtered}
          onEdit={(m) => setEditTarget(m)}
          onViewDetails={(m) => setDetailTarget(m)}
        />
      )}

      {/* Add Member Modal */}
      <Modal isOpen={formOpen} onClose={() => setFormOpen(false)} title="Add New Member" size="lg">
        <MemberForm onSubmit={handleCreate} onCancel={() => setFormOpen(false)} />
      </Modal>

      {/* Edit Member Modal */}
      <Modal
        isOpen={!!editTarget}
        onClose={() => setEditTarget(null)}
        title="Edit Member"
        size="lg"
      >
        {editTarget && (
          <MemberForm
            initialData={editTarget}
            onSubmit={handleUpdate}
            onCancel={() => setEditTarget(null)}
          />
        )}
      </Modal>

      {/* Member Detail Modal */}
      <Modal
        isOpen={!!detailTarget}
        onClose={() => setDetailTarget(null)}
        title={detailTarget ? detailTarget.full_name : 'Member Details'}
        size="xl"
      >
        {detailTarget && (
          <div className="space-y-6">
            <MemberDetail member={detailTarget} />
            <RecommendationsPanel memberId={detailTarget.id} />
          </div>
        )}
      </Modal>
    </div>
  );
}
