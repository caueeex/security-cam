import React from 'react';
import { Card, CardContent, Typography, Box, Grid, Chip } from '@mui/material';
import { Camera } from '../../types';

interface CameraGridProps {
  cameras: Camera[];
}

const CameraGrid: React.FC<CameraGridProps> = ({ cameras }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Câmeras
        </Typography>
        <Grid container spacing={2}>
          {cameras.map((camera) => (
            <Grid item xs={12} sm={6} md={4} key={camera.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {camera.name}
                    </Typography>
                    <Chip
                      label={camera.is_online ? 'Online' : 'Offline'}
                      color={camera.is_online ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {camera.location}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {camera.ip_address}:{camera.port}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CameraGrid;
