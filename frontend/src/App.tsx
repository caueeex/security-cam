import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import Cameras from './pages/Cameras/Cameras';
import Detections from './pages/Detections/Detections';
import Alerts from './pages/Alerts/Alerts';
import Analytics from './pages/Analytics/Analytics';
import Settings from './pages/Settings/Settings';
import Login from './pages/Login/Login';

import { useAuth } from './hooks/useAuth';
import { useWebSocket } from './hooks/useWebSocket';

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const { isConnected } = useWebSocket();

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <div className="loading-spinner" />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/cameras" element={<Cameras />} />
        <Route path="/detections" element={<Detections />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
};

export default App;
