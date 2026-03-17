export interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  publisher?: string;
  published_year?: number;
  category?: string;
  total_copies: number;
  available_copies: number;
  shelf_location?: string;
  summary?: string;
  tags?: string[];
  reading_level?: string;
  recommended_for?: string;
  pdf_file_path?: string;
  created_at: string;
  updated_at: string;
}

export interface BookCreate {
  title: string;
  author: string;
  isbn?: string;
  publisher?: string;
  published_year?: number;
  category?: string;
  total_copies?: number;
  available_copies?: number;
  shelf_location?: string;
}

export interface Member {
  id: string;
  membership_id: string;
  full_name: string;
  email?: string;
  phone?: string;
  address?: string;
  status: 'active' | 'inactive';
  joined_date?: string;
  created_at: string;
  updated_at: string;
}

export interface MemberCreate {
  membership_id: string;
  full_name: string;
  email?: string;
  phone?: string;
  address?: string;
  status?: 'active' | 'inactive';
  joined_date?: string;
}

export interface BorrowTransaction {
  id: string;
  book_id: string;
  member_id: string;
  book_title?: string;
  member_name?: string;
  borrow_date: string;
  due_date: string;
  return_date?: string;
  status: 'borrowed' | 'returned' | 'overdue';
  overdue_days: number;
  reminder_sent: boolean;
  fine_amount: number;
  fine_paid: boolean;
  fine_paid_date?: string;
  created_at: string;
  updated_at: string;
}

export interface FinesSummary {
  member_id: string;
  member_name?: string;
  total_fines: number;
  paid_fines: number;
  outstanding_fines: number;
  transactions_with_fines: number;
}

export interface AIEnrichment {
  summary: string;
  genre: string;
  tags: string[];
  reading_level: string;
  recommended_for: string;
}

export interface Recommendation {
  book: Book;
  reason: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface DashboardStats {
  total_books: number;
  total_members: number;
  active_borrowings: number;
  overdue_books: number;
}
