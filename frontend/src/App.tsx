import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import PanoramaPage from './pages/PanoramaPage';
import BeneficiariosPage from './pages/BeneficiariosPage';
import InclusionPage from './pages/InclusionPage';
import OfertaPage from './pages/OfertaPage';
import MadurezPage from './pages/MadurezPage';
import CoberturaxPage from './pages/CoberturaxPage';
import MapaPage from './pages/MapaPage';
import IndicePage from './pages/IndicePage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/"              element={<PanoramaPage />} />
            <Route path="/beneficiarios" element={<BeneficiariosPage />} />
            <Route path="/inclusion"     element={<InclusionPage />} />
            <Route path="/oferta"        element={<OfertaPage />} />
            <Route path="/madurez"       element={<MadurezPage />} />
            <Route path="/cobertura"     element={<CoberturaxPage />} />
            <Route path="/mapa"          element={<MapaPage />} />
            <Route path="/indice"        element={<IndicePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
