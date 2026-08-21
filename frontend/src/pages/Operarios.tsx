import { useState } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { Plus, Phone, Mail, Pencil, Power, Wrench } from "lucide-react";
import { tecnicosApi, type TecnicoPayload } from "../api/tecnicos";
import type { Tecnico } from "../types";
import Modal from "../components/Modal";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import { useToast } from "../components/Toast";

const inputCls = "w-full text-sm px-3 py-2 rounded-md border border-border bg-card outline-none focus:ring-2 focus:ring-primary/25";

export default function Operarios() {
  const qc = useQueryClient();
  const showToast = useToast();
  const [showNuevo, setShowNuevo] = useState(false);
  const [editando, setEditando] = useState<Tecnico | null>(null);

  const { data: tecnicos, isLoading, isError, refetch } = useQuery({
    queryKey: ["tecnicos", "todos"],
    queryFn: () => tecnicosApi.listar(false),
  });

  const toggleActivo = useMutation({
    mutationFn: (t: Tecnico) => tecnicosApi.actualizar(t.id, { activo: !t.activo }),
    onSuccess: (t) => {
      qc.invalidateQueries({ queryKey: ["tecnicos"] });
      showToast(t.activo ? `${t.nombre} reactivado.` : `${t.nombre} dado de baja.`, "info");
    },
  });

  if (isLoading) return <div className="text-muted text-sm py-10 text-center">Cargando…</div>;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const activos = (tecnicos ?? []).filter((t) => t.activo);
  const inactivos = (tecnicos ?? []).filter((t) => !t.activo);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <p className="text-sm text-muted">Quiénes hacen los trabajos en campo, y a quién avisar cuando se carga uno nuevo.</p>
        <button
          onClick={() => setShowNuevo(true)}
          className="flex items-center gap-1.5 text-sm font-semibold px-3 py-2 rounded-md text-white bg-primary transition-transform hover:scale-[1.03] shrink-0"
        >
          <Plus size={16} /> Nuevo operario
        </button>
      </div>

      {(!tecnicos || tecnicos.length === 0) ? (
        <EmptyState icon={Wrench} title="Todavía no cargaste ningún operario." subtitle="Agregalo para poder asignarle trabajos." />
      ) : (
        <div className="space-y-6">
          <div className="space-y-2">
            {activos.map((t) => (
              <TecnicoRow key={t.id} tecnico={t} onEdit={() => setEditando(t)} onToggle={() => toggleActivo.mutate(t)} />
            ))}
          </div>

          {inactivos.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-faint uppercase tracking-wide mb-2">Dados de baja</p>
              <div className="space-y-2 opacity-60">
                {inactivos.map((t) => (
                  <TecnicoRow key={t.id} tecnico={t} onEdit={() => setEditando(t)} onToggle={() => toggleActivo.mutate(t)} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {showNuevo && <TecnicoModal titulo="Nuevo operario" onClose={() => setShowNuevo(false)} />}
      {editando && <TecnicoModal titulo="Editar operario" tecnico={editando} onClose={() => setEditando(null)} />}
    </div>
  );
}

function TecnicoRow({ tecnico, onEdit, onToggle }: { tecnico: Tecnico; onEdit: () => void; onToggle: () => void }) {
  return (
    <div className="bg-card rounded-lg border border-border p-4 flex items-center gap-3 flex-wrap">
      <div className="min-w-0 flex-1">
        <div className="font-bold text-[15px] text-ink">{tecnico.nombre}</div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-soft mt-1">
          {tecnico.telefono && <span className="flex items-center gap-1.5"><Phone size={13} className="text-faint" />{tecnico.telefono}</span>}
          {tecnico.email && <span className="flex items-center gap-1.5"><Mail size={13} className="text-faint" />{tecnico.email}</span>}
          {!tecnico.telefono && !tecnico.email && <span className="text-faint italic">Sin datos de contacto</span>}
        </div>
      </div>
      <div className="flex gap-2 shrink-0">
        <button onClick={onEdit} className="p-2 rounded-md border border-border text-ink-soft hover:bg-surface-alt transition-colors" title="Editar">
          <Pencil size={15} />
        </button>
        <button
          onClick={onToggle}
          className={`p-2 rounded-md border transition-colors ${
            tecnico.activo ? "border-border text-warn hover:bg-warn-soft" : "border-border text-success hover:bg-success-soft"
          }`}
          title={tecnico.activo ? "Dar de baja" : "Reactivar"}
        >
          <Power size={15} />
        </button>
      </div>
    </div>
  );
}

function TecnicoModal({ titulo, tecnico, onClose }: { titulo: string; tecnico?: Tecnico; onClose: () => void }) {
  const qc = useQueryClient();
  const showToast = useToast();
  const [form, setForm] = useState<TecnicoPayload>({
    nombre: tecnico?.nombre ?? "",
    telefono: tecnico?.telefono ?? "",
    email: tecnico?.email ?? "",
  });

  const guardar = useMutation({
    mutationFn: () => (tecnico ? tecnicosApi.actualizar(tecnico.id, form) : tecnicosApi.crear(form)),
    onSuccess: (t) => {
      qc.invalidateQueries({ queryKey: ["tecnicos"] });
      showToast(tecnico ? `${t.nombre} actualizado.` : `${t.nombre} agregado como operario.`, "success");
      onClose();
    },
  });

  const valido = form.nombre.trim().length > 0;

  return (
    <Modal title={titulo} onClose={onClose}>
      <div className="space-y-3">
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-ink-soft">Nombre</span>
          <input className={inputCls} value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} placeholder="Nombre y apellido" />
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-ink-soft">Teléfono (opcional)</span>
          <input className={inputCls} value={form.telefono ?? ""} onChange={(e) => setForm({ ...form, telefono: e.target.value })} placeholder="260 4..." />
        </label>
        <label className="block">
          <span className="block text-xs font-semibold mb-1 text-ink-soft">Email (opcional)</span>
          <input
            type="email"
            className={inputCls}
            value={form.email ?? ""}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="para avisarle por mail cuando se le asigna un trabajo"
          />
        </label>

        <button
          disabled={!valido || guardar.isPending}
          onClick={() => guardar.mutate()}
          className="w-full py-2.5 rounded-md font-semibold text-sm text-white mt-2 disabled:opacity-40 bg-primary"
        >
          {guardar.isPending ? "Guardando…" : tecnico ? "Guardar cambios" : "Agregar operario"}
        </button>
        {guardar.isError && <p className="text-warn text-xs">No se pudo guardar. Revisá la conexión con la API.</p>}
      </div>
    </Modal>
  );
}
