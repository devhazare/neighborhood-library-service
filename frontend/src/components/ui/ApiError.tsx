'use client';

import Button from './Button';

interface ApiErrorProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export default function ApiError({
  message = 'Failed to load data. Please try again.',
  onRetry,
  className = '',
}: ApiErrorProps) {
  return (
    <div className={`rounded-xl bg-red-50 border border-red-200 p-6 text-center ${className}`}>
      <div className="flex items-center justify-center gap-2 text-red-700 mb-2">
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span className="font-medium">Error</span>
      </div>
      <p className="text-red-600 text-sm mb-4">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}

export function parseApiError(error: unknown): string {
  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    const axiosError = error as {
      response?: {
        data?: {
          detail?: string | { msg: string }[];
          message?: string;
        };
        status?: number;
      };
      message?: string;
    };

    if (axiosError.response?.data) {
      const { detail, message } = axiosError.response.data;

      if (typeof detail === 'string') {
        return detail;
      }

      if (Array.isArray(detail)) {
        return detail.map((d) => d.msg).join(', ');
      }

      if (message) {
        return message;
      }
    }

    if (axiosError.response?.status === 0 || !axiosError.response) {
      return 'Network error. Please check your connection.';
    }

    const status = axiosError.response?.status;
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Session expired. Please log in again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'This operation conflicts with existing data.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return axiosError.message || 'An unexpected error occurred.';
    }
  }

  return 'An unexpected error occurred.';
}

