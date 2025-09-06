import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Chip } from '@mui/material';

const RecentAlerts: React.FC = () => {
  // Mock data
  const alerts = [
    { id: 1, title: 'Intrusão Detectada', priority: 'High', time: '1 min atrás', camera: 'Câmera 1' },
    { id: 2, title: 'Movimento Suspeito', priority: 'Medium', time: '3 min atrás', camera: 'Câmera 2' },
    { id: 3, title: 'Objeto Abandonado', priority: 'Low', time: '7 min atrás', camera: 'Câmera 3' },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Alertas Recentes
        </Typography>
        <List>
          {alerts.map((alert) => (
            <ListItem key={alert.id} divider>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">{alert.title}</Typography>
                    <Chip
                      label={alert.priority}
                      color={getPriorityColor(alert.priority) as any}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="body2" color="text.secondary">
                    {alert.camera} • {alert.time}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default RecentAlerts;
