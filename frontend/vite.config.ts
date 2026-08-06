import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  optimizeDeps: {
    exclude: ['leaflet.heat'],
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React core — cambia poco, caching largo
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Animaciones — separado para no bloquear React
          'vendor-motion': ['framer-motion'],
          // Recharts — el chunk más pesado, solo cuando se usan gráficas
          'vendor-charts': ['recharts'],
          // Mapa — carga solo al visitar la sección mapa
          'vendor-map': ['leaflet', 'react-leaflet'],
        },
      },
    },
    // Avisa si algún chunk supera 600 KB sin comprimir
    chunkSizeWarningLimit: 600,
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
