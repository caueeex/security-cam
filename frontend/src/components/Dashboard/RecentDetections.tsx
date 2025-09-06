import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Chip } from '@mui/material';

const RecentDetections: React.FC = () => {
  // Mock data
  const detections = [
    { id: 1, type: 'Person', confidence: 0.95, time: '2 min atrás', camera: 'Câmera 1' },
    { id: 2, type: 'Vehicle', confidence: 0.87, time: '5 min atrás', camera: 'Câmera 2' },
    { id: 3, type: 'Anomaly', confidence: 0.92, time: '8 min atrás', camera: 'Câmera 1' },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Detecções Recentes
        </Typography>
        <List>
          {detections.map((detection) => (
            <ListItem key={detection.id} divider>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">{detection.type}</Typography>
                    <Chip
                      label={`${(detection.confidence * 100).toFixed(0)}%`}
                      color={detection.confidence > 0.9 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {detection.camera} • {detection.time}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default RecentDetections;
