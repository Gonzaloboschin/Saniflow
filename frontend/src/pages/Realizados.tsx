import { useQuery } from "@tanstack/react-query";
import { CheckCircle2 } from "lucide-react";
import { trabajosApi } from "../api/trabajos";
import ServiceTag from "../components/ServiceTag";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import { fmtMoney, fmtFecha } from "../lib/format";

export default function Realizados() {
  const { data: trabajos, isLoading, isError, refetch } = useQuery({
    queryKey: ["trabajos", "realizado"],
    queryFn: () => trabajosApi.listar("realizado"),
  });

  if (isLoading) return <div className="text-muted text-sm py-10 text-center">Cargando…</div>;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  if (!trabajos || trabajos.length === 0) {
    return <EmptyState icon={CheckCircle2} title="Todavía no hay trabajos realizados." />;
  }

  return (
    <div className="bg-white rounded-lg border overflow-hidden border-border">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wide font-bold text-faint bg-surface">
              <th className="px-4 py-3">Código</th>
              <th className="px-4 py-3">Cliente</th>
              <th className="px-4 py-3">Servicio</th>
              <th className="px-4 py-3">Fecha</th>
              <th className="px-4 py-3">Duración</th>
              <th className="px-4 py-3">Monto</th>
              <th className="px-4 py-3">Costo</th>
              <th className="px-4 py-3">Ganancia</th>
              <th className="px-4 py-3">Técnico</th>
            </tr>
          </thead>
          <tbody>
            {trabajos.map((t) => (
              <tr key={t.id} className="border-t border-[#EEF2F0]">
                <td className="px-4 py-3 mono text-[12px] font-semibold text-primary">{t.codigo}</td>
                <td className="px-4 py-3 font-semibold text-ink">{t.cliente_nombre}</td>
                <td className="px-4 py-3"><ServiceTag nombre={t.servicio_nombre} color={t.servicio_color} /></td>
                <td className="px-4 py-3 text-[#4B5B54]">{fmtFecha(t.fecha_realizado)}</td>
                <td className="px-4 py-3 text-[#4B5B54]">{t.duracion_min} min</td>
                <td className="px-4 py-3 font-semibold text-ink">{fmtMoney(t.monto)}</td>
                <td className="px-4 py-3 text-warn">{fmtMoney(t.costo)}</td>
                <td className="px-4 py-3 font-semibold text-success">{fmtMoney((t.monto ?? 0) - (t.costo ?? 0))}</td>
                <td className="px-4 py-3 text-[#4B5B54]">{t.tecnico_nombre ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
