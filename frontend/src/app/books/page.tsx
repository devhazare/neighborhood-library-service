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

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [filtered, setFiltered] = useState<Book[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [formOpen, setFormOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Book | null>(null);
  const [aiTarget, setAiTarget] = useState<Book | null>(null);
  const [aiEnrichment, setAiEnrichment] = useState<AIEnrichment | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await booksApi.list(0, 200);
      setBooks(r.data.items);
      setFiltered(r.data.items);
    } catch {
      setError('Failed to load books. Is the API running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      q
        ? books.filter(
            (b) =>
              b.title.toLowerCase().includes(q) ||
              b.author.toLowerCase().includes(q) ||
              b.isbn?.toLowerCase().includes(q) ||
              b.category?.toLowerCase().includes(q)
          )
        : books
    );
  }, [search, books]);

  async function handleCreate(data: BookCreate) {
    await booksApi.create(data);
    setFormOpen(false);
    await load();
  }

  async function handleUpdate(data: BookCreate) {
    if (!editTarget) return;
    await booksApi.update(editTarget.id, data);
    setEditTarget(null);
    await load();
  }

  async function handleUploadPdf(book: Book, file: File) {
    try {
      await booksApi.uploadPdf(book.id, file);
      await load();
    } catch {
      alert('Failed to upload PDF.');
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
    await load(); // refresh book data
    return r.data;
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex-1 min-w-48">
          <Input
            placeholder="Search books by title, author, ISBN, category…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button onClick={() => setFormOpen(true)}>+ Add Book</Button>
      </div>

      {/* Stats row */}
      <p className="text-sm text-gray-500">
        Showing {filtered.length} of {books.length} books
      </p>

      {/* Content */}
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
        <BookList
          books={filtered}
          onEdit={(b) => setEditTarget(b)}
          onUploadPdf={handleUploadPdf}
          onAiEnrich={openAi}
        />
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
