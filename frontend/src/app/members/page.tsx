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
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import ApiError, { parseApiError } from '@/components/ui/ApiError';
import Pagination, { usePagination } from '@/components/ui/Pagination';
import ProtectedRoute from '@/components/ProtectedRoute';

function MembersPageContent() {
  const [members, setMembers] = useState<Member[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const pagination = usePagination(25);

  const [formOpen, setFormOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Member | null>(null);
  const [detailTarget, setDetailTarget] = useState<Member | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const hasFilters = search || statusFilter;
      const r = hasFilters
        ? await membersApi.search({
            q: search || undefined,
            status: statusFilter || undefined,
            skip: pagination.skip,
            limit: pagination.pageSize,
          })
        : await membersApi.list(pagination.skip, pagination.pageSize);
      setMembers(r.data.items);
      pagination.setTotal(r.data.total);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, pagination.skip, pagination.pageSize]);

  useEffect(() => { load(); }, [load]);

  // Debounce search and reset pagination
  useEffect(() => {
    const timer = setTimeout(() => {
      pagination.reset();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, statusFilter]);

  async function handleCreate(data: MemberCreate) {
    try {
      await membersApi.create(data);
      setFormOpen(false);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  async function handleUpdate(data: MemberCreate) {
    if (!editTarget) return;
    try {
      await membersApi.update(editTarget.id, data);
      setEditTarget(null);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  async function handleDelete(member: Member) {
    if (!confirm(`Are you sure you want to delete "${member.full_name}"?`)) return;
    try {
      await membersApi.delete(member.id);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex-1 min-w-48">
          <Input
            placeholder="Search by name, membership ID, email…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <Button onClick={() => setFormOpen(true)}>+ Add Member</Button>
      </div>

      {/* Error display */}
      {error && <ApiError message={error} onRetry={load} />}

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          <MemberList
            members={members}
            onEdit={(m) => setEditTarget(m)}
            onDelete={handleDelete}
            onViewDetails={(m) => setDetailTarget(m)}
          />

          {/* Pagination */}
          <Pagination
            currentPage={pagination.currentPage}
            totalPages={pagination.totalPages}
            totalItems={pagination.total}
            pageSize={pagination.pageSize}
            onPageChange={pagination.handlePageChange}
            onPageSizeChange={pagination.handlePageSizeChange}
            className="mt-4 pt-4 border-t border-gray-200"
          />
        </>
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

export default function MembersPage() {
  return (
    <ProtectedRoute>
      <ErrorBoundary>
        <MembersPageContent />
      </ErrorBoundary>
    </ProtectedRoute>
  );
}
