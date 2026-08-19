import { api } from "./client";

export interface FilaImportacionDatos {
  nombre: string;
  tipo: string;
  telefono: string;
  email: string;
  direccion: string;
  localidad: string;
  notas: string;
  servicio: string;
  frecuencia: string;
  precio_acordado: string;
}

export type EstadoFilaImportacion = "ok" | "advertencia" | "error" | "duplicado";

export interface FilaImportacionPreview {
  fila: number;
  datos: FilaImportacionDatos;
  estado: EstadoFilaImportacion;
  mensajes: string[];
  tipo_resuelto: string;
  es_fijo: boolean;
  servicio_resuelto: string | null;
}

export interface ResumenImportacion {
  creados: number;
  contratos_creados: number;
  omitidos: number;
  detalles: FilaImportacionPreview[];
}

export const importacionApi = {
  plantillaUrl: () => `${api.defaults.baseURL}/clientes/importar/plantilla`,

  previsualizar: (archivo: File) => {
    const formData = new FormData();
    formData.append("archivo", archivo);
    return api
      .post<FilaImportacionPreview[]>("/clientes/importar/previsualizar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  confirmar: (filas: FilaImportacionDatos[]) =>
    api.post<ResumenImportacion>("/clientes/importar/confirmar", filas).then((r) => r.data),
};
