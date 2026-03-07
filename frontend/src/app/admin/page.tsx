"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { getAdminUsers, createAdminUser, updateAdminUser, deleteAdminUser } from "@/lib/api";
import type { AdminUser } from "@/lib/api";

export default function AdminPage() {
  const { t } = useLanguage();
  const { user, isAdmin } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "user" });
  const [error, setError] = useState("");

  const limit = 20;

  // Redirect non-admins
  useEffect(() => {
    if (user && !isAdmin) {
      router.replace("/");
    }
  }, [user, isAdmin, router]);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getAdminUsers({ page, limit, search: search || undefined });
      setUsers(data.users);
      setTotal(data.total);
    } catch {
      // If 403, redirect
      router.replace("/");
    } finally {
      setLoading(false);
    }
  }, [page, search, router]);

  useEffect(() => {
    if (isAdmin) fetchUsers();
  }, [isAdmin, fetchUsers]);

  // Debounced search
  useEffect(() => {
    setPage(1);
  }, [search]);

  const openCreate = () => {
    setEditingUser(null);
    setForm({ name: "", email: "", password: "", role: "user" });
    setError("");
    setShowModal(true);
  };

  const openEdit = (u: AdminUser) => {
    setEditingUser(u);
    setForm({ name: u.name, email: u.email, password: "", role: u.role });
    setError("");
    setShowModal(true);
  };

  const handleSave = async () => {
    setError("");
    try {
      if (editingUser) {
        await updateAdminUser(editingUser.id, {
          name: form.name || undefined,
          role: form.role || undefined,
        });
      } else {
        if (!form.email || !form.password || !form.name) {
          setError("All fields are required");
          return;
        }
        await createAdminUser({
          email: form.email,
          password: form.password,
          name: form.name,
          role: form.role,
        });
      }
      setShowModal(false);
      fetchUsers();
    } catch (e: any) {
      setError(e.message || "Error");
    }
  };

  const handleToggleActive = async (u: AdminUser) => {
    try {
      await updateAdminUser(u.id, { is_active: !u.is_active });
      fetchUsers();
    } catch {
      // ignore
    }
  };

  const handleDelete = async (u: AdminUser) => {
    if (!confirm(t.admin.confirmDelete)) return;
    try {
      await deleteAdminUser(u.id);
      fetchUsers();
    } catch {
      // ignore
    }
  };

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  const totalPages = Math.ceil(total / limit);

  return (
    <>
      <Header title={t.admin.title} />

      {/* Search + Add */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
        <input
          type="text"
          placeholder={t.admin.search}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full sm:w-80 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <button
          onClick={openCreate}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors whitespace-nowrap"
        >
          + {t.admin.addUser}
        </button>
      </div>

      {/* Users table */}
      {loading ? (
        <div className="card text-center py-12 text-gray-500">Loading...</div>
      ) : users.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">{t.admin.noUsers}</div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 text-left">
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.name}</th>
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.email}</th>
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.role}</th>
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.status}</th>
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.created}</th>
                <th className="py-3 px-3 font-medium text-gray-500 dark:text-gray-400">{t.admin.actions}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="py-3 px-3 text-gray-900 dark:text-gray-100 font-medium">{u.name}</td>
                  <td className="py-3 px-3 text-gray-600 dark:text-gray-300">{u.email}</td>
                  <td className="py-3 px-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      u.role === "admin"
                        ? "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
                        : "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
                    }`}>
                      {u.role === "admin" ? t.admin.admin : t.admin.user}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <button
                      onClick={() => handleToggleActive(u)}
                      disabled={u.id === user?.id}
                      className={`text-xs px-2 py-1 rounded-full font-medium cursor-pointer transition-colors ${
                        u.is_active
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 hover:bg-green-200"
                          : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 hover:bg-red-200"
                      } ${u.id === user?.id ? "opacity-50 cursor-not-allowed" : ""}`}
                    >
                      {u.is_active ? t.admin.active : t.admin.inactive}
                    </button>
                  </td>
                  <td className="py-3 px-3 text-gray-500 dark:text-gray-400 text-xs">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openEdit(u)}
                        className="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:hover:bg-blue-900/40 transition-colors"
                      >
                        {t.admin.editUser}
                      </button>
                      {u.id !== user?.id && (
                        <button
                          onClick={() => handleDelete(u)}
                          className="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/40 transition-colors"
                        >
                          {t.reports.delete}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500">{total} {t.admin.users}</p>
              <div className="flex gap-1">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i + 1}
                    onClick={() => setPage(i + 1)}
                    className={`px-3 py-1 rounded text-sm ${
                      page === i + 1
                        ? "bg-primary-600 text-white"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setShowModal(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              {editingUser ? t.admin.editUser : t.admin.addUser}
            </h3>

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.admin.name}</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>

              {!editingUser && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.admin.email}</label>
                    <input
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.admin.password}</label>
                    <input
                      type="password"
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      minLength={8}
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.admin.role}</label>
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="user">{t.admin.user}</option>
                  <option value="admin">{t.admin.admin}</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                {t.admin.cancel}
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                {t.admin.save}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
