'use client';

import { useState } from 'react';
import type { AIEnrichment } from '@/lib/types';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface AIInsightPanelProps {
  bookId: string;
  enrichment?: AIEnrichment | null;
  onEnrich: () => Promise<AIEnrichment>;
}

export default function AIInsightPanel({ enrichment: initial, onEnrich }: AIInsightPanelProps) {
  const [enrichment, setEnrichment] = useState<AIEnrichment | null>(initial ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleEnrich() {
    setLoading(true);
    setError(null);
    try {
      const result = await onEnrich();
      setEnrichment(result);
    } catch {
      setError('Failed to fetch AI insights. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">✨</span>
          <h3 className="font-semibold text-indigo-900 text-sm">AI Insights</h3>
        </div>
        <Button size="sm" variant="primary" onClick={handleEnrich} loading={loading}>
          {enrichment ? 'Re-Enrich' : 'Enrich with AI'}
        </Button>
      </div>

      {loading && (
        <div className="py-4">
          <LoadingSpinner size="sm" />
          <p className="text-center text-xs text-indigo-600 mt-2">Analyzing with AI…</p>
        </div>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}

      {enrichment && !loading && (
        <div className="space-y-3">
          {enrichment.summary && (
            <div>
              <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-1">Summary</p>
              <p className="text-sm text-gray-700 leading-relaxed">{enrichment.summary}</p>
            </div>
          )}
          <div className="flex flex-wrap gap-4">
            {enrichment.genre && (
              <div>
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-1">Genre</p>
                <span className="bg-purple-100 text-purple-800 text-xs px-2.5 py-0.5 rounded-full font-medium">
                  {enrichment.genre}
                </span>
              </div>
            )}
            {enrichment.reading_level && (
              <div>
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-1">Reading Level</p>
                <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-0.5 rounded-full font-medium">
                  {enrichment.reading_level}
                </span>
              </div>
            )}
          </div>
          {enrichment.tags && enrichment.tags.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-1">Tags</p>
              <div className="flex flex-wrap gap-1">
                {enrichment.tags.map((tag) => (
                  <span
                    key={tag}
                    className="bg-white border border-indigo-200 text-indigo-700 text-xs px-2 py-0.5 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
          {enrichment.recommended_for && (
            <div>
              <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-1">Recommended For</p>
              <p className="text-sm text-gray-700">{enrichment.recommended_for}</p>
            </div>
          )}
        </div>
      )}

      {!enrichment && !loading && !error && (
        <p className="text-xs text-indigo-600 text-center py-2">
          Click &quot;Enrich with AI&quot; to generate insights for this book.
        </p>
      )}
    </div>
  );
}
