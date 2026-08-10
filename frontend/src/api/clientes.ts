import { api } from "./client";
import type { Cliente, ClienteConMetricas, ClienteEnRiesgo, Trabajo, Interaccion, ProblemaRecurrente } from "../types";

export const clientesApi = {
  listar: (q?: string) => api.get<Cliente[]>("/clientes", { params: { q } }).then((r) => r.data),
  obtener: (id: number) => api.get<ClienteConMetricas>(`/clientes/${id}`).then((r) => r.data),
  crear: (data: Partial<Cliente>) => api.post<Cliente>("/clientes", data).then((r) => r.data),
  enRiesgo: () => api.get<ClienteEnRiesgo[]>("/clientes/en-riesgo").then((r) => r.data),
  historial: (id: number) => api.get<Trabajo[]>(`/clientes/${id}/historial`).then((r) => r.data),
  interacciones: (id: number) => api.get<Interaccion[]>(`/clientes/${id}/interacciones`).then((r) => r.data),
  problemasRecurrentes: (id: number) =>
    api.get<ProblemaRecurrente[]>(`/clientes/${id}/problemas-recurrentes`).then((r) => r.data),
};
