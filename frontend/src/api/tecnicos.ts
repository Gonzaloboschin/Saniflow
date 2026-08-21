import { api } from "./client";
import type { Tecnico } from "../types";

export interface TecnicoPayload {
  nombre: string;
  telefono?: string | null;
  email?: string | null;
}

export const tecnicosApi = {
  listar: (soloActivos = false) =>
    api.get<Tecnico[]>("/tecnicos", { params: { solo_activos: soloActivos } }).then((r) => r.data),
  crear: (data: TecnicoPayload) => api.post<Tecnico>("/tecnicos", data).then((r) => r.data),
  actualizar: (id: number, data: Partial<TecnicoPayload & { activo: boolean }>) =>
    api.patch<Tecnico>(`/tecnicos/${id}`, data).then((r) => r.data),
};
