import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft, Download, Upload, CheckCircle2, AlertTriangle, XCircle, Copy,
  FileSpreadsheet, Loader2, PartyPopper,
} from "lucide-react";
import { importacionApi, type FilaImportacionPreview } from "../api/importacion";
import { useToast } from "../components/Toast";

const ESTADO_INFO: Record<string, { icon: typeof CheckCircle2; color: string; bg: string; label: string }> = {
  ok: { icon: CheckCircle2, color: "#6F8F57", bg: "#E7EDDF", label: "Listo para cargar" },
  advertencia: { icon: AlertTriangle, color: "#A8402E", bg: "#F5E0D9", label: "Con advertencia" },
  error: { icon: XCircle, color: "#B3261E", bg: "#FBEAEA", label: "No se puede cargar" },
  duplicado: { icon: Copy, color: "#8A7A6E", bg: "#F1E7DA", label: "Ya existe" },
};

export default function ImportarClientes() {
  const showToast = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [cargandoPreview, setCargandoPreview] = useState(false);
  const [preview, setPreview] = useState<FilaImportacionPreview[] | null>(null);
  const [nombreArchivo, setNombreArchivo] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [resultado, setResultado] = useState<{ creados: number; contratosCreados: number; omitidos: number } | null>(null);

  const importables = (preview ?? []).filter((f) => f.estado === "ok" || f.estado === "advertencia");
  const noImportables = (preview ?? []).filter((f) => f.estado === "error" || f.estado === "duplicado");

  const handleFile = async (file: File) => {
    setNombreArchivo(file.name);
    setResultado(null);
    setCargandoPreview(true);
    try {
      const datos = await importacionApi.previsualizar(file);
      setPreview(datos);
    } catch {
      showToast("No se pudo leer el archivo. Confirmá que sea el .xlsx descargado de acá y volvé a intentar.", "error");
      setPreview(null);
    } finally {
      setCargandoPreview(false);
    }
  };

  const handleConfirmar = async () => {
    setConfirmando(true);
    try {
      const resumen = await importacionApi.confirmar(importables.map((f) => f.datos));
      setResultado({ creados: resumen.creados, contratosCreados: resumen.contratos_creados, omitidos: resumen.omitidos });
      setPreview(null);
    } catch {
      showToast("No se pudo completar la carga. Probá de nuevo en un momento.", "error");
    } finally {
      setConfirmando(false);
    }
  };

  const reiniciar = () => {
    setPreview(null);
    setResultado(null);
    setNombreArchivo("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to="/clientes" className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
        <ArrowLeft size={15} /> Volver a clientes
      </Link>

      <div>
        <h1 className="text-xl font-extrabold text-ink">Importar clientes desde Excel</h1>
        <p className="text-sm text-muted mt-1">
          Cargá muchos clientes de una vez, eventuales o fijos, sin tipear uno por uno.
        </p>
      </div>

      {/* Pantalla de éxito final */}
      {resultado && (
        <div className="bg-card rounded-lg border border-border p-6 text-center">
          <PartyPopper className="mx-auto mb-3 text-success" size={40} strokeWidth={1.5} />
          <h2 className="text-lg font-extrabold text-ink">¡Listo!</h2>
          <p className="text-sm text-[#5B4A3D] mt-2">
            Se cargaron <span className="font-bold text-ink">{resultado.creados}</span> clientes
            {resultado.contratosCreados > 0 && (
              <> ({resultado.contratosCreados} con contrato fijo)</>
            )}.
            {resultado.omitidos > 0 && (
              <> {resultado.omitidos} fila(s) no se cargaron por errores o estar repetidas.</>
            )}
          </p>
          <div className="flex gap-2 justify-center mt-5">
            <button onClick={reiniciar} className="px-4 py-2 rounded-md text-sm font-semibold border border-border text-ink">
              Importar otro archivo
            </button>
            <Link to="/clientes" className="px-4 py-2 rounded-md text-sm font-semibold text-white bg-primary">
              Ver clientes
            </Link>
          </div>
        </div>
      )}

      {!resultado && (
        <>
          {/* Paso 1 */}
          <div className="bg-card rounded-lg border border-border p-5">
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full bg-primary text-white text-sm font-bold flex items-center justify-center shrink-0">1</div>
              <div className="flex-1">
                <h2 className="font-bold text-[15px] text-ink">Descargá la planilla</h2>
                <p className="text-sm text-muted mt-1">
                  Ya viene con las columnas armadas, dos ejemplos, y desplegables para no tener que
                  escribir "particular" o "mensual" a mano.
                </p>
                <a
                  href={importacionApi.plantillaUrl()}
                  className="inline-flex items-center gap-2 mt-3 text-sm font-semibold px-4 py-2 rounded-md border border-border text-primary hover:bg-primary/5 transition-colors"
                >
                  <Download size={16} /> Descargar planilla (.xlsx)
                </a>
              </div>
            </div>
          </div>

          {/* Paso 2 */}
          <div className="bg-card rounded-lg border border-border p-5">
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full bg-primary text-white text-sm font-bold flex items-center justify-center shrink-0">2</div>
              <div className="flex-1">
                <h2 className="font-bold text-[15px] text-ink">Completá y subí el archivo</h2>
                <p className="text-sm text-muted mt-1">
                  Solo el nombre es obligatorio. El resto lo podés dejar vacío si no lo tenés.
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFile(file);
                  }}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={cargandoPreview}
                  className="inline-flex items-center gap-2 mt-3 text-sm font-semibold px-4 py-2 rounded-md text-white bg-primary disabled:opacity-50"
                >
                  {cargandoPreview ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                  {cargandoPreview ? "Revisando el archivo…" : "Elegir archivo…"}
                </button>
                {nombreArchivo && !cargandoPreview && (
                  <p className="text-xs text-muted mt-2 flex items-center gap-1.5">
                    <FileSpreadsheet size={13} /> {nombreArchivo}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Paso 3: vista previa */}
          {preview && (
            <div className="bg-card rounded-lg border border-border p-5">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-7 h-7 rounded-full bg-primary text-white text-sm font-bold flex items-center justify-center shrink-0">3</div>
                <div>
                  <h2 className="font-bold text-[15px] text-ink">Revisá antes de confirmar</h2>
                  <p className="text-sm text-muted mt-1">
                    Nada se cargó todavía. Revisá la lista y confirmá cuando esté bien.
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#E7EDDF] text-success">
                  {importables.length} para cargar
                </span>
                {noImportables.length > 0 && (
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#FBEAEA] text-[#B3261E]">
                    {noImportables.length} no se van a cargar
                  </span>
                )}
              </div>

              {preview.length === 0 ? (
                <p className="text-sm text-muted py-4">
                  No se encontró ninguna fila con datos en el archivo. Revisá que hayas completado
                  la hoja "Clientes" de la planilla.
                </p>
              ) : (
                <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                  {preview.map((fila) => {
                    const info = ESTADO_INFO[fila.estado];
                    const Icon = info.icon;
                    return (
                      <div key={fila.fila} className="flex items-start gap-3 p-3 rounded-md" style={{ background: info.bg }}>
                        <Icon size={16} className="shrink-0 mt-0.5" style={{ color: info.color }} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-semibold text-ink">
                              {fila.datos.nombre || `Fila ${fila.fila} (sin nombre)`}
                            </span>
                            <span className="text-[11px] font-semibold px-1.5 py-0.5 rounded" style={{ color: info.color }}>
                              {info.label}
                            </span>
                            {fila.estado !== "error" && fila.estado !== "duplicado" && (
                              <span className="text-[11px] font-semibold px-1.5 py-0.5 rounded-full bg-card/60 text-muted">
                                {fila.es_fijo ? `Fijo — ${fila.servicio_resuelto}` : "Eventual"}
                              </span>
                            )}
                          </div>
                          {fila.mensajes.map((m, i) => (
                            <p key={i} className="text-xs mt-1" style={{ color: info.color }}>{m}</p>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {importables.length > 0 && (
                <button
                  onClick={handleConfirmar}
                  disabled={confirmando}
                  className="w-full mt-5 py-3 rounded-md font-semibold text-white bg-success disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {confirmando ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}
                  {confirmando ? "Cargando…" : `Confirmar carga de ${importables.length} cliente${importables.length === 1 ? "" : "s"}`}
                </button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
