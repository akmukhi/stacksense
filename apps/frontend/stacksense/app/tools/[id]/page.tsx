"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import UnknownToolBadge from "../../components/UnknownToolBadge";
import DuplicateAlert from "../../components/DuplicateAlert";

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

export default function ToolDetailPage() {
  const params = useParams();
  const toolId = params.id as string;
  const [tool, setTool] = useState<Tool | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTool = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/tools/${toolId}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch tool details");
        }
        const result = await response.json();
        setTool(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    if (toolId) {
      fetchTool();
    }
  }, [toolId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading tool details...</p>
      </div>
    );
  }

  if (error || !tool) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-lg bg-red-50 p-6 dark:bg-red-900/20">
          <p className="text-red-800 dark:text-red-200">
            Error: {error || "Tool not found"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <a
            href="/tools"
            className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
          >
            ← Back to Tools
          </a>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {tool.name}
            </h1>
            <div className="flex items-center gap-2">
              {tool.status === "unknown" && <UnknownToolBadge />}
              {tool.status === "suspected_duplicate" && (
                <DuplicateAlert toolId={tool.id} />
              )}
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  tool.status === "active"
                    ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                    : tool.status === "unknown"
                    ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
                    : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                }`}
              >
                {tool.status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Category
              </h3>
              <p className="text-lg text-gray-900 dark:text-white">
                {tool.category || "—"}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Vendor
              </h3>
              <p className="text-lg text-gray-900 dark:text-white">
                {tool.vendor || "—"}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                First Detected
              </h3>
              <p className="text-lg text-gray-900 dark:text-white">
                {new Date(tool.first_detected_at).toLocaleDateString()}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Last Seen
              </h3>
              <p className="text-lg text-gray-900 dark:text-white">
                {tool.last_seen_at
                  ? new Date(tool.last_seen_at).toLocaleDateString()
                  : "—"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

