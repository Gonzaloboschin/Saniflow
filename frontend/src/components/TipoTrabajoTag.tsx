import { Repeat } from "lucide-react";

export default function TipoTrabajoTag({ contratoId }: { contratoId: number | null }) {
  if (contratoId == null) {
    return (
      <span className="inline-flex items-center text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#EEF2F0] text-muted">
        Eventual
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#0F5C5618] text-primary">
      <Repeat size={11} /> Fijo
    </span>
  );
}
