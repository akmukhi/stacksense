"use client";

import { useEffect, useState } from "react";

interface ApiResponse {
  message: string;
  status?: string;
  framework?: string;
}

export default function Home() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/hello");
        if (!response.ok) {
          throw new Error("Failed to fetch data");
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

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center px-8 py-16">
        <div className="w-full max-w-2xl rounded-2xl bg-white p-8 shadow-xl dark:bg-gray-800">
          <h1 className="mb-8 text-center text-4xl font-bold text-gray-900 dark:text-white">
            FastAPI + Next.js
          </h1>
          
          <div className="space-y-6">
            <div className="rounded-lg bg-blue-50 p-6 dark:bg-gray-700">
              <h2 className="mb-4 text-xl font-semibold text-gray-800 dark:text-white">
                Backend Response
              </h2>
              
              {loading && (
                <p className="text-gray-600 dark:text-gray-300">
                  Loading...
                </p>
              )}
              
              {error && (
                <div className="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
                  <p className="text-red-800 dark:text-red-200">
                    Error: {error}
                  </p>
                  <p className="mt-2 text-sm text-red-600 dark:text-red-300">
                    Make sure the FastAPI server is running on http://localhost:8000
                  </p>
                </div>
              )}
              
              {data && !loading && (
                <div className="space-y-2">
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    {data.message}
                  </p>
                  {data.framework && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Framework: {data.framework}
                    </p>
                  )}
                  {data.status && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Status: {data.status}
                    </p>
                  )}
                </div>
              )}
            </div>
            
            <div className="rounded-lg bg-gray-50 p-6 dark:bg-gray-700">
              <h2 className="mb-4 text-xl font-semibold text-gray-800 dark:text-white">
                Tech Stack
              </h2>
              <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                <li>• <strong>Backend:</strong> FastAPI (Python)</li>
                <li>• <strong>Frontend:</strong> Next.js 16 (React 19)</li>
                <li>• <strong>Styling:</strong> Tailwind CSS 4</li>
                <li>• <strong>Language:</strong> TypeScript</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
