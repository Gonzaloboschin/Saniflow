import axios from "axios";

// En WSL, si accedés desde el navegador de Windows y localhost no resuelve,
// reemplazar VITE_API_URL en .env por la IP que devuelve `hostname -I`.
const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });
