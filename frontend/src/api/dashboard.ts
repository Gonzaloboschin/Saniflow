import { api } from "./client";
import type { KpisDashboard, PorServicio, PorTecnico, Periodo } from "../types";

export const dashboardApi = {
  kpis: (periodo: Periodo) => api.get<KpisDashboard>("/dashboard/kpis", { params: { periodo } }).then((r) => r.data),
  porServicio: (periodo: Periodo) =>
    api.get<PorServicio[]>("/dashboard/por-servicio", { params: { periodo } }).then((r) => r.data),
  porTecnico: (periodo: Periodo) =>
    api.get<PorTecnico[]>("/dashboard/por-tecnico", { params: { periodo } }).then((r) => r.data),
};
