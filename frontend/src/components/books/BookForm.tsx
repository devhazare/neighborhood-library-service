'use client';

import { useState } from 'react';
import type { Book, BookCreate } from '@/lib/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface BookFormProps {
  initialData?: Partial<Book>;
  onSubmit: (data: BookCreate) => Promise<void>;
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
  const [errors, setErrors] = useState<Partial<Record<keyof BookCreate, string>>>({});

  function validate() {
    const e: Partial<Record<keyof BookCreate, string>> = {};
    if (!form.title.trim()) e.title = 'Title is required';
    if (!form.author.trim()) e.author = 'Author is required';
    return e;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setLoading(true);
    try {
      await onSubmit(form);
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
