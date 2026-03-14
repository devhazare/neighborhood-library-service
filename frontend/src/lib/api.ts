import axios from 'axios';
import type {
  Book,
  BookCreate,
  Member,
  MemberCreate,
  BorrowTransaction,
  AIEnrichment,
  Recommendation,
  PaginatedResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

export const booksApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Book>>(`/api/v1/books?skip=${skip}&limit=${limit}`),
  get: (id: string) => api.get<Book>(`/api/v1/books/${id}`),
  create: (data: BookCreate) => api.post<Book>('/api/v1/books', data),
  update: (id: string, data: Partial<BookCreate>) =>
    api.put<Book>(`/api/v1/books/${id}`, data),
  uploadPdf: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Book>(`/api/v1/books/${id}/upload-pdf`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  aiEnrich: (id: string) => api.post<AIEnrichment>(`/api/v1/books/${id}/ai-enrich`),
};

export const membersApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Member>>(`/api/v1/members?skip=${skip}&limit=${limit}`),
  get: (id: string) => api.get<Member>(`/api/v1/members/${id}`),
  create: (data: MemberCreate) => api.post<Member>('/api/v1/members', data),
  update: (id: string, data: Partial<MemberCreate>) =>
    api.put<Member>(`/api/v1/members/${id}`, data),
  getBorrowedBooks: (id: string) =>
    api.get<BorrowTransaction[]>(`/api/v1/members/${id}/borrowed-books`),
  getRecommendations: (id: string) =>
    api.get<Recommendation[]>(`/api/v1/members/${id}/recommendations`),
};

export const borrowApi = {
  borrow: (bookId: string, memberId: string) =>
    api.post<BorrowTransaction>('/api/v1/borrow', {
      book_id: bookId,
      member_id: memberId,
    }),
  return: (borrowId: string) =>
    api.post<BorrowTransaction>('/api/v1/return', { borrow_id: borrowId }),
  listActive: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<BorrowTransaction>>(
      `/api/v1/borrow/active?skip=${skip}&limit=${limit}`
    ),
  listOverdue: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<BorrowTransaction>>(
      `/api/v1/borrow/overdue?skip=${skip}&limit=${limit}`
    ),
  generateReminder: (borrowId: string) =>
    api.post<{ message: string }>(`/api/v1/borrow/${borrowId}/generate-reminder`),
};

export const dashboardApi = {
  getStats: async () => {
    const [books, members, active, overdue] = await Promise.all([
      api.get<PaginatedResponse<Book>>('/api/v1/books?skip=0&limit=1'),
      api.get<PaginatedResponse<Member>>('/api/v1/members?skip=0&limit=1'),
      api.get<PaginatedResponse<BorrowTransaction>>('/api/v1/borrow/active?skip=0&limit=1'),
      api.get<PaginatedResponse<BorrowTransaction>>('/api/v1/borrow/overdue?skip=0&limit=1'),
    ]);
    return {
      total_books: books.data.total,
      total_members: members.data.total,
      active_borrowings: active.data.total,
      overdue_books: overdue.data.total,
    };
  },
};
