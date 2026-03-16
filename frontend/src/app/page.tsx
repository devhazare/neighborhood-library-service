'use client';

import { useState, useEffect } from 'react';
import { dashboardApi, borrowApi } from '@/lib/api';
import type { DashboardStats, BorrowTransaction } from '@/lib/types';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { formatDate } from '@/lib/utils';
import ProtectedRoute from '@/components/ProtectedRoute';

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-xl ${color}`}>{icon}</div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [overdue, setOverdue] = useState<BorrowTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [s, o] = await Promise.all([
          dashboardApi.getStats(),
          borrowApi.listOverdue(0, 5),
        ]);
        setStats(s);
        setOverdue(o.data.items);
      } catch {
        // API might not be running; show zeros
        setStats({ total_books: 0, total_members: 0, active_borrowings: 0, overdue_books: 0 });
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Books',
      value: stats?.total_books ?? 0,
      color: 'bg-indigo-100',
      icon: (
        <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
    },
    {
      label: 'Total Members',
      value: stats?.total_members ?? 0,
      color: 'bg-green-100',
      icon: (
        <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
    },
    {
      label: 'Active Borrowings',
      value: stats?.active_borrowings ?? 0,
      color: 'bg-blue-100',
      icon: (
        <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      ),
    },
    {
      label: 'Overdue Books',
      value: stats?.overdue_books ?? 0,
      color: 'bg-red-100',
      icon: (
        <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ];

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {statCards.map((s) => (
            <StatCard key={s.label} {...s} />
          ))}
        </div>

        {/* Recent Overdue */}
        <Card title="Recent Overdue Books" subtitle="Books past their due date">
          {overdue.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">No overdue books. 🎉</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {overdue.map((b) => (
                <div key={b.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm text-gray-900">{b.book_title ?? b.book_id}</p>
                    <p className="text-xs text-gray-500">
                      {b.member_name ?? b.member_id} · Due {formatDate(b.due_date)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-semibold text-red-600">
                      {b.overdue_days}d overdue
                    </span>
                    <Badge status={b.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Quick Links */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { href: '/books', label: 'Manage Books', desc: 'Add, edit, and enrich books with AI', icon: '📚' },
            { href: '/members', label: 'Manage Members', desc: 'Add members and view borrowing history', icon: '👥' },
            { href: '/borrow', label: 'Borrow / Return', desc: 'Process loans and returns', icon: '🔄' },
          ].map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-indigo-300 transition-all group"
            >
              <span className="text-2xl">{item.icon}</span>
              <p className="mt-2 font-semibold text-gray-900 group-hover:text-indigo-700">{item.label}</p>
              <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </ProtectedRoute>
  );
}
