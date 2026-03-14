import type { Book } from '@/lib/types';
import Badge from '@/components/ui/Badge';
import { formatDate } from '@/lib/utils';

interface BookDetailProps {
  book: Book;
}

export default function BookDetail({ book }: BookDetailProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide">Author</p>
          <p className="font-medium text-gray-900">{book.author}</p>
        </div>
        {book.isbn && (
          <div>
            <p className="text-gray-500 text-xs uppercase tracking-wide">ISBN</p>
            <p className="font-medium text-gray-900">{book.isbn}</p>
          </div>
        )}
        {book.publisher && (
          <div>
            <p className="text-gray-500 text-xs uppercase tracking-wide">Publisher</p>
            <p className="font-medium text-gray-900">{book.publisher}</p>
          </div>
        )}
        {book.published_year && (
          <div>
            <p className="text-gray-500 text-xs uppercase tracking-wide">Published Year</p>
            <p className="font-medium text-gray-900">{book.published_year}</p>
          </div>
        )}
        {book.category && (
          <div>
            <p className="text-gray-500 text-xs uppercase tracking-wide">Category</p>
            <p className="font-medium text-gray-900">{book.category}</p>
          </div>
        )}
        {book.shelf_location && (
          <div>
            <p className="text-gray-500 text-xs uppercase tracking-wide">Shelf Location</p>
            <p className="font-medium text-gray-900">{book.shelf_location}</p>
          </div>
        )}
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide">Copies</p>
          <p className="font-medium text-gray-900">
            {book.available_copies} available of {book.total_copies}
          </p>
        </div>
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide">Status</p>
          <Badge
            status={book.available_copies > 0 ? 'active' : 'inactive'}
            label={book.available_copies > 0 ? 'Available' : 'Unavailable'}
          />
        </div>
      </div>
      {book.summary && (
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Summary</p>
          <p className="text-sm text-gray-700 leading-relaxed">{book.summary}</p>
        </div>
      )}
      {book.tags && book.tags.length > 0 && (
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Tags</p>
          <div className="flex flex-wrap gap-1">
            {book.tags.map((tag) => (
              <span
                key={tag}
                className="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="text-xs text-gray-400 pt-2 border-t border-gray-100">
        Added {formatDate(book.created_at)} · Updated {formatDate(book.updated_at)}
      </div>
    </div>
  );
}
