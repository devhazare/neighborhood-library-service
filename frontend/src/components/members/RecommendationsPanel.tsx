'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Recommendation } from '@/lib/types';
import { membersApi } from '@/lib/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Button from '@/components/ui/Button';

interface RecommendationsPanelProps {
  memberId: string;
}

export default function RecommendationsPanel({ memberId }: RecommendationsPanelProps) {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetched, setFetched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await membersApi.getRecommendations(memberId);
      setRecs(r.data.recommendations || []);
      setFetched(true);
    } catch {
      setError('Failed to load recommendations.');
    } finally {
      setLoading(false);
    }
  }, [memberId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="rounded-xl border border-purple-200 bg-purple-50 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">🤖</span>
          <h3 className="font-semibold text-purple-900 text-sm">AI Recommendations</h3>
        </div>
        <Button size="sm" variant="ghost" onClick={load} loading={loading}>
          Refresh
        </Button>
      </div>

      {loading && <LoadingSpinner size="sm" />}
      {error && <p className="text-xs text-red-600">{error}</p>}

      {fetched && !loading && recs.length === 0 && (
        <p className="text-xs text-purple-600">No recommendations available yet.</p>
      )}

      {recs.length > 0 && !loading && (
        <div className="space-y-3">
          {recs.map((rec, i) => (
            <div key={i} className="bg-white rounded-lg p-3 shadow-sm border border-purple-100">
              <p className="font-semibold text-gray-900 text-sm">{rec.book.title}</p>
              <p className="text-xs text-gray-500 mb-1">by {rec.book.author}</p>
              <p className="text-xs text-purple-700 italic">{rec.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
