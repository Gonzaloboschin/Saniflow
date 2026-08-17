import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { ClipboardList, DollarSign, TrendingUp, Clock, Repeat, Users, XCircle } from "lucide-react";
import { dashboardApi } from "../api/dashboard";
import Kpi from "../components/Kpi";
import { fmtMoney } from "../lib/format";
import type { Periodo } from "../types";

const PERIODOS: { id: Periodo; label: string }[] = [
  { id: "semana", label: "Semana" },
  { id: "mes", label: "Mes" },
  { id: "anio", label: "Año" },
];

export default function Dashboard() {
  const [periodo, setPeriodo] = useState<Periodo>("mes");

  const { data: kpis } = useQuery({ queryKey: ["dashboard", "kpis", periodo], queryFn: () => dashboardApi.kpis(periodo) });
  const { data: porServicio } = useQuery({ queryKey: ["dashboard", "servicio", periodo], queryFn: () => dashboardApi.porServicio(periodo) });
  const { data: porTecnico } = useQuery({ queryKey: ["dashboard", "tecnico", periodo], queryFn: () => dashboardApi.porTecnico(periodo) });

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        {PERIODOS.map((p) => (
          <button
            key={p.id}
            onClick={() => setPeriodo(p.id)}
            className="text-sm font-semibold px-3 py-1.5 rounded-md border transition-colors"
            style={{
              borderColor: periodo === p.id ? "#0F5C56" : "#E4EAE7",
              background: periodo === p.id ? "#0F5C56" : "white",
              color: periodo === p.id ? "white" : "#4B5B54",
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      {kpis && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Kpi icon={ClipboardList} label="Trabajos" value={kpis.trabajos_realizados} />
          <Kpi icon={DollarSign} label="Facturación" value={fmtMoney(kpis.facturacion)} accent="#0F5C56" />
          <Kpi icon={TrendingUp} label="Ganancia neta" value={fmtMoney(kpis.ganancia_neta)} accent="#2F9E6E" sub={`${kpis.margen_pct.toFixed(0)}% margen`} />
          <Kpi icon={Clock} label="Duración promedio" value={`${Math.round(kpis.duracion_promedio_min)} min`} />
        </div>
      )}

      {kpis && (
        <div className="space-y-3">
          <h3 className="font-bold text-sm text-ink">Eventuales vs. Fijos</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Kpi icon={Users} label="Trabajos eventuales" value={kpis.trabajos_eventuales} />
            <Kpi icon={Repeat} label="Trabajos fijos" value={kpis.trabajos_fijos} accent="#0F5C56" />
            <Kpi
              icon={TrendingUp}
              label="Ingresos recurrentes"
              value={`${kpis.pct_ingresos_fijos.toFixed(0)}%`}
              accent="#2F9E6E"
              sub="del total facturado, viene de contratos fijos"
            />
            <Kpi
              icon={XCircle}
              label="Cancelaciones"
              value={kpis.trabajos_cancelados}
              accent={kpis.trabajos_cancelados > 0 ? "#C2542B" : "#16241F"}
              sub={
                kpis.trabajos_programados_periodo > 0
                  ? `${kpis.pct_cancelados.toFixed(0)}% de lo agendado en el período`
                  : "sin visitas agendadas todavía"
              }
            />
          </div>

          {(kpis.trabajos_eventuales > 0 || kpis.trabajos_fijos > 0) && (
            <div className="bg-white rounded-lg border border-border p-4">
              <h4 className="font-bold text-sm mb-3 text-ink">Facturación y ticket promedio por tipo</h4>
              <div className="space-y-3">
                <TipoBarRow
                  label="Eventuales"
                  facturacion={kpis.facturacion_eventual}
                  ticket={kpis.ticket_promedio_eventual}
                  max={Math.max(kpis.facturacion_eventual, kpis.facturacion_fija) || 1}
                  color="#8CA39A"
                />
                <TipoBarRow
                  label="Fijos"
                  facturacion={kpis.facturacion_fija}
                  ticket={kpis.ticket_promedio_fijo}
                  max={Math.max(kpis.facturacion_eventual, kpis.facturacion_fija) || 1}
                  color="#0F5C56"
                />
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3 bg-white rounded-lg border border-border p-4">
          <h3 className="font-bold text-sm mb-3 text-ink">Facturación por tipo de servicio</h3>
          {!porServicio || porServicio.length === 0 ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={porServicio}>
                <CartesianGrid stroke="#EEF2F0" vertical={false} />
                <XAxis dataKey="servicio" tick={{ fontSize: 10, fill: "#8CA39A" }} axisLine={{ stroke: "#DCE3DF" }} tickLine={false} interval={0} angle={-15} textAnchor="end" height={60} />
                <YAxis tick={{ fontSize: 11, fill: "#8CA39A" }} axisLine={false} tickLine={false} width={40} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                <Tooltip formatter={(v) => fmtMoney(Number(v))} contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "#E4EAE7" }} />
                <Bar dataKey="facturacion" radius={[4, 4, 0, 0]}>
                  {porServicio.map((s, i) => <Cell key={i} fill={s.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg border border-border p-4">
          <h3 className="font-bold text-sm mb-3 text-ink">Distribución por servicio</h3>
          {!porServicio || porServicio.length === 0 ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={porServicio} dataKey="facturacion" nameKey="servicio" innerRadius={45} outerRadius={80} paddingAngle={2}>
                  {porServicio.map((s, i) => <Cell key={i} fill={s.color} />)}
                </Pie>
                <Tooltip formatter={(v) => fmtMoney(Number(v))} contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "#E4EAE7" }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-border p-4">
        <h3 className="font-bold text-sm mb-3 text-ink">Rendimiento por técnico</h3>
        {!porTecnico || porTecnico.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="space-y-2">
            {porTecnico.map((t) => (
              <div key={t.tecnico} className="flex items-center gap-3">
                <div className="w-32 text-sm font-semibold shrink-0 text-ink">{t.tecnico}</div>
                <div className="flex-1 h-2 rounded-full bg-[#EEF2F0]">
                  <div
                    className="h-2 rounded-full bg-primary"
                    style={{ width: `${Math.min(100, (t.facturacion / (porTecnico[0].facturacion || 1)) * 100)}%` }}
                  />
                </div>
                <div className="text-xs mono w-16 text-right text-[#4B5B54]">{t.trabajos} trab.</div>
                <div className="text-sm font-semibold w-24 text-right text-ink">{fmtMoney(t.facturacion)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyChart() {
  return <div className="h-[240px] flex items-center justify-center text-sm text-faint">Sin datos en este período todavía.</div>;
}

function TipoBarRow({
  label, facturacion, ticket, max, color,
}: {
  label: string; facturacion: number; ticket: number; max: number; color: string;
}) {
  return (
    <div className="flex items-center gap-3 flex-wrap sm:flex-nowrap">
      <div className="w-20 text-sm font-semibold shrink-0 text-ink">{label}</div>
      <div className="flex-1 min-w-[80px] h-2 rounded-full bg-[#EEF2F0]">
        <div
          className="h-2 rounded-full transition-all"
          style={{ width: `${Math.min(100, (facturacion / max) * 100)}%`, background: color }}
        />
      </div>
      <div className="text-sm font-semibold w-24 text-right shrink-0 text-ink">{fmtMoney(facturacion)}</div>
      <div className="text-xs mono shrink-0 text-muted">ticket prom. {fmtMoney(ticket)}</div>
    </div>
  );
}
