import React from 'react';
import { Box, Typography, IconButton, Badge, Tooltip } from '@mui/material';
import { Notifications as NotificationsIcon, AccountCircle as AccountIcon } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

const Header: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const { alerts } = useSelector((state: RootState) => state.alerts);
  const { isConnected } = useSelector((state: RootState) => state.websocket);

  const pendingAlerts = alerts.filter(alert => alert.status === 'pending').length;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
      <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
        Sistema de Segurança Inteligente
      </Typography>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: isConnected ? 'success.main' : 'error.main',
            }}
          />
          <Typography variant="body2" color="text.secondary">
            {isConnected ? 'Conectado' : 'Desconectado'}
          </Typography>
        </Box>

        <Tooltip title="Notificações">
          <IconButton color="inherit">
            <Badge badgeContent={pendingAlerts} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>

        <Tooltip title={user?.full_name || 'Usuário'}>
          <IconButton color="inherit">
            <AccountIcon />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Header;
