import { api } from "./client";
import type { Trabajo, EstadoTrabajo } from "../types";

export interface TrabajoCreatePayload {
  cliente_id: number;
  servicio_id: number;
  tecnico_id?: number | null;
  contrato_id?: number | null;
  fecha_programada: string;
  hora_programada: string;
  prioridad?: "normal" | "urgente";
  notas?: string;
}

export interface TrabajoCompletarPayload {
  hora_inicio: string;
  hora_fin: string;
  monto: number;
  costo: number;
  detalle_trabajo?: string;
  etiquetas?: string[];
}

export const trabajosApi = {
  listar: (estado?: EstadoTrabajo) =>
    api.get<Trabajo[]>("/trabajos", { params: { estado } }).then((r) => r.data),
  crear: (data: TrabajoCreatePayload) => api.post<Trabajo>("/trabajos", data).then((r) => r.data),
  completar: (id: number, data: TrabajoCompletarPayload) =>
    api.post<{ trabajo: Trabajo; proximo_trabajo_generado: Trabajo | null }>(
      `/trabajos/${id}/completar`, data
    ).then((r) => r.data),
  cancelar: (id: number) => api.post<Trabajo>(`/trabajos/${id}/cancelar`).then((r) => r.data),
};
