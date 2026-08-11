import Modal from "./Modal";

export default function ConfirmDialog({
  title,
  message,
  confirmLabel = "Confirmar",
  danger,
  onConfirm,
  onCancel,
}: {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <Modal title={title} onClose={onCancel}>
      <p className="text-sm text-[#4B5B54] mb-5">{message}</p>
      <div className="flex gap-2">
        <button
          onClick={onCancel}
          className="flex-1 py-2.5 rounded-md font-semibold text-sm border border-border text-ink hover:bg-surface transition-colors"
        >
          Volver
        </button>
        <button
          onClick={onConfirm}
          className={`flex-1 py-2.5 rounded-md font-semibold text-sm text-white ${danger ? "bg-warn" : "bg-primary"}`}
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
