import { api } from "./client";
import type { Servicio } from "../types";

export const serviciosApi = {
  listar: (soloActivos = true) =>
    api.get<Servicio[]>("/servicios", { params: { solo_activos: soloActivos } }).then((r) => r.data),
};
