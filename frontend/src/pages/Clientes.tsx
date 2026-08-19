import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Search, AlertTriangle, Users, Upload, LayoutGrid, List, ChevronRight } from "lucide-react";
import { clientesApi } from "../api/clientes";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";

const TIPO_LABEL: Record<string, string> = { particular: "Particular", comercio: "Comercio", industria: "Industria" };
type Vista = "grilla" | "lista";

export default function Clientes() {
  const [q, setQ] = useState("");
  const [vista, setVista] = useState<Vista>("lista"); // lista por defecto: con 200+ clientes reales es lo más práctico
  const { data: clientes, isLoading, isError, refetch } = useQuery({ queryKey: ["clientes", q], queryFn: () => clientesApi.listar(q || undefined) });
  const { data: enRiesgo } = useQuery({ queryKey: ["clientes-en-riesgo"], queryFn: clientesApi.enRiesgo });

  const idsEnRiesgo = new Set((enRiesgo ?? []).map((r) => r.cliente_id));

  if (isError) return <ErrorState onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      {enRiesgo && enRiesgo.length > 0 && (
        <div className="bg-warn-soft border border-warn/30 rounded-lg p-4">
          <div className="flex items-center gap-2 font-bold text-sm text-warn mb-2">
            <AlertTriangle size={16} /> {enRiesgo.length} {enRiesgo.length === 1 ? "cliente requiere" : "clientes requieren"} atención
          </div>
          <ul className="space-y-1 text-sm text-warn/90">
            {enRiesgo.map((r) => (
              <li key={`${r.cliente_id}-${r.motivo}`}>
                <Link to={`/clientes/${r.cliente_id}`} className="font-semibold underline">{r.cliente_nombre}</Link>: {r.detalle}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-faint" />
          <input
            className="w-full pl-9 pr-3 py-2.5 text-sm rounded-md border border-border bg-card outline-none focus:ring-2 focus:ring-primary/25"
            placeholder="Buscar cliente por nombre…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        <div className="flex rounded-md border border-border overflow-hidden shrink-0">
          <button
            onClick={() => setVista("lista")}
            className={`p-2.5 transition-colors ${vista === "lista" ? "bg-primary text-white" : "bg-card text-muted hover:bg-surface-alt"}`}
            title="Ver en lista"
          >
            <List size={16} />
          </button>
          <button
            onClick={() => setVista("grilla")}
            className={`p-2.5 transition-colors border-l border-border ${vista === "grilla" ? "bg-primary text-white" : "bg-card text-muted hover:bg-surface-alt"}`}
            title="Ver en grilla"
          >
            <LayoutGrid size={16} />
          </button>
        </div>

        <Link
          to="/clientes/importar"
          className="flex items-center gap-1.5 text-sm font-semibold px-3 py-2 rounded-md border border-border bg-card text-primary hover:bg-primary-soft transition-colors shrink-0"
        >
          <Upload size={15} /> <span className="hidden sm:inline">Importar Excel</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm py-10 text-center">Cargando…</div>
      ) : !clientes || clientes.length === 0 ? (
        <EmptyState icon={Users} title="No se encontraron clientes." />
      ) : (
        <>
          <p className="text-xs text-muted">{clientes.length} cliente{clientes.length === 1 ? "" : "s"}</p>

          {vista === "lista" ? (
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              {clientes.map((c, i) => (
                <Link
                  key={c.id}
                  to={`/clientes/${c.id}`}
                  className={`flex items-center gap-3 px-4 py-3 hover:bg-surface-alt transition-colors ${i > 0 ? "border-t border-border" : ""}`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm text-ink truncate">{c.nombre}</span>
                      {idsEnRiesgo.has(c.id) && (
                        <span className="flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-warn-soft text-warn shrink-0">
                          <AlertTriangle size={9} /> Riesgo
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted truncate mt-0.5">
                      {TIPO_LABEL[c.tipo]}
                      {c.localidad ? ` · ${c.localidad}` : ""}
                      {c.telefono ? ` · ${c.telefono}` : ""}
                    </p>
                  </div>
                  <ChevronRight size={16} className="text-faint shrink-0" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3">
              {clientes.map((c) => (
                <Link
                  key={c.id}
                  to={`/clientes/${c.id}`}
                  className="bg-card rounded-lg border border-border p-4 hover:border-primary/40 hover:shadow-sm transition-all"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="font-bold text-[15px] text-ink truncate">{c.nombre}</div>
                      <div className="text-xs text-muted mt-0.5">{TIPO_LABEL[c.tipo]} · {c.localidad ?? "sin localidad"}</div>
                    </div>
                    {idsEnRiesgo.has(c.id) && (
                      <span className="flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-warn-soft text-warn shrink-0">
                        <AlertTriangle size={11} /> Riesgo
                      </span>
                    )}
                  </div>
                  {c.telefono && <div className="text-sm text-ink-soft mt-2">{c.telefono}</div>}
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
