"use client";

import { useEffect, useState } from "react";
import DashboardStats from "../components/DashboardStats";
import IntegrationCard from "../components/IntegrationCard";

interface DashboardData {
  stats: {
    total_tools: number;
    active_tools: number;
    unknown_tools: number;
    suspected_duplicates: number;
    total_integrations: number;
    connected_integrations: number;
    last_scan_at: string;
  };
  recent_tools: Array<{
    id: number;
    name: string;
    status: string;
    last_seen_at: string | null;
  }>;
  integration_status: Array<{
    id: number;
    type: string;
    status: string;
    connected_at: string | null;
    last_sync_at: string | null;
  }>;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (!response.ok) {
          throw new Error("Failed to fetch dashboard data");
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
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading dashboard...</p>
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
          Dashboard
        </h1>

        {data && (
          <>
            <DashboardStats stats={data.stats} />

            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
                  Recent Tools
                </h2>
                <div className="space-y-2">
                  {data.recent_tools.length > 0 ? (
                    data.recent_tools.map((tool) => (
                      <div
                        key={tool.id}
                        className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded"
                      >
                        <span className="text-gray-900 dark:text-white">
                          {tool.name}
                        </span>
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            tool.status === "active"
                              ? "bg-green-100 text-green-800"
                              : tool.status === "unknown"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {tool.status}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500">No tools detected yet</p>
                  )}
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
                  Integrations
                </h2>
                <div className="space-y-4">
                  {data.integration_status.length > 0 ? (
                    data.integration_status.map((integration) => (
                      <IntegrationCard
                        key={integration.id}
                        integration={integration}
                      />
                    ))
                  ) : (
                    <p className="text-gray-500">No integrations connected</p>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

