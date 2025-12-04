"use client";

import { useEffect, useState } from "react";
import IntegrationCard from "../components/IntegrationCard";

interface Integration {
  id: number;
  type: string;
  organization_id: number;
  status: string;
  connected_at: string | null;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
}

const INTEGRATION_TYPES = [
  { value: "google_workspace", label: "Google Workspace" },
  { value: "microsoft_365", label: "Microsoft 365" },
  { value: "slack", label: "Slack" },
  { value: "github", label: "GitHub" },
  { value: "jira", label: "Jira" },
  { value: "notion", label: "Notion" },
];

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/integrations");
      if (!response.ok) {
        throw new Error("Failed to fetch integrations");
      }
      const result = await response.json();
      setIntegrations(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (type: string) => {
    setConnecting(type);
    try {
      // For now, we'll use organization_id 1 as default
      // In production, this should come from user context
      const response = await fetch(
        `http://localhost:8000/api/integrations/${type}/connect?organization_id=1`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ organization_id: 1 }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to connect integration");
      }

      const result = await response.json();

      if (result.auth_url) {
        // Redirect to OAuth flow
        window.location.href = result.auth_url;
      } else {
        // Already connected
        fetchIntegrations();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect");
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (integrationId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/integrations/${integrationId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to disconnect integration");
      }

      fetchIntegrations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to disconnect");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading integrations...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Integrations
        </h1>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {INTEGRATION_TYPES.map((type) => {
            const existingIntegration = integrations.find(
              (i) => i.type === type.value
            );

            return (
              <div
                key={type.value}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  {type.label}
                </h3>

                {existingIntegration ? (
                  <>
                    <IntegrationCard integration={existingIntegration} />
                    <button
                      onClick={() => handleDisconnect(existingIntegration.id)}
                      className="mt-4 w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Disconnect
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleConnect(type.value)}
                    disabled={connecting === type.value}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    {connecting === type.value ? "Connecting..." : "Connect"}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

