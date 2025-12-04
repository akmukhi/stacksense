"use client";

interface Stats {
  total_tools: number;
  active_tools: number;
  unknown_tools: number;
  suspected_duplicates: number;
  total_integrations: number;
  connected_integrations: number;
  last_scan_at: string;
}

interface DashboardStatsProps {
  stats: Stats;
}

export default function DashboardStats({ stats }: DashboardStatsProps) {
  const statCards = [
    {
      label: "Total Tools",
      value: stats.total_tools,
      color: "blue",
    },
    {
      label: "Active Tools",
      value: stats.active_tools,
      color: "green",
    },
    {
      label: "Unknown Tools",
      value: stats.unknown_tools,
      color: "yellow",
    },
    {
      label: "Suspected Duplicates",
      value: stats.suspected_duplicates,
      color: "red",
    },
    {
      label: "Connected Integrations",
      value: `${stats.connected_integrations}/${stats.total_integrations}`,
      color: "purple",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {statCards.map((stat, index) => (
        <div
          key={index}
          className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {stat.label}
          </p>
          <p
            className={`text-2xl font-bold ${
              stat.color === "blue"
                ? "text-blue-600"
                : stat.color === "green"
                ? "text-green-600"
                : stat.color === "yellow"
                ? "text-yellow-600"
                : stat.color === "red"
                ? "text-red-600"
                : "text-purple-600"
            }`}
          >
            {stat.value}
          </p>
        </div>
      ))}
    </div>
  );
}

