import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
}

interface Book {
  id: string;
  title: string;
  author: string;
}

interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Toast notifications
  toast: {
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
    visible: boolean;
  };
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
  hideToast: () => void;

  // Cart/Selection (for batch operations)
  selectedBooks: Book[];
  addToSelection: (book: Book) => void;
  removeFromSelection: (bookId: string) => void;
  clearSelection: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // User state
        user: null,
        isAuthenticated: false,
        setUser: (user) =>
          set({ user, isAuthenticated: !!user }, false, 'setUser'),
        login: (user, token) => {
          if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', token);
          }
          set({ user, isAuthenticated: true }, false, 'login');
        },
        logout: () => {
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
          }
          set({ user: null, isAuthenticated: false }, false, 'logout');
        },

        // UI state
        sidebarOpen: true,
        setSidebarOpen: (open) =>
          set({ sidebarOpen: open }, false, 'setSidebarOpen'),
        toggleSidebar: () =>
          set((state) => ({ sidebarOpen: !state.sidebarOpen }), false, 'toggleSidebar'),

        // Toast notifications
        toast: {
          message: '',
          type: 'info',
          visible: false,
        },
        showToast: (message, type) =>
          set(
            { toast: { message, type, visible: true } },
            false,
            'showToast'
          ),
        hideToast: () =>
          set(
            (state) => ({ toast: { ...state.toast, visible: false } }),
            false,
            'hideToast'
          ),

        // Selection state
        selectedBooks: [],
        addToSelection: (book) =>
          set(
            (state) => ({
              selectedBooks: [...state.selectedBooks, book],
            }),
            false,
            'addToSelection'
          ),
        removeFromSelection: (bookId) =>
          set(
            (state) => ({
              selectedBooks: state.selectedBooks.filter(
                (b) => b.id !== bookId
              ),
            }),
            false,
            'removeFromSelection'
          ),
        clearSelection: () =>
          set({ selectedBooks: [] }, false, 'clearSelection'),
      }),
      {
        name: 'library-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    ),
    { name: 'LibraryStore' }
  )
);

// Selectors for better performance
export const useUser = () => useAppStore((state) => state.user);
export const useIsAuthenticated = () => useAppStore((state) => state.isAuthenticated);
export const useSidebarOpen = () => useAppStore((state) => state.sidebarOpen);
export const useToast = () => useAppStore((state) => state.toast);
export const useSelectedBooks = () => useAppStore((state) => state.selectedBooks);

