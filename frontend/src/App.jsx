import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Landing from './pages/Landing.jsx';
import AuthPage from './pages/AuthPage.jsx';
import NotFound from './pages/NotFound.jsx';

// Route-level code splitting: chart.js only loads when a chart page is opened.
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'));
const Resume = lazy(() => import('./pages/Resume.jsx'));
const Analysis = lazy(() => import('./pages/Analysis.jsx'));
const AnalysisDetail = lazy(() => import('./pages/AnalysisDetail.jsx'));
const Roadmap = lazy(() => import('./pages/Roadmap.jsx'));
const RoadmapDetail = lazy(() => import('./pages/RoadmapDetail.jsx'));
const Courses = lazy(() => import('./pages/Courses.jsx'));
const Profile = lazy(() => import('./pages/Profile.jsx'));

const Fallback = () => <div style={{ display: 'grid', placeItems: 'center', padding: 80 }}><div className="spinner dark" style={{ width: 26, height: 26 }} /></div>;

export default function App() {
  return (
    <Suspense fallback={<Fallback />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/resume" element={<Resume />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/analysis/:id" element={<AnalysisDetail />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/roadmap/:id" element={<RoadmapDetail />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}
