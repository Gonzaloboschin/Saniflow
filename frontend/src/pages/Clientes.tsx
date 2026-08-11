import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Search, AlertTriangle, Users } from "lucide-react";
import { clientesApi } from "../api/clientes";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";

const TIPO_LABEL: Record<string, string> = { particular: "Particular", comercio: "Comercio", industria: "Industria" };

export default function Clientes() {
  const [q, setQ] = useState("");
  const { data: clientes, isLoading, isError, refetch } = useQuery({ queryKey: ["clientes", q], queryFn: () => clientesApi.listar(q || undefined) });
  const { data: enRiesgo } = useQuery({ queryKey: ["clientes-en-riesgo"], queryFn: clientesApi.enRiesgo });

  const idsEnRiesgo = new Set((enRiesgo ?? []).map((r) => r.cliente_id));

  if (isError) return <ErrorState onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      {enRiesgo && enRiesgo.length > 0 && (
        <div className="bg-[#FBEAE3] border border-warn/30 rounded-lg p-4">
          <div className="flex items-center gap-2 font-bold text-sm text-warn mb-2">
            <AlertTriangle size={16} /> {enRiesgo.length} {enRiesgo.length === 1 ? "cliente requiere" : "clientes requieren"} atención
          </div>
          <ul className="space-y-1 text-sm text-[#7A3A24]">
            {enRiesgo.map((r) => (
              <li key={`${r.cliente_id}-${r.motivo}`}>
                <Link to={`/clientes/${r.cliente_id}`} className="font-semibold underline">{r.cliente_nombre}</Link>: {r.detalle}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-faint" />
        <input
          className="w-full pl-9 pr-3 py-2.5 text-sm rounded-md border border-border outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="Buscar cliente por nombre…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="text-muted text-sm py-10 text-center">Cargando…</div>
      ) : !clientes || clientes.length === 0 ? (
        <EmptyState icon={Users} title="No se encontraron clientes." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {clientes.map((c) => (
            <Link
              key={c.id}
              to={`/clientes/${c.id}`}
              className="bg-white rounded-lg border border-border p-4 hover:border-primary/40 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-bold text-[15px] text-ink">{c.nombre}</div>
                  <div className="text-xs text-muted mt-0.5">{TIPO_LABEL[c.tipo]} · {c.localidad ?? "sin localidad"}</div>
                </div>
                {idsEnRiesgo.has(c.id) && (
                  <span className="flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#FBEAE3] text-warn shrink-0">
                    <AlertTriangle size={11} /> Riesgo
                  </span>
                )}
              </div>
              {c.telefono && <div className="text-sm text-[#4B5B54] mt-2">{c.telefono}</div>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
