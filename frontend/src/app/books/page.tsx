'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Book, BookCreate, AIEnrichment } from '@/lib/types';
import { booksApi } from '@/lib/api';
import BookList from '@/components/books/BookList';
import BookForm from '@/components/books/BookForm';
import AIInsightPanel from '@/components/books/AIInsightPanel';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import ApiError, { parseApiError } from '@/components/ui/ApiError';
import Pagination, { usePagination } from '@/components/ui/Pagination';
import ProtectedRoute from '@/components/ProtectedRoute';

const CATEGORIES = ['Fiction', 'History', 'Technology', 'Science', 'Self-Help'];

function BooksPageContent() {
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const pagination = usePagination(25);

  // Modals
  const [formOpen, setFormOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Book | null>(null);
  const [aiTarget, setAiTarget] = useState<Book | null>(null);
  const [aiEnrichment, setAiEnrichment] = useState<AIEnrichment | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const hasFilters = search || category || availableOnly;
      const r = hasFilters
        ? await booksApi.search({
            q: search || undefined,
            category: category || undefined,
            available_only: availableOnly || undefined,
            skip: pagination.skip,
            limit: pagination.pageSize,
          })
        : await booksApi.list(pagination.skip, pagination.pageSize);
      setBooks(r.data.items);
      pagination.setTotal(r.data.total);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [search, category, availableOnly, pagination.skip, pagination.pageSize]);

  useEffect(() => { load(); }, [load]);

  // Debounce search and reset pagination
  useEffect(() => {
    const timer = setTimeout(() => {
      pagination.reset();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, category, availableOnly]);

  async function handleCreate(data: BookCreate, pdfFile?: File) {
    try {
      const response = await booksApi.create(data);
      if (pdfFile) {
        await booksApi.uploadPdf(response.data.id, pdfFile);
      }
      setFormOpen(false);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  async function handleUpdate(data: BookCreate) {
    if (!editTarget) return;
    try {
      await booksApi.update(editTarget.id, data);
      setEditTarget(null);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  async function handleDelete(book: Book) {
    if (!confirm(`Are you sure you want to delete "${book.title}"?`)) return;
    try {
      await booksApi.delete(book.id);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  async function handleUploadPdf(book: Book, file: File) {
    try {
      await booksApi.uploadPdf(book.id, file);
      await load();
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  function openAi(book: Book) {
    setAiTarget(book);
    setAiEnrichment(null);
  }

  async function doAiEnrich(): Promise<AIEnrichment> {
    if (!aiTarget) throw new Error('No book selected');
    const r = await booksApi.aiEnrich(aiTarget.id);
    setAiEnrichment(r.data);
    await load();
    return r.data;
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex-1 min-w-48">
          <Input
            placeholder="Search books by title, author, ISBN…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={availableOnly}
            onChange={(e) => setAvailableOnly(e.target.checked)}
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          Available only
        </label>
        <Button onClick={() => setFormOpen(true)}>+ Add Book</Button>
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
          <BookList
            books={books}
            onEdit={(b) => setEditTarget(b)}
            onDelete={handleDelete}
            onUploadPdf={handleUploadPdf}
            onAiEnrich={openAi}
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

      {/* Add Book Modal */}
      <Modal isOpen={formOpen} onClose={() => setFormOpen(false)} title="Add New Book" size="lg">
        <BookForm onSubmit={handleCreate} onCancel={() => setFormOpen(false)} />
      </Modal>

      {/* Edit Book Modal */}
      <Modal
        isOpen={!!editTarget}
        onClose={() => setEditTarget(null)}
        title="Edit Book"
        size="lg"
      >
        {editTarget && (
          <BookForm
            initialData={editTarget}
            onSubmit={handleUpdate}
            onCancel={() => setEditTarget(null)}
          />
        )}
      </Modal>

      {/* AI Insight Modal */}
      <Modal
        isOpen={!!aiTarget}
        onClose={() => { setAiTarget(null); setAiEnrichment(null); }}
        title={aiTarget ? `AI Insights: ${aiTarget.title}` : 'AI Insights'}
        size="lg"
      >
        {aiTarget && (
          <AIInsightPanel
            bookId={aiTarget.id}
            enrichment={
              aiEnrichment ?? (aiTarget.summary
                ? {
                    summary: aiTarget.summary ?? '',
                    genre: aiTarget.category ?? '',
                    tags: aiTarget.tags ?? [],
                    reading_level: aiTarget.reading_level ?? '',
                    recommended_for: aiTarget.recommended_for ?? '',
                  }
                : null)
            }
            onEnrich={doAiEnrich}
          />
        )}
      </Modal>
    </div>
  );
}

export default function BooksPage() {
  return (
    <ProtectedRoute>
      <ErrorBoundary>
        <BooksPageContent />
      </ErrorBoundary>
    </ProtectedRoute>
  );
}
