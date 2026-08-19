export type FiltroTipoTrabajo = "todos" | "eventual" | "fijo";

const OPCIONES: { id: FiltroTipoTrabajo; label: string }[] = [
  { id: "todos", label: "Todos" },
  { id: "eventual", label: "Eventuales" },
  { id: "fijo", label: "Fijos" },
];

export default function TipoTrabajoFilter({
  value,
  onChange,
}: {
  value: FiltroTipoTrabajo;
  onChange: (v: FiltroTipoTrabajo) => void;
}) {
  return (
    <div className="flex gap-2">
      {OPCIONES.map((o) => (
        <button
          key={o.id}
          onClick={() => onChange(o.id)}
          className={`text-sm font-semibold px-3 py-1.5 rounded-md border transition-colors ${
            value === o.id
              ? "bg-primary border-primary text-white"
              : "bg-card border-border text-ink-soft hover:bg-surface-alt"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
