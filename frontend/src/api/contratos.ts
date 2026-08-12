import { api } from "./client";
import type { Contrato } from "../types";

export const contratosApi = {
  porCliente: (clienteId: number) => api.get<Contrato[]>(`/contratos/cliente/${clienteId}`).then((r) => r.data),
};
