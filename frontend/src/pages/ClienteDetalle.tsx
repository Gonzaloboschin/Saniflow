import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Phone, MapPin, Mail, DollarSign, ClipboardList, AlertTriangle, MessageSquare, Repeat } from "lucide-react";
import { clientesApi } from "../api/clientes";
import ServiceTag from "../components/ServiceTag";
import TipoTrabajoTag from "../components/TipoTrabajoTag";
import Kpi from "../components/Kpi";
import ErrorState from "../components/ErrorState";
import { fmtMoney, fmtFecha } from "../lib/format";

const TIPO_INTERACCION_LABEL: Record<string, string> = {
  reclamo: "Reclamo", consulta: "Consulta", llamado: "Llamado", otro: "Otro",
};

export default function ClienteDetalle() {
  const { id } = useParams<{ id: string }>();
  const clienteId = Number(id);

  const { data: cliente, isError, refetch } = useQuery({ queryKey: ["cliente", clienteId], queryFn: () => clientesApi.obtener(clienteId) });
  const { data: historial } = useQuery({ queryKey: ["cliente", clienteId, "historial"], queryFn: () => clientesApi.historial(clienteId) });
  const { data: interacciones } = useQuery({ queryKey: ["cliente", clienteId, "interacciones"], queryFn: () => clientesApi.interacciones(clienteId) });
  const { data: problemas } = useQuery({ queryKey: ["cliente", clienteId, "problemas"], queryFn: () => clientesApi.problemasRecurrentes(clienteId) });

  if (isError) return <ErrorState onRetry={() => refetch()} />;
  if (!cliente) return <div className="text-muted text-sm py-10 text-center">Cargando…</div>;

  return (
    <div className="space-y-6">
      <Link to="/clientes" className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
        <ArrowLeft size={15} /> Volver a clientes
      </Link>

      <div className="bg-card rounded-lg border border-border p-5">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-xl font-extrabold text-ink">{cliente.nombre}</h1>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-[#5B4A3D] mt-2">
              {cliente.telefono && <span className="flex items-center gap-1.5"><Phone size={13} className="text-faint" />{cliente.telefono}</span>}
              {cliente.direccion && <span className="flex items-center gap-1.5"><MapPin size={13} className="text-faint" />{cliente.direccion}</span>}
              {cliente.email && <span className="flex items-center gap-1.5"><Mail size={13} className="text-faint" />{cliente.email}</span>}
            </div>
          </div>
          {cliente.estado === "en_riesgo" && (
            <span className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-[#F5E0D9] text-warn">
              <AlertTriangle size={12} /> En riesgo
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Kpi icon={ClipboardList} label="Trabajos realizados" value={cliente.total_trabajos_realizados} />
        <Kpi icon={DollarSign} label="Total facturado" value={fmtMoney(cliente.total_facturado)} accent="#BD5A38" />
        <Kpi icon={AlertTriangle} label="Reclamos" value={cliente.total_reclamos} accent={cliente.total_reclamos > 0 ? "#A8402E" : "#362A22"} />
        <Kpi icon={ClipboardList} label="Último trabajo" value={cliente.ultimo_trabajo ? fmtFecha(cliente.ultimo_trabajo) : "-"} small />
      </div>

      {problemas && problemas.length > 0 && (
        <div className="bg-card rounded-lg border border-border p-4">
          <h3 className="font-bold text-sm mb-3 flex items-center gap-2 text-ink">
            <Repeat size={15} className="text-warn" /> Problemas recurrentes
          </h3>
          <div className="flex flex-wrap gap-2">
            {problemas.map((p) => (
              <span key={p.etiqueta} className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#F5E0D9] text-warn">
                {p.etiqueta} · {p.ocurrencias}×
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="bg-card rounded-lg border border-border p-4">
        <h3 className="font-bold text-sm mb-3 text-ink">Historial de trabajos</h3>
        {!historial || historial.length === 0 ? (
          <p className="text-sm text-muted">Sin trabajos registrados todavía.</p>
        ) : (
          <div className="space-y-2">
            {historial.map((t) => (
              <div key={t.id} className="flex items-center justify-between gap-3 py-2 border-t border-[#F1E7DA] first:border-t-0 first:pt-0">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="mono text-[11px] font-bold text-primary shrink-0">{t.codigo}</span>
                  <ServiceTag nombre={t.servicio_nombre} color={t.servicio_color} />
                  <TipoTrabajoTag contratoId={t.contrato_id} />
                  <span className="text-xs text-muted shrink-0">
                    {t.estado === "realizado" ? fmtFecha(t.fecha_realizado) : `Programado ${fmtFecha(t.fecha_programada)}`}
                  </span>
                </div>
                <span className="text-sm font-semibold text-ink shrink-0">{t.monto ? fmtMoney(t.monto) : "-"}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-card rounded-lg border border-border p-4">
        <h3 className="font-bold text-sm mb-3 flex items-center gap-2 text-ink">
          <MessageSquare size={15} /> Interacciones y reclamos
        </h3>
        {!interacciones || interacciones.length === 0 ? (
          <p className="text-sm text-muted">Sin interacciones registradas todavía.</p>
        ) : (
          <div className="space-y-3">
            {interacciones.map((i) => (
              <div key={i.id} className="py-2 border-t border-[#F1E7DA] first:border-t-0 first:pt-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      i.tipo === "reclamo" ? "bg-[#F5E0D9] text-warn" : "bg-[#BD5A3818] text-primary"
                    }`}
                  >
                    {TIPO_INTERACCION_LABEL[i.tipo]}
                  </span>
                  <span className="text-xs text-muted">{fmtFecha(i.fecha.slice(0, 10))}</span>
                  {!i.resuelto && i.tipo === "reclamo" && (
                    <span className="text-[11px] font-bold text-warn">· Sin resolver</span>
                  )}
                </div>
                <p className="text-sm font-semibold text-ink mt-1">{i.motivo}</p>
                {i.descripcion && <p className="text-sm text-[#5B4A3D] mt-0.5">{i.descripcion}</p>}
                {i.resolucion && <p className="text-sm text-success mt-1">Resolución: {i.resolucion}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
