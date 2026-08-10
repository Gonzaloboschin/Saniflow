import type { LucideIcon } from "lucide-react";

export default function EmptyState({ icon: Icon, title, subtitle }: { icon: LucideIcon; title: string; subtitle?: string }) {
  return (
    <div className="text-center py-20 text-muted">
      <Icon className="mx-auto mb-3" size={36} strokeWidth={1.5} />
      <p className="font-semibold">{title}</p>
      {subtitle && <p className="text-sm mt-1">{subtitle}</p>}
    </div>
  );
}
