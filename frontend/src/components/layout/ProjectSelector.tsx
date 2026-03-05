"use client";

import { useState, useEffect } from "react";
import { getProjects, createProject } from "@/lib/api";
import type { Project } from "@/lib/types";

interface ProjectSelectorProps {
  selected: string | null;
  onSelect: (id: string | null) => void;
}

export default function ProjectSelector({ selected, onSelect }: ProjectSelectorProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    const data = await getProjects().catch(() => []);
    setProjects(data);
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createProject({ name: newName, url: newUrl || undefined });
    setNewName("");
    setNewUrl("");
    setShowCreate(false);
    loadProjects();
  };

  return (
    <div className="p-4 border-t border-gray-200">
      <label className="text-xs font-medium text-gray-500 block mb-2">Du an</label>
      <select
        value={selected || ""}
        onChange={(e) => onSelect(e.target.value || null)}
        className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 bg-white"
      >
        <option value="">Tat ca du an</option>
        {projects.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
      <button
        onClick={() => setShowCreate(!showCreate)}
        className="mt-2 text-xs text-primary-600 hover:text-primary-800"
      >
        + Tao du an moi
      </button>
      {showCreate && (
        <div className="mt-2 space-y-2">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Ten du an"
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          />
          <input
            type="text"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            placeholder="URL (tuy chon)"
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          />
          <button onClick={handleCreate} className="btn-primary text-xs w-full">
            Tao
          </button>
        </div>
      )}
    </div>
  );
}
