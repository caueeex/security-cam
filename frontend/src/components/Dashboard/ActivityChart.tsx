import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

const ActivityChart: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Atividade das Últimas 24h
        </Typography>
        <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Gráfico de atividade será implementado aqui
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ActivityChart;
