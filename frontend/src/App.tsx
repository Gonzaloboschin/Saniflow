import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Pendientes from "./pages/Pendientes";
import Realizados from "./pages/Realizados";
import Clientes from "./pages/Clientes";
import ClienteDetalle from "./pages/ClienteDetalle";
import ImportarClientes from "./pages/ImportarClientes";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Pendientes />} />
        <Route path="realizados" element={<Realizados />} />
        <Route path="clientes" element={<Clientes />} />
        <Route path="clientes/importar" element={<ImportarClientes />} />
        <Route path="clientes/:id" element={<ClienteDetalle />} />
        <Route path="dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}
