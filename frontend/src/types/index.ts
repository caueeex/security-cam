// Tipos principais do sistema

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
}

export enum UserRole {
  ADMIN = 'admin',
  OPERATOR = 'operator',
  VIEWER = 'viewer'
}

export interface Camera {
  id: number;
  name: string;
  description?: string;
  location: string;
  ip_address: string;
  port: number;
  stream_url: string;
  username?: string;
  password?: string;
  resolution: string;
  frame_rate: number;
  codec: string;
  detection_enabled: boolean;
  confidence_threshold: number;
  motion_sensitivity: number;
  is_active: boolean;
  is_online: boolean;
  last_heartbeat?: string;
  last_error?: string;
  created_at: string;
  updated_at?: string;
}

export interface Detection {
  id: number;
  camera_id: number;
  detection_type: string;
  confidence_score: number;
  anomaly_score?: number;
  bounding_box?: BoundingBox;
  center_point?: Point;
  frame_timestamp: string;
  frame_number?: number;
  image_path?: string;
  video_path?: string;
  model_version?: string;
  processing_time_ms?: number;
  object_class?: string;
  behavior_type?: string;
  risk_level: RiskLevel;
  is_verified: boolean;
  is_false_positive: boolean;
  verification_notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface Alert {
  id: number;
  camera_id: number;
  detection_id?: number;
  alert_type: string;
  title: string;
  description?: string;
  priority: AlertPriority;
  status: AlertStatus;
  detection_data?: any;
  image_url?: string;
  video_url?: string;
  location?: string;
  coordinates?: Coordinates;
  email_sent: boolean;
  sms_sent: boolean;
  push_notification_sent: boolean;
  resolved_at?: string;
  resolved_by?: string;
  resolution_notes?: string;
  created_at: string;
  updated_at?: string;
}

export enum AlertPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum AlertStatus {
  PENDING = 'pending',
  ACKNOWLEDGED = 'acknowledged',
  INVESTIGATING = 'investigating',
  RESOLVED = 'resolved',
  FALSE_POSITIVE = 'false_positive'
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface Coordinates {
  lat: number;
  lng: number;
}

// Tipos para estatísticas
export interface DetectionStats {
  total_detections: number;
  verified_detections: number;
  false_positives: number;
  accuracy_rate: number;
  detections_by_type: Record<string, number>;
  detections_by_risk_level: Record<string, number>;
  average_confidence: number;
  detections_last_24h: number;
  detections_last_7d: number;
}

export interface AlertStats {
  total_alerts: number;
  pending_alerts: number;
  resolved_alerts: number;
  false_positive_alerts: number;
  alerts_by_priority: Record<string, number>;
  alerts_by_status: Record<string, number>;
  alerts_by_type: Record<string, number>;
  average_resolution_time_minutes?: number;
  alerts_last_24h: number;
  alerts_last_7d: number;
}

export interface CameraStats {
  id: number;
  name: string;
  total_detections: number;
  total_alerts: number;
  false_positives: number;
  accuracy_rate: number;
  uptime_percentage: number;
  last_detection?: string;
}

// Tipos para WebSocket
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  source?: string;
}

export interface LiveFeedMessage extends WebSocketMessage {
  type: 'video_frame';
  camera_id: number;
  frame_data: string;
  metadata: any;
}

export interface DetectionMessage extends WebSocketMessage {
  type: 'new_detection';
  detection: Detection;
}

export interface AlertMessage extends WebSocketMessage {
  type: 'new_alert';
  alert: Alert;
}

export interface CameraStatusMessage extends WebSocketMessage {
  type: 'camera_status_update';
  camera_id: number;
  status: CameraStatus;
}

export interface CameraStatus {
  id: number;
  name: string;
  is_online: boolean;
  last_heartbeat?: string;
  last_error?: string;
  detection_enabled: boolean;
}

// Tipos para filtros
export interface DetectionFilter {
  camera_id?: number;
  detection_type?: string;
  risk_level?: string;
  object_class?: string;
  is_verified?: boolean;
  is_false_positive?: boolean;
  start_date?: string;
  end_date?: string;
  min_confidence?: number;
  max_confidence?: number;
}

export interface AlertFilter {
  camera_id?: number;
  alert_type?: string;
  priority?: AlertPriority;
  status?: AlertStatus;
  start_date?: string;
  end_date?: string;
  location?: string;
}

// Tipos para API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Tipos para configurações
export interface AppConfig {
  api_url: string;
  ws_url: string;
  refresh_interval: number;
  max_retries: number;
  timeout: number;
}

// Tipos para notificações
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Tipos para gráficos
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
}

// Tipos para mapas
export interface MapMarker {
  id: number;
  position: [number, number]; // [lat, lng]
  title: string;
  description?: string;
  type: 'camera' | 'detection' | 'alert';
  status?: 'online' | 'offline' | 'warning';
}

// Tipos para exportação
export interface ExportOptions {
  format: 'csv' | 'json' | 'pdf';
  date_range: {
    start: string;
    end: string;
  };
  filters?: DetectionFilter | AlertFilter;
  include_images?: boolean;
}

// Tipos para relatórios
export interface Report {
  id: string;
  title: string;
  type: 'detection' | 'alert' | 'analytics';
  generated_at: string;
  generated_by: string;
  parameters: any;
  file_path?: string;
  status: 'generating' | 'completed' | 'failed';
}
