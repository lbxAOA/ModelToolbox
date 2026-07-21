import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 开发模式下将 /api 与 /socket.io 转发到 Node 后端（默认 127.0.0.1:5678），
// 生产模式由后端直接托管本目录的构建产物，不需要代理。
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:5678",
      "/socket.io": {
        target: "http://127.0.0.1:5678",
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
  },
});
