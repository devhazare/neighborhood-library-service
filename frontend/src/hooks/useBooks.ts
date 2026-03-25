import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api-client';

// Types
interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  category?: string;
  available_copies: number;
  total_copies: number;
  summary?: string;
  tags?: string[];
}

interface BookCreateData {
  title: string;
  author: string;
  isbn?: string;
  category?: string;
  total_copies?: number;
}

// Query Keys
export const bookKeys = {
  all: ['books'] as const,
  lists: () => [...bookKeys.all, 'list'] as const,
  list: (filters: any) => [...bookKeys.lists(), filters] as const,
  details: () => [...bookKeys.all, 'detail'] as const,
  detail: (id: string) => [...bookKeys.details(), id] as const,
  search: (query: string) => [...bookKeys.all, 'search', query] as const,
};

// Hooks

/**
 * Fetch all books
 */
export const useBooks = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: bookKeys.list(params || {}),
    queryFn: async () => {
      const { data } = await api.get<Book[]>('/api/v1/books', { params });
      return data;
    },
  });
};

/**
 * Fetch a single book by ID
 */
export const useBook = (id: string) => {
  return useQuery({
    queryKey: bookKeys.detail(id),
    queryFn: async () => {
      const { data } = await api.get<Book>(`/api/v1/books/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

/**
 * Search books
 */
export const useSearchBooks = (query: string, filters?: Record<string, any>) => {
  return useQuery({
    queryKey: bookKeys.search(JSON.stringify({ query, ...filters })),
    queryFn: async () => {
      const { data } = await api.get<Book[]>('/api/v1/books/search', {
        params: { q: query, ...filters },
      });
      return data;
    },
    enabled: query.length > 0,
  });
};

/**
 * Create a new book
 */
export const useCreateBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookData: BookCreateData) => {
      const { data } = await api.post<Book>('/api/v1/books', bookData);
      return data;
    },
    onSuccess: () => {
      // Invalidate and refetch books list
      queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
    },
  });
};

/**
 * Update a book
 */
export const useUpdateBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<BookCreateData> }) => {
      const response = await api.put<Book>(`/api/v1/books/${id}`, data);
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate lists and the specific book detail
      queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
      queryClient.invalidateQueries({ queryKey: bookKeys.detail(data.id) });
    },
  });
};

/**
 * Delete a book
 */
export const useDeleteBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/books/${id}`);
      return id;
    },
    onSuccess: (id) => {
      // Invalidate lists and remove the specific book from cache
      queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
      queryClient.removeQueries({ queryKey: bookKeys.detail(id) });
    },
  });
};

/**
 * AI enrich a book
 */
export const useEnrichBook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post<Book>(`/api/v1/books/${id}/ai-enrich`);
      return data;
    },
    onSuccess: (data) => {
      // Update the book in cache
      queryClient.setQueryData(bookKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
    },
  });
};

/**
 * Upload PDF for a book
 */
export const useUploadBookPDF = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, file }: { id: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post<Book>(`/api/v1/books/${id}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(bookKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
    },
  });
};

