"use client";

interface Integration {
  id: number;
  type: string;
  status: string;
  connected_at: string | null;
  last_sync_at: string | null;
}

interface IntegrationCardProps {
  integration: Integration;
}

export default function IntegrationCard({ integration }: IntegrationCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "disconnected":
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400";
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatType = (type: string) => {
    return type
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-900 dark:text-white">
          {formatType(integration.type)}
        </h3>
        <span
          className={`px-2 py-1 rounded text-xs ${getStatusColor(
            integration.status
          )}`}
        >
          {integration.status}
        </span>
      </div>
      {integration.connected_at && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Connected: {new Date(integration.connected_at).toLocaleDateString()}
        </p>
      )}
      {integration.last_sync_at && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Last sync: {new Date(integration.last_sync_at).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}

