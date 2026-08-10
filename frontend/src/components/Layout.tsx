import { NavLink, Outlet } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { trabajosApi } from "../api/trabajos";

const NAV = [
  { to: "/", label: "Pendientes", end: true },
  { to: "/realizados", label: "Realizados" },
  { to: "/clientes", label: "Clientes" },
  { to: "/dashboard", label: "Estadísticas" },
];

export default function Layout() {
  const { data: pendientes } = useQuery({
    queryKey: ["trabajos", "pendiente"],
    queryFn: () => trabajosApi.listar("pendiente"),
    refetchInterval: 60_000,
  });

  return (
    <div className="min-h-screen bg-surface">
      <header
        className="px-4 sm:px-8 pt-6 pb-4"
        style={{ background: "linear-gradient(135deg, #0F5C56 0%, #0B4440 100%)" }}
      >
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-2 text-white/70 text-xs font-semibold tracking-widest uppercase mb-1">
            <Sparkles size={13} /> SaniFlow
          </div>
          <h1 className="text-white text-2xl sm:text-3xl font-extrabold tracking-tight">
            Desinfecciones — Control de trabajos
          </h1>
          <p className="text-white/60 text-sm mt-1">
            {pendientes?.length ?? "…"} {pendientes?.length === 1 ? "visita pendiente" : "visitas pendientes"}
          </p>
        </div>
      </header>

      <nav className="flex gap-1 px-4 sm:px-8 border-b border-border bg-white sticky top-0 z-10 overflow-x-auto">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `relative px-4 py-3 text-sm font-semibold whitespace-nowrap transition-colors ${
                isActive ? "text-primary" : "text-muted"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {item.label}
                {isActive && <div className="absolute left-0 right-0 -bottom-px h-[2px] bg-primary" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <main className="px-4 sm:px-8 py-6 max-w-6xl mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
