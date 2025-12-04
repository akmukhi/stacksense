"use client";

export default function UnknownToolBadge() {
  return (
    <span
      className="ml-2 px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full dark:bg-yellow-900/20 dark:text-yellow-400"
      title="This tool was detected but not recognized"
    >
      Unknown
    </span>
  );
}

