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
  FinesSummary,
} from './types';
import { getToken, logout } from './auth';
import { ENDPOINTS, buildQueryString } from './endpoints';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

// Add auth token to all requests
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors by logging out
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout();
    }
    return Promise.reject(error);
  }
);

export const booksApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Book>>(ENDPOINTS.BOOKS.LIST + buildQueryString({ skip, limit })),
  search: (params: {
    q?: string;
    category?: string;
    author?: string;
    available_only?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const queryString = buildQueryString({
      q: params.q,
      category: params.category,
      author: params.author,
      available_only: params.available_only,
      skip: params.skip || 0,
      limit: params.limit || 100,
    });
    return api.get<PaginatedResponse<Book>>(ENDPOINTS.BOOKS.SEARCH + queryString);
  },
  get: (id: string) => api.get<Book>(ENDPOINTS.BOOKS.GET(id)),
  create: (data: BookCreate) => api.post<Book>(ENDPOINTS.BOOKS.CREATE, data),
  update: (id: string, data: Partial<BookCreate>) =>
    api.put<Book>(ENDPOINTS.BOOKS.UPDATE(id), data),
  delete: (id: string) => api.delete(ENDPOINTS.BOOKS.DELETE(id)),
  uploadPdf: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Book>(ENDPOINTS.BOOKS.UPLOAD_PDF(id), formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  aiEnrich: (id: string) => api.post<AIEnrichment>(ENDPOINTS.BOOKS.AI_ENRICH(id)),
  extractPdfMetadata: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<{
      title?: string;
      author?: string;
      isbn?: string;
      publisher?: string;
      published_year?: number;
      category?: string;
    }>(ENDPOINTS.BOOKS.EXTRACT_PDF_METADATA, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const membersApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Member>>(ENDPOINTS.MEMBERS.LIST + buildQueryString({ skip, limit })),
  search: (params: {
    q?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const queryString = buildQueryString({
      q: params.q,
      status: params.status,
      skip: params.skip || 0,
      limit: params.limit || 100,
    });
    return api.get<PaginatedResponse<Member>>(ENDPOINTS.MEMBERS.SEARCH + queryString);
  },
  get: (id: string) => api.get<Member>(ENDPOINTS.MEMBERS.GET(id)),
  create: (data: MemberCreate) => api.post<Member>(ENDPOINTS.MEMBERS.CREATE, data),
  update: (id: string, data: Partial<MemberCreate>) =>
    api.put<Member>(ENDPOINTS.MEMBERS.UPDATE(id), data),
  delete: (id: string) => api.delete(ENDPOINTS.MEMBERS.DELETE(id)),
  getBorrowedBooks: (id: string) =>
    api.get<PaginatedResponse<BorrowTransaction>>(ENDPOINTS.MEMBERS.BORROWED_BOOKS(id)),
  getRecommendations: (id: string) =>
    api.get<{ recommendations: Recommendation[] }>(ENDPOINTS.MEMBERS.RECOMMENDATIONS(id)),
};

export const borrowApi = {
  borrow: (bookId: string, memberId: string) =>
    api.post<BorrowTransaction>(ENDPOINTS.BORROW.BORROW, {
      book_id: bookId,
      member_id: memberId,
    }),
  return: (borrowId: string) =>
    api.post<BorrowTransaction>(ENDPOINTS.BORROW.RETURN, { borrow_id: borrowId }),
  listActive: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<BorrowTransaction>>(
      ENDPOINTS.BORROW.ACTIVE + buildQueryString({ skip, limit })
    ),
  listOverdue: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<BorrowTransaction>>(
      ENDPOINTS.BORROW.OVERDUE + buildQueryString({ skip, limit })
    ),
  generateReminder: (borrowId: string) =>
    api.post<{ message: string }>(ENDPOINTS.BORROW.GENERATE_REMINDER(borrowId)),
};

export const finesApi = {
  payFine: (borrowId: string) =>
    api.post<BorrowTransaction>(ENDPOINTS.FINES.PAY, { borrow_id: borrowId }),
  listUnpaid: (memberId?: string) =>
    api.get<PaginatedResponse<BorrowTransaction>>(
      ENDPOINTS.FINES.UNPAID + buildQueryString({ member_id: memberId })
    ),
  getMemberFines: (memberId: string) =>
    api.get<FinesSummary>(ENDPOINTS.MEMBERS.FINES(memberId)),
};

export const dashboardApi = {
  getStats: async () => {
    const [books, members, active, overdue] = await Promise.all([
      api.get<PaginatedResponse<Book>>(ENDPOINTS.BOOKS.LIST + buildQueryString({ skip: 0, limit: 1 })),
      api.get<PaginatedResponse<Member>>(ENDPOINTS.MEMBERS.LIST + buildQueryString({ skip: 0, limit: 1 })),
      api.get<PaginatedResponse<BorrowTransaction>>(ENDPOINTS.BORROW.ACTIVE + buildQueryString({ skip: 0, limit: 1 })),
      api.get<PaginatedResponse<BorrowTransaction>>(ENDPOINTS.BORROW.OVERDUE + buildQueryString({ skip: 0, limit: 1 })),
    ]);
    return {
      total_books: books.data.total,
      total_members: members.data.total,
      active_borrowings: active.data.total,
      overdue_books: overdue.data.total,
    };
  },
};

export const authApi = {
  login: (username: string, password: string) =>
    api.post<{ access_token: string; token_type: string }>(ENDPOINTS.AUTH.LOGIN, {
      username,
      password,
    }),
  register: (data: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) => api.post(ENDPOINTS.AUTH.REGISTER, data),
  getCurrentUser: () => api.get(ENDPOINTS.AUTH.ME),
};


