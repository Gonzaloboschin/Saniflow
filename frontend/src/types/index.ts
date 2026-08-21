// Espejo de los schemas de app/schemas/*.py — si cambia el backend, empieza acá.

export type TipoCliente = "particular" | "comercio" | "industria";
export type EstadoCliente = "activo" | "en_riesgo" | "inactivo";
export type EstadoTrabajo = "pendiente" | "realizado" | "cancelado";
export type PrioridadTrabajo = "normal" | "urgente";
export type TipoInteraccion = "reclamo" | "consulta" | "llamado" | "otro";
export type FrecuenciaContrato =
  | "semanal" | "quincenal" | "mensual" | "trimestral" | "semestral" | "anual" | "a_demanda";

export interface Cliente {
  id: number;
  nombre: string;
  tipo: TipoCliente;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
  localidad: string | null;
  estado: EstadoCliente;
  notas: string | null;
  creado_en: string;
}

export interface ClienteConMetricas extends Cliente {
  total_trabajos_realizados: number;
  total_facturado: number;
  total_reclamos: number;
  ultimo_trabajo: string | null;
}

export interface Servicio {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  color: string;
  activo: boolean;
}

export interface Tecnico {
  id: number;
  nombre: string;
  telefono: string | null;
  email: string | null;
  activo: boolean;
}

export interface Contrato {
  id: number;
  cliente_id: number;
  servicio_id: number;
  frecuencia: FrecuenciaContrato;
  precio_acordado: number | null;
  fecha_inicio: string;
  fecha_fin: string | null;
  activo: boolean;
}

export interface Trabajo {
  id: number;
  codigo: string;
  cliente_id: number;
  servicio_id: number;
  tecnico_id: number | null;
  contrato_id: number | null;
  fecha_programada: string;
  hora_programada: string;
  prioridad: PrioridadTrabajo;
  notas: string | null;
  estado: EstadoTrabajo;
  hora_inicio: string | null;
  hora_fin: string | null;
  duracion_min: number | null;
  monto: number | null;
  costo: number | null;
  detalle_trabajo: string | null;
  fecha_realizado: string | null;
  creado_en: string;
  cliente_nombre: string | null;
  servicio_nombre: string | null;
  servicio_color: string | null;
  tecnico_nombre: string | null;
}

export interface Interaccion {
  id: number;
  cliente_id: number;
  trabajo_id: number | null;
  tipo: TipoInteraccion;
  fecha: string;
  motivo: string;
  descripcion: string | null;
  resuelto: boolean;
  resolucion: string | null;
  registrado_por: string | null;
}

export interface ProblemaRecurrente {
  etiqueta: string;
  ocurrencias: number;
}

export interface ClienteEnRiesgo {
  cliente_id: number;
  cliente_nombre: string;
  motivo: string;
  detalle: string;
}

export interface KpisDashboard {
  periodo: string;
  desde: string;
  hasta: string;
  trabajos_realizados: number;
  facturacion: number;
  costo: number;
  ganancia_neta: number;
  margen_pct: number;
  ticket_promedio: number;
  duracion_promedio_min: number;
  trabajos_eventuales: number;
  trabajos_fijos: number;
  facturacion_eventual: number;
  facturacion_fija: number;
  ticket_promedio_eventual: number;
  ticket_promedio_fijo: number;
  pct_ingresos_fijos: number;
  trabajos_cancelados: number;
  trabajos_programados_periodo: number;
  pct_cancelados: number;
}

export interface PorServicio {
  servicio: string;
  color: string;
  trabajos: number;
  facturacion: number;
}

export interface PorTecnico {
  tecnico: string;
  trabajos: number;
  facturacion: number;
}

export type Periodo = "semana" | "mes" | "anio";
