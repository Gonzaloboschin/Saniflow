import { AlertTriangle } from "lucide-react";

export default function ErrorState({
  message = "No se pudo conectar con el servidor.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="text-center py-20">
      <AlertTriangle className="mx-auto mb-3 text-warn" size={36} strokeWidth={1.5} />
      <p className="font-semibold text-ink">{message}</p>
      <p className="text-sm text-muted mt-1">Revisá que el backend esté corriendo y volvé a intentar.</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 text-sm font-semibold px-4 py-2 rounded-md border border-border text-primary hover:bg-primary/5 transition-colors"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
