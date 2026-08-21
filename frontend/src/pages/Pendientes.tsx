import { useState } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { Clock, User, CheckCircle2, X, Plus, AlertTriangle, CalendarDays, ClipboardList } from "lucide-react";
import { trabajosApi, type TrabajoCreatePayload, type TrabajoCompletarPayload } from "../api/trabajos";
import { clientesApi } from "../api/clientes";
import { serviciosApi } from "../api/servicios";
import { tecnicosApi } from "../api/tecnicos";
import { contratosApi } from "../api/contratos";
import type { Trabajo } from "../types";
import ServiceTag from "../components/ServiceTag";
import TipoTrabajoTag from "../components/TipoTrabajoTag";
import TipoTrabajoFilter, { type FiltroTipoTrabajo } from "../components/TipoTrabajoFilter";
import Modal from "../components/Modal";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import ConfirmDialog from "../components/ConfirmDialog";
import { useToast } from "../components/Toast";
import { diffMin, hoyISO, FRECUENCIA_LABEL } from "../lib/format";

export default function Pendientes() {
  const qc = useQueryClient();
  const [showNew, setShowNew] = useState(false);
  const [completando, setCompletando] = useState<Trabajo | null>(null);
  const [cancelando, setCancelando] = useState<Trabajo | null>(null);
  const [filtroTipo, setFiltroTipo] = useState<FiltroTipoTrabajo>("todos");

  const { data: trabajos, isLoading, isError, refetch } = useQuery({
    queryKey: ["trabajos", "pendiente"],
    queryFn: () => trabajosApi.listar("pendiente"),
  });

  const cancelar = useMutation({
    mutationFn: (id: number) => trabajosApi.cancelar(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["trabajos"] });
      setCancelando(null);
    },
  });

  if (isLoading) return <div className="text-muted text-sm py-10 text-center">Cargando…</div>;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const hoy = hoyISO();
  const filtrados = (trabajos ?? []).filter((t) => {
    if (filtroTipo === "eventual") return t.contrato_id == null;
    if (filtroTipo === "fijo") return t.contrato_id != null;
    return true;
  });
  const grupos = filtrados.reduce<Record<string, Trabajo[]>>((acc, t) => {
    (acc[t.fecha_programada] ??= []).push(t);
    return acc;
  }, {});

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <TipoTrabajoFilter value={filtroTipo} onChange={setFiltroTipo} />
        <button
          onClick={() => setShowNew(true)}
          className="flex items-center gap-1.5 text-sm font-semibold px-3 py-2 rounded-md text-white bg-primary transition-transform hover:scale-[1.03]"
        >
          <Plus size={16} /> Nuevo trabajo
        </button>
      </div>

      {Object.keys(grupos).length === 0 && (
        <EmptyState
          icon={ClipboardList}
          title={filtroTipo === "todos" ? "No hay visitas pendientes." : "No hay visitas pendientes de este tipo."}
          subtitle="Cargá un nuevo trabajo para verlo acá."
        />
      )}

      {Object.entries(grupos)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([fecha, lista]) => (
          <div key={fecha}>
            <div className="flex items-center gap-2 mb-3">
              <CalendarDays size={15} className="text-primary" />
              <h2 className="font-bold text-sm text-primary">{fecha === hoy ? "Hoy" : fecha}</h2>
              <div className="flex-1 h-px bg-border" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {lista
                .sort((a, b) => a.hora_programada.localeCompare(b.hora_programada))
                .map((t) => (
                  <JobCard key={t.id} trabajo={t} onComplete={() => setCompletando(t)} onCancel={() => setCancelando(t)} />
                ))}
            </div>
          </div>
        ))}

      {showNew && <NewJobModal onClose={() => setShowNew(false)} />}
      {completando && <CompleteModal trabajo={completando} onClose={() => setCompletando(null)} />}
      {cancelando && (
        <ConfirmDialog
          title="Cancelar visita"
          message={`¿Seguro que querés cancelar la visita de "${cancelando.cliente_nombre}" programada para las ${cancelando.hora_programada.slice(0, 5)} hs? Esta acción no se puede deshacer.`}
          confirmLabel="Sí, cancelar"
          danger
          onCancel={() => setCancelando(null)}
          onConfirm={() => cancelar.mutate(cancelando.id)}
        />
      )}
    </div>
  );
}

function JobCard({ trabajo, onComplete, onCancel }: { trabajo: Trabajo; onComplete: () => void; onCancel: () => void }) {
  const color = trabajo.servicio_color || "#BD5A38";
  return (
    <div className="ticket bg-card rounded-lg border overflow-hidden border-border">
      <div className="flex">
        <div className="w-1.5 shrink-0" style={{ background: color }} />
        <div className="flex-1 p-4">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <div className="mono text-[11px] font-bold" style={{ color }}>{trabajo.codigo}</div>
              <div className="font-bold text-[15px] text-ink">{trabajo.cliente_nombre}</div>
            </div>
            {trabajo.prioridad === "urgente" && (
              <span className="flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#F5E0D9] text-warn">
                <AlertTriangle size={11} /> Urgente
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 flex-wrap">
            <ServiceTag nombre={trabajo.servicio_nombre} color={trabajo.servicio_color} />
            <TipoTrabajoTag contratoId={trabajo.contrato_id} />
          </div>

          <div className="mt-3 space-y-1.5 text-sm text-[#5B4A3D]">
            <div className="flex items-center gap-2">
              <Clock size={14} className="shrink-0 text-faint" />
              {trabajo.hora_programada.slice(0, 5)} hs
              {trabajo.tecnico_nombre && (
                <>
                  <span className="mx-1 text-[#DCCBB8]">·</span>
                  <User size={14} className="shrink-0 text-faint" />
                  {trabajo.tecnico_nombre}
                </>
              )}
            </div>
            {trabajo.notas && <div className="text-[13px] italic pt-1 text-faint">"{trabajo.notas}"</div>}
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={onComplete}
              className="flex-1 flex items-center justify-center gap-1.5 text-sm font-semibold py-2 rounded-md text-white bg-primary transition-transform hover:scale-[1.02]"
            >
              <CheckCircle2 size={15} /> Marcar realizado
            </button>
            <button onClick={onCancel} className="px-3 rounded-md text-sm font-semibold border border-border text-warn" title="Cancelar visita">
              <X size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const inputCls = "w-full text-sm px-3 py-2 rounded-md border border-border outline-none focus:ring-2 focus:ring-primary/30 transition-shadow";

function NewJobModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { data: clientes } = useQuery({ queryKey: ["clientes"], queryFn: () => clientesApi.listar() });
  const { data: servicios } = useQuery({ queryKey: ["servicios"], queryFn: () => serviciosApi.listar() });
  const { data: tecnicos } = useQuery({ queryKey: ["tecnicos", "activos"], queryFn: () => tecnicosApi.listar(true) });

  const [form, setForm] = useState<TrabajoCreatePayload>({
    cliente_id: 0, servicio_id: 0, fecha_programada: hoyISO(), hora_programada: "09:00", prioridad: "normal",
  });

  const { data: contratosCliente } = useQuery({
    queryKey: ["contratos", form.cliente_id],
    queryFn: () => contratosApi.porCliente(form.cliente_id),
    enabled: form.cliente_id > 0,
  });
  const contratosActivos = (contratosCliente ?? []).filter((c) => c.activo);

  const crear = useMutation({
    mutationFn: () => trabajosApi.crear(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["trabajos"] });
      onClose();
    },
  });

  const valido = form.cliente_id > 0 && form.servicio_id > 0;

  return (
    <Modal title="Nuevo trabajo" onClose={onClose}>
      <div className="space-y-3">
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Cliente</span>
          <select
            className={inputCls}
            value={form.cliente_id}
            onChange={(e) => setForm({ ...form, cliente_id: Number(e.target.value), contrato_id: null })}
          >
            <option value={0}>Seleccionar…</option>
            {clientes?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Tipo de trabajo</span>
          <select
            className={inputCls}
            value={form.contrato_id ?? 0}
            disabled={form.cliente_id === 0}
            onChange={(e) => setForm({ ...form, contrato_id: Number(e.target.value) || null })}
          >
            <option value={0}>Eventual (sin contrato)</option>
            {contratosActivos.map((c) => (
              <option key={c.id} value={c.id}>
                Fijo — contrato #{c.id} ({FRECUENCIA_LABEL[c.frecuencia]})
              </option>
            ))}
          </select>
          {form.cliente_id > 0 && contratosActivos.length === 0 && (
            <p className="text-xs text-muted mt-1">Este cliente no tiene contratos activos — solo puede ser eventual.</p>
          )}
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Tipo de servicio</span>
          <select className={inputCls} value={form.servicio_id} onChange={(e) => setForm({ ...form, servicio_id: Number(e.target.value) })}>
            <option value={0}>Seleccionar…</option>
            {servicios?.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Fecha</span>
            <input type="date" className={inputCls} value={form.fecha_programada} onChange={(e) => setForm({ ...form, fecha_programada: e.target.value })} />
          </label>
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Hora</span>
            <input type="time" className={inputCls} value={form.hora_programada} onChange={(e) => setForm({ ...form, hora_programada: e.target.value })} />
          </label>
        </div>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Técnico</span>
          <select className={inputCls} value={form.tecnico_id ?? 0} onChange={(e) => setForm({ ...form, tecnico_id: Number(e.target.value) || undefined })}>
            <option value={0}>Sin asignar</option>
            {tecnicos?.map((t) => <option key={t.id} value={t.id}>{t.nombre}</option>)}
          </select>
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Prioridad</span>
          <select className={inputCls} value={form.prioridad} onChange={(e) => setForm({ ...form, prioridad: e.target.value as "normal" | "urgente" })}>
            <option value="normal">Normal</option>
            <option value="urgente">Urgente</option>
          </select>
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Notas (opcional)</span>
          <textarea className={inputCls} rows={2} value={form.notas ?? ""} onChange={(e) => setForm({ ...form, notas: e.target.value })} />
        </label>

        <button
          disabled={!valido || crear.isPending}
          onClick={() => crear.mutate()}
          className="w-full py-2.5 rounded-md font-semibold text-sm text-white mt-2 disabled:opacity-40 bg-primary"
        >
          {crear.isPending ? "Guardando…" : "Agregar a pendientes"}
        </button>
        {crear.isError && <p className="text-warn text-xs">No se pudo guardar. Revisá la conexión con la API.</p>}
      </div>
    </Modal>
  );
}

function CompleteModal({ trabajo, onClose }: { trabajo: Trabajo; onClose: () => void }) {
  const qc = useQueryClient();
  const showToast = useToast();
  const [form, setForm] = useState<TrabajoCompletarPayload>({
    hora_inicio: trabajo.hora_programada.slice(0, 5),
    hora_fin: "",
    monto: 0,
    costo: 0,
    detalle_trabajo: "",
  });
  const [etiquetasTexto, setEtiquetasTexto] = useState("");

  const completar = useMutation({
    mutationFn: () =>
      trabajosApi.completar(trabajo.id, {
        ...form,
        etiquetas: etiquetasTexto.split(",").map((e) => e.trim()).filter(Boolean),
      }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["trabajos"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      onClose();
      if (data.proximo_trabajo_generado) {
        showToast(
          `Trabajo confirmado. Como es un contrato recurrente, se agendó solo el próximo para el ${data.proximo_trabajo_generado.fecha_programada}.`,
          "success"
        );
      } else {
        showToast("Trabajo confirmado y movido a Realizados.", "success");
      }
    },
  });

  const valido = form.hora_inicio && form.hora_fin && form.monto > 0;

  return (
    <Modal title={`Confirmar trabajo — ${trabajo.codigo}`} onClose={onClose}>
      <div className="mb-3 p-3 rounded-md text-sm bg-surface">
        <div className="font-semibold text-ink">{trabajo.cliente_nombre}</div>
        <ServiceTag nombre={trabajo.servicio_nombre} color={trabajo.servicio_color} />
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Hora de inicio</span>
            <input type="time" className={inputCls} value={form.hora_inicio} onChange={(e) => setForm({ ...form, hora_inicio: e.target.value })} />
          </label>
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Hora de fin</span>
            <input type="time" className={inputCls} value={form.hora_fin} onChange={(e) => setForm({ ...form, hora_fin: e.target.value })} />
          </label>
        </div>
        {form.hora_inicio && form.hora_fin && (
          <div className="text-xs font-semibold text-primary">Duración: {diffMin(form.hora_inicio, form.hora_fin)} minutos</div>
        )}
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Monto cobrado ($)</span>
            <input type="number" className={inputCls} value={form.monto || ""} onChange={(e) => setForm({ ...form, monto: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Costo del servicio ($)</span>
            <input type="number" className={inputCls} value={form.costo || ""} onChange={(e) => setForm({ ...form, costo: Number(e.target.value) })} />
          </label>
        </div>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Detalle del trabajo realizado</span>
          <textarea className={inputCls} rows={3} value={form.detalle_trabajo} onChange={(e) => setForm({ ...form, detalle_trabajo: e.target.value })} placeholder="Producto aplicado, zonas tratadas, observaciones…" />
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-[#5B4A3D]">Etiquetas (opcional, separadas por coma)</span>
          <input className={inputCls} value={etiquetasTexto} onChange={(e) => setEtiquetasTexto(e.target.value)} placeholder="ej: reaparición cucarachas, acceso difícil" />
        </label>

        <button
          disabled={!valido || completar.isPending}
          onClick={() => completar.mutate()}
          className="w-full py-2.5 rounded-md font-semibold text-sm text-white mt-2 disabled:opacity-40 flex items-center justify-center gap-2 bg-success"
        >
          <CheckCircle2 size={16} /> {completar.isPending ? "Guardando…" : "Confirmar y mover a Realizados"}
        </button>
        {completar.isError && <p className="text-warn text-xs">No se pudo confirmar. Revisá la conexión con la API.</p>}
      </div>
    </Modal>
  );
}
