// -- Router y loading por pagina --

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from './components/layout';
import { ROUTES } from './constants/routes';
import { Skeleton } from './components/ui';

// Lazy loading
const Overview     = lazy(() => import('./pages/Overview').then(m => ({ default: m.Overview })));
const Beneficiaries = lazy(() => import('./pages/Beneficiaries').then(m => ({ default: m.Beneficiaries })));
const Inclusion    = lazy(() => import('./pages/Inclusion').then(m => ({ default: m.Inclusion })));
const STEMOffer    = lazy(() => import('./pages/STEMOffer').then(m => ({ default: m.STEMOffer })));
const Maturity     = lazy(() => import('./pages/Maturity').then(m => ({ default: m.Maturity })));
const MapPage      = lazy(() => import('./pages/Map').then(m => ({ default: m.MapPage })));
const Gaps         = lazy(() => import('./pages/Gaps').then(m => ({ default: m.Gaps })));
const Admin        = lazy(() => import('./pages/Admin').then(m => ({ default: m.Admin })));

function PageLoader() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, padding: 32 }}>
      <Skeleton width="40%" height="32px" />
      <Skeleton width="20%" height="16px" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 16 }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} height="100px" />
        ))}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route
            path={ROUTES.OVERVIEW}
            element={
              <Suspense fallback={<PageLoader />}>
                <Overview />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.BENEFICIARIES}
            element={
              <Suspense fallback={<PageLoader />}>
                <Beneficiaries />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.INCLUSION}
            element={
              <Suspense fallback={<PageLoader />}>
                <Inclusion />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.STEM_OFFER}
            element={
              <Suspense fallback={<PageLoader />}>
                <STEMOffer />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.MATURITY}
            element={
              <Suspense fallback={<PageLoader />}>
                <Maturity />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.MAP}
            element={
              <Suspense fallback={<PageLoader />}>
                <MapPage />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.GAPS}
            element={
              <Suspense fallback={<PageLoader />}>
                <Gaps />
              </Suspense>
            }
          />
          <Route
            path={ROUTES.ADMIN}
            element={
              <Suspense fallback={<PageLoader />}>
                <Admin />
              </Suspense>
            }
          />
          {/* Fallback */}
          <Route path="*" element={<Navigate to={ROUTES.OVERVIEW} replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
