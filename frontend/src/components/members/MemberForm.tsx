'use client';

import { useState } from 'react';
import type { Member, MemberCreate } from '@/lib/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface MemberFormProps {
  initialData?: Partial<Member>;
  onSubmit: (data: MemberCreate) => Promise<void>;
  onCancel: () => void;
}

export default function MemberForm({ initialData, onSubmit, onCancel }: MemberFormProps) {
  const [form, setForm] = useState<MemberCreate>({
    membership_id: initialData?.membership_id ?? '',
    full_name: initialData?.full_name ?? '',
    email: initialData?.email ?? '',
    phone: initialData?.phone ?? '',
    address: initialData?.address ?? '',
    status: initialData?.status ?? 'active',
    joined_date: initialData?.joined_date
      ? initialData.joined_date.slice(0, 10)
      : new Date().toISOString().slice(0, 10),
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof MemberCreate, string>>>({});

  function validate() {
    const e: Partial<Record<keyof MemberCreate, string>> = {};
    if (!form.membership_id.trim()) e.membership_id = 'Membership ID is required';
    if (!form.full_name.trim()) e.full_name = 'Full name is required';
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

  function set(field: keyof MemberCreate) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
    };
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Membership ID *"
          value={form.membership_id}
          onChange={set('membership_id')}
          error={errors.membership_id}
          placeholder="LIB-0001"
          disabled={!!initialData?.id}
        />
        <Input
          label="Full Name *"
          value={form.full_name}
          onChange={set('full_name')}
          error={errors.full_name}
          placeholder="Jane Doe"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Email"
          type="email"
          value={form.email ?? ''}
          onChange={set('email')}
          placeholder="jane@example.com"
        />
        <Input
          label="Phone"
          type="tel"
          value={form.phone ?? ''}
          onChange={set('phone')}
          placeholder="+1 555 0000"
        />
      </div>
      <Input
        label="Address"
        value={form.address ?? ''}
        onChange={set('address')}
        placeholder="123 Main St, Springfield"
      />
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            value={form.status ?? 'active'}
            onChange={set('status')}
            className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <Input
          label="Joined Date"
          type="date"
          value={form.joined_date ?? ''}
          onChange={set('joined_date')}
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={loading}>
          {initialData?.id ? 'Update Member' : 'Add Member'}
        </Button>
      </div>
    </form>
  );
}
