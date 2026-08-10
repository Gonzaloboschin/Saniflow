export default function ServiceTag({ nombre, color }: { nombre: string | null; color: string | null }) {
  if (!nombre) return null;
  const c = color || "#0F5C56";
  return (
    <span
      className="inline-flex items-center gap-1.5 text-xs font-semibold px-2 py-1 rounded-full"
      style={{ background: c + "18", color: c }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: c }} />
      {nombre}
    </span>
  );
}
