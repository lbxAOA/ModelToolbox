import { io } from "socket.io-client";

// 同源部署（生产模式）时留空 URL 即可；开发模式下由 vite.config.js 代理 /socket.io。
export const socket = io({ autoConnect: true, transports: ["websocket", "polling"] });
