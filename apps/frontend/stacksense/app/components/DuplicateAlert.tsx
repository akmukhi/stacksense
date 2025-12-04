"use client";

interface DuplicateAlertProps {
  toolId: number;
}

export default function DuplicateAlert({ toolId }: DuplicateAlertProps) {
  return (
    <span
      className="ml-2 px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full dark:bg-red-900/20 dark:text-red-400"
      title="This tool may be a duplicate of another tool"
    >
      Possible Duplicate
    </span>
  );
}

