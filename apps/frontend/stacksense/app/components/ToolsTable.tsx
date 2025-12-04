"use client";

import { useState } from "react";
import UnknownToolBadge from "./UnknownToolBadge";
import DuplicateAlert from "./DuplicateAlert";

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

interface ToolsTableProps {
  tools: Tool[];
  onFilterChange?: (filter: string) => void;
}

export default function ToolsTable({ tools, onFilterChange }: ToolsTableProps) {
  const [filter, setFilter] = useState<string>("all");

  const handleFilterChange = (newFilter: string) => {
    setFilter(newFilter);
    if (onFilterChange) {
      onFilterChange(newFilter);
    }
  };

  const filteredTools =
    filter === "all"
      ? tools
      : tools.filter((tool) => tool.status === filter);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            SaaS Tools
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => handleFilterChange("all")}
              className={`px-4 py-2 rounded ${
                filter === "all"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              }`}
            >
              All
            </button>
            <button
              onClick={() => handleFilterChange("active")}
              className={`px-4 py-2 rounded ${
                filter === "active"
                  ? "bg-green-600 text-white"
                  : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              }`}
            >
              Active
            </button>
            <button
              onClick={() => handleFilterChange("unknown")}
              className={`px-4 py-2 rounded ${
                filter === "unknown"
                  ? "bg-yellow-600 text-white"
                  : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              }`}
            >
              Unknown
            </button>
            <button
              onClick={() => handleFilterChange("suspected_duplicate")}
              className={`px-4 py-2 rounded ${
                filter === "suspected_duplicate"
                  ? "bg-red-600 text-white"
                  : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              }`}
            >
              Duplicates
            </button>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Vendor
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Last Seen
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {filteredTools.length > 0 ? (
              filteredTools.map((tool) => (
                <tr key={tool.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {tool.name}
                      </span>
                      {tool.status === "unknown" && <UnknownToolBadge />}
                      {tool.status === "suspected_duplicate" && (
                        <DuplicateAlert toolId={tool.id} />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {tool.category || "—"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {tool.vendor || "—"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        tool.status === "active"
                          ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                          : tool.status === "unknown"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
                          : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                      }`}
                    >
                      {tool.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {tool.last_seen_at
                      ? new Date(tool.last_seen_at).toLocaleDateString()
                      : "—"}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                  No tools found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

