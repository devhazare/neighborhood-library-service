/**
 * Centralized API endpoint paths.
 * All API routes are defined here to ensure consistency and easy maintenance.
 */

const API_PREFIX = '/api/v1';

export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: `${API_PREFIX}/auth/login/json`,
    REGISTER: `${API_PREFIX}/auth/register`,
    ME: `${API_PREFIX}/auth/me`,
  },

  // Books
  BOOKS: {
    BASE: `${API_PREFIX}/books`,
    LIST: `${API_PREFIX}/books`,
    SEARCH: `${API_PREFIX}/books/search`,
    GET: (id: string) => `${API_PREFIX}/books/${id}`,
    CREATE: `${API_PREFIX}/books`,
    UPDATE: (id: string) => `${API_PREFIX}/books/${id}`,
    DELETE: (id: string) => `${API_PREFIX}/books/${id}`,
    UPLOAD_PDF: (id: string) => `${API_PREFIX}/books/${id}/upload-pdf`,
    AI_ENRICH: (id: string) => `${API_PREFIX}/books/${id}/ai-enrich`,
    EXTRACT_PDF_METADATA: `${API_PREFIX}/books/extract-pdf-metadata`,
  },

  // Members
  MEMBERS: {
    BASE: `${API_PREFIX}/members`,
    LIST: `${API_PREFIX}/members`,
    SEARCH: `${API_PREFIX}/members/search`,
    GET: (id: string) => `${API_PREFIX}/members/${id}`,
    CREATE: `${API_PREFIX}/members`,
    UPDATE: (id: string) => `${API_PREFIX}/members/${id}`,
    DELETE: (id: string) => `${API_PREFIX}/members/${id}`,
    BORROWED_BOOKS: (id: string) => `${API_PREFIX}/members/${id}/borrowed-books`,
    RECOMMENDATIONS: (id: string) => `${API_PREFIX}/members/${id}/recommendations`,
    FINES: (id: string) => `${API_PREFIX}/members/${id}/fines`,
  },

  // Borrow Operations
  BORROW: {
    BORROW: `${API_PREFIX}/borrow`,
    RETURN: `${API_PREFIX}/return`,
    ACTIVE: `${API_PREFIX}/borrow/active`,
    OVERDUE: `${API_PREFIX}/borrow/overdue`,
    GENERATE_REMINDER: (id: string) => `${API_PREFIX}/borrow/${id}/generate-reminder`,
  },

  // Fines
  FINES: {
    PAY: `${API_PREFIX}/fines/pay`,
    UNPAID: `${API_PREFIX}/fines/unpaid`,
  },
} as const;

/**
 * Helper to build query string from params object
 */
export function buildQueryString(params: Record<string, string | number | boolean | undefined>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

