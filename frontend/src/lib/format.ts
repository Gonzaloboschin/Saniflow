export const fmtMoney = (n: number | null | undefined) =>
  new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(n || 0);

export const fmtFecha = (iso: string | null | undefined) => {
  if (!iso) return "-";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("es-AR", { day: "2-digit", month: "2-digit", year: "numeric" });
};

export const fmtHora = (h: string | null | undefined) => (h ? h.slice(0, 5) : "-");

export const diffMin = (hi: string, hf: string) => {
  const [h1, m1] = hi.split(":").map(Number);
  const [h2, m2] = hf.split(":").map(Number);
  return Math.max(0, h2 * 60 + m2 - (h1 * 60 + m1));
};

export const hoyISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
