import type { LucideIcon } from "lucide-react";

export default function Kpi({
  icon: Icon, label, value, sub, accent = "#362A22", small,
}: {
  icon: LucideIcon; label: string; value: string | number; sub?: string; accent?: string; small?: boolean;
}) {
  return (
    <div className="bg-card rounded-lg border p-3.5 border-border">
      <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide mb-1.5 text-muted">
        <Icon size={13} /> {label}
      </div>
      <div className={small ? "text-lg font-bold" : "text-xl sm:text-2xl font-extrabold"} style={{ color: accent }}>
        {value}
      </div>
      {sub && <div className="text-xs font-semibold mt-0.5 text-muted">{sub}</div>}
    </div>
  );
}
