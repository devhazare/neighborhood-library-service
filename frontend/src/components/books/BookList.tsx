'use client';

import { useRef } from 'react';
import type { Book } from '@/lib/types';
import type { Column } from '@/components/ui/Table';
import Table from '@/components/ui/Table';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

interface BookListProps {
  books: Book[];
  onEdit: (book: Book) => void;
  onDelete?: (book: Book) => void;
  onUploadPdf: (book: Book, file: File) => void;
  onAiEnrich: (book: Book) => void;
}

export default function BookList({ books, onEdit, onDelete, onUploadPdf, onAiEnrich }: BookListProps) {
  const fileInputRefs = useRef<Map<string, HTMLInputElement>>(new Map());

  const columns: Column<Book>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (b) => (
        <div>
          <p className="font-medium text-gray-900 line-clamp-1">{b.title}</p>
          {b.category && <p className="text-xs text-gray-400">{b.category}</p>}
        </div>
      ),
    },
    { key: 'author', header: 'Author' },
    { key: 'isbn', header: 'ISBN', render: (b) => b.isbn ?? '—' },
    {
      key: 'available_copies',
      header: 'Availability',
      render: (b) => (
        <div className="flex items-center gap-2">
          <Badge
            status={b.available_copies > 0 ? 'active' : 'inactive'}
            label={b.available_copies > 0 ? 'Available' : 'Unavailable'}
          />
          <span className="text-xs text-gray-500">
            {b.available_copies}/{b.total_copies}
          </span>
        </div>
      ),
    },
    { key: 'shelf_location', header: 'Shelf', render: (b) => b.shelf_location ?? '—' },
    {
      key: 'actions',
      header: 'Actions',
      render: (b) => (
        <div className="flex items-center gap-1 flex-wrap">
          <Button size="sm" variant="ghost" onClick={() => onEdit(b)}>
            Edit
          </Button>
          {onDelete && (
            <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700" onClick={() => onDelete(b)}>
              Delete
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => fileInputRefs.current.get(b.id)?.click()}
          >
            PDF
          </Button>
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            ref={(el) => {
              if (el) fileInputRefs.current.set(b.id, el);
            }}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onUploadPdf(b, f);
              e.target.value = '';
            }}
          />
          <Button size="sm" variant="ghost" onClick={() => onAiEnrich(b)}>
            AI ✨
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={books}
      keyExtractor={(b) => b.id}
      emptyMessage="No books found. Add one to get started."
    />
  );
}
