import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': { target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000', changeOrigin: true } },
  },
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        // long-lived vendor chunks => better caching between deploys
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
          motion: ['framer-motion'],
          charts: ['chart.js', 'react-chartjs-2'],
        },
      },
    },
  },
});
