import React, { useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { fetchCameras } from '../../store/slices/cameraSlice';
import { fetchDetectionStats } from '../../store/slices/detectionSlice';
import { fetchAlertStats } from '../../store/slices/alertSlice';
import StatsCard from '../../components/Dashboard/StatsCard';
import CameraGrid from '../../components/Dashboard/CameraGrid';
import RecentDetections from '../../components/Dashboard/RecentDetections';
import RecentAlerts from '../../components/Dashboard/RecentAlerts';
import ActivityChart from '../../components/Dashboard/ActivityChart';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { cameras } = useSelector((state: RootState) => state.cameras);
  const { stats: detectionStats } = useSelector((state: RootState) => state.detections);
  const { stats: alertStats } = useSelector((state: RootState) => state.alerts);

  useEffect(() => {
    dispatch(fetchCameras());
    dispatch(fetchDetectionStats());
    dispatch(fetchAlertStats());
  }, [dispatch]);

  const onlineCameras = cameras.filter(camera => camera.is_online).length;
  const totalDetections = detectionStats?.total_detections || 0;
  const pendingAlerts = alertStats?.pending_alerts || 0;
  const accuracyRate = detectionStats?.accuracy_rate || 0;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        Dashboard
      </Typography>

      {/* Cards de Estatísticas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Câmeras Online"
            value={onlineCameras}
            total={cameras.length}
            icon="📹"
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Detecções Hoje"
            value={totalDetections}
            icon="🔍"
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Alertas Pendentes"
            value={pendingAlerts}
            icon="⚠️"
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Precisão"
            value={`${(accuracyRate * 100).toFixed(1)}%`}
            icon="🎯"
            color="success"
          />
        </Grid>
      </Grid>

      {/* Grid de Câmeras */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <CameraGrid cameras={cameras} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ActivityChart />
        </Grid>
      </Grid>

      {/* Detecções e Alertas Recentes */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <RecentDetections />
        </Grid>
        <Grid item xs={12} md={6}>
          <RecentAlerts />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
