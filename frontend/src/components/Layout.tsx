import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Sparkles, Menu, X, ClipboardList, CheckCircle2, Users, BarChart3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { trabajosApi } from "../api/trabajos";

const NAV = [
  { to: "/", label: "Pendientes", end: true, icon: ClipboardList },
  { to: "/realizados", label: "Realizados", icon: CheckCircle2 },
  { to: "/clientes", label: "Clientes", icon: Users },
  { to: "/dashboard", label: "Estadísticas", icon: BarChart3 },
];

const TITULOS: Record<string, string> = {
  "/": "Pendientes",
  "/realizados": "Trabajos realizados",
  "/clientes": "Clientes",
  "/dashboard": "Estadísticas",
};

function tituloDePagina(pathname: string): string {
  if (TITULOS[pathname]) return TITULOS[pathname];
  if (pathname.startsWith("/clientes/importar")) return "Importar clientes";
  if (pathname.startsWith("/clientes/")) return "Ficha de cliente";
  return "SaniFlow";
}

export default function Layout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const location = useLocation();

  const { data: pendientes } = useQuery({
    queryKey: ["trabajos", "pendiente"],
    queryFn: () => trabajosApi.listar("pendiente"),
    refetchInterval: 60_000,
  });

  return (
    <div className="min-h-screen bg-surface flex">
      {/* Sidebar — fija en desktop, cajón deslizable en mobile */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border flex flex-col transition-transform duration-200 md:translate-x-0 ${
          menuAbierto ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="px-5 pt-6 pb-5 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shrink-0">
                <Sparkles size={16} className="text-white" />
              </div>
              <span className="font-display font-semibold text-lg text-ink">SaniFlow</span>
            </div>
            <button className="md:hidden text-muted" onClick={() => setMenuAbierto(false)}>
              <X size={20} />
            </button>
          </div>
          <p className="text-xs text-muted mt-1.5 ml-10">Desinfecciones</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                onClick={() => setMenuAbierto(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                    isActive ? "bg-primary-soft text-primary" : "text-ink-soft hover:bg-surface-alt"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={17} className={isActive ? "text-primary" : "text-faint"} />
                    {item.label}
                    {item.to === "/" && pendientes && pendientes.length > 0 && (
                      <span
                        className={`ml-auto mono text-[11px] font-bold px-1.5 py-0.5 rounded ${
                          isActive ? "bg-card text-primary" : "bg-surface-alt text-muted"
                        }`}
                      >
                        {pendientes.length}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="px-5 py-4 border-t border-border">
          <p className="text-[11px] text-faint">Control de trabajos</p>
        </div>
      </aside>

      {/* Fondo oscuro al abrir el menú en mobile */}
      {menuAbierto && (
        <div className="fixed inset-0 bg-ink/30 z-30 md:hidden" onClick={() => setMenuAbierto(false)} />
      )}

      {/* Contenido principal */}
      <div className="flex-1 md:ml-64 min-w-0">
        <header className="sticky top-0 z-20 bg-surface/90 backdrop-blur-sm border-b border-border px-4 sm:px-8 py-4 flex items-center gap-3">
          <button className="md:hidden text-ink" onClick={() => setMenuAbierto(true)}>
            <Menu size={22} />
          </button>
          <h1 className="font-display text-xl sm:text-2xl font-semibold text-ink">
            {tituloDePagina(location.pathname)}
          </h1>
        </header>

        <main className="px-4 sm:px-8 py-6 w-full max-w-[1600px]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
