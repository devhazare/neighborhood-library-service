'use client';

import { useState, useRef } from 'react';
import type { Book, BookCreate } from '@/lib/types';
import { booksApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface BookFormProps {
  initialData?: Partial<Book>;
  onSubmit: (data: BookCreate, pdfFile?: File) => Promise<void>;
  onCancel: () => void;
}

export default function BookForm({ initialData, onSubmit, onCancel }: BookFormProps) {
  const [form, setForm] = useState<BookCreate>({
    title: initialData?.title ?? '',
    author: initialData?.author ?? '',
    isbn: initialData?.isbn ?? '',
    publisher: initialData?.publisher ?? '',
    published_year: initialData?.published_year ?? undefined,
    category: initialData?.category ?? '',
    total_copies: initialData?.total_copies ?? 1,
    available_copies: initialData?.available_copies ?? 1,
    shelf_location: initialData?.shelf_location ?? '',
  });
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [errors, setErrors] = useState<Partial<Record<keyof BookCreate, string>>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  function validate() {
    const e: Partial<Record<keyof BookCreate, string>> = {};
    if (!form.title.trim()) e.title = 'Title is required';
    if (!form.author.trim()) e.author = 'Author is required';
    return e;
  }

  async function handlePdfUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    setPdfFile(file);
    setExtracting(true);

    try {
      const response = await booksApi.extractPdfMetadata(file);
      const metadata = response.data;

      // Auto-fill form fields (except shelf_location, total_copies, available_copies)
      setForm((prev) => ({
        ...prev,
        title: metadata.title || prev.title,
        author: metadata.author || prev.author,
        isbn: metadata.isbn || prev.isbn,
        publisher: metadata.publisher || prev.publisher,
        published_year: metadata.published_year || prev.published_year,
        category: metadata.category || prev.category,
      }));
    } catch (err) {
      console.error('Failed to extract PDF metadata:', err);
      alert('Failed to extract metadata from PDF. Please fill in the details manually.');
    } finally {
      setExtracting(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setLoading(true);
    try {
      await onSubmit(form, pdfFile || undefined);
    } finally {
      setLoading(false);
    }
  }

  function set(field: keyof BookCreate) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
      setForm((prev) => ({
        ...prev,
        [field]: e.target.type === 'number'
          ? e.target.value === '' ? undefined : Number(e.target.value)
          : e.target.value,
      }));
    };
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* PDF Upload Section */}
      {!initialData?.id && (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handlePdfUpload}
            className="hidden"
          />
          {pdfFile ? (
            <div className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-gray-700">{pdfFile.name}</span>
              <button
                type="button"
                onClick={() => { setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
                className="text-red-500 hover:text-red-700 text-sm ml-2"
              >
                Remove
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={extracting}
              className="text-sm text-gray-600 hover:text-blue-600"
            >
              {extracting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Extracting metadata from PDF...
                </span>
              ) : (
                <>
                  <svg className="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Upload PDF to auto-fill book details
                </>
              )}
            </button>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Title *"
          value={form.title}
          onChange={set('title')}
          error={errors.title}
          placeholder="Book title"
        />
        <Input
          label="Author *"
          value={form.author}
          onChange={set('author')}
          error={errors.author}
          placeholder="Author name"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="ISBN" value={form.isbn ?? ''} onChange={set('isbn')} placeholder="978-..." />
        <Input label="Publisher" value={form.publisher ?? ''} onChange={set('publisher')} placeholder="Publisher name" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Published Year"
          type="number"
          value={form.published_year ?? ''}
          onChange={set('published_year')}
          placeholder="2024"
          min={1000}
          max={new Date().getFullYear()}
        />
        <Input label="Category" value={form.category ?? ''} onChange={set('category')} placeholder="Fiction, Science..." />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Total Copies"
          type="number"
          value={form.total_copies ?? 1}
          onChange={set('total_copies')}
          min={0}
        />
        <Input
          label="Available Copies"
          type="number"
          value={form.available_copies ?? 1}
          onChange={set('available_copies')}
          min={0}
        />
      </div>
      <Input
        label="Shelf Location"
        value={form.shelf_location ?? ''}
        onChange={set('shelf_location')}
        placeholder="A1, B3..."
      />
      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={loading}>
          {initialData?.id ? 'Update Book' : 'Add Book'}
        </Button>
      </div>
    </form>
  );
}
