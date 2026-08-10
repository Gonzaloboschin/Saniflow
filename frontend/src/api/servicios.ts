import { api } from "./client";
import type { Servicio, Tecnico } from "../types";

export const serviciosApi = {
  listar: (soloActivos = true) =>
    api.get<Servicio[]>("/servicios", { params: { solo_activos: soloActivos } }).then((r) => r.data),
};

export const tecnicosApi = {
  listar: (soloActivos = true) =>
    api.get<Tecnico[]>("/tecnicos", { params: { solo_activos: soloActivos } }).then((r) => r.data),
};
