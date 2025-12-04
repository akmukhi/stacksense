"use client";

import { useEffect, useState } from "react";
import ToolsTable from "../components/ToolsTable";

interface Tool {
  id: number;
  name: string;
  category: string | null;
  vendor: string | null;
  status: string;
  organization_id: number;
  first_detected_at: string;
  last_seen_at: string;
}

interface ToolsResponse {
  tools: Tool[];
  total: number;
  active_count: number;
  unknown_count: number;
  duplicate_count: number;
}

export default function ToolsPage() {
  const [data, setData] = useState<ToolsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = new URL("http://localhost:8000/api/tools");
        if (filter !== "all") {
          url.searchParams.append("status", filter);
        }

        const response = await fetch(url.toString());
        if (!response.ok) {
          throw new Error("Failed to fetch tools");
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filter]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading tools...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-lg bg-red-50 p-6 dark:bg-red-900/20">
          <p className="text-red-800 dark:text-red-200">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          SaaS Tools
        </h1>

        {data && (
          <>
            <div className="mb-4 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {data.total}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {data.active_count}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Unknown</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {data.unknown_count}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Duplicates</p>
                <p className="text-2xl font-bold text-red-600">
                  {data.duplicate_count}
                </p>
              </div>
            </div>

            <ToolsTable tools={data.tools} onFilterChange={setFilter} />
          </>
        )}
      </div>
    </div>
  );
}

