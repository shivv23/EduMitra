"use client";

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center animate-fade-in">
      <span className="text-6xl mb-4 block animate-float">{icon}</span>
      <h3 className="text-xl font-semibold text-surface-200 mb-2">{title}</h3>
      <p className="text-sm text-surface-400 max-w-sm mb-6">{description}</p>
      {action && (
        <button onClick={action.onClick} className="btn-primary text-sm glow">
          {action.label}
        </button>
      )}
    </div>
  );
}
