const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = fetchJson;

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// ── Domain types (mirror backend Pydantic schemas) ──
export interface Stop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  notes: string | null;
  customer_email: string | null;
  customer_phone: string | null;
  territory_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Territory {
  id: string;
  name: string;
  color: string;
  created_at: string;
}

export interface TerritoryAssignment {
  territory_id: string;
  name: string;
  color: string;
  stop_count: number;
  center_lat: number;
  center_lng: number;
}

export interface ClusterResult {
  territories: TerritoryAssignment[];
  assigned_stops: number;
  iterations: number;
}

export const territoriesApi = {
  list: () => fetchJson<Territory[]>("/api/v1/territories/"),
  cluster: (n: number) =>
    fetchJson<ClusterResult>("/api/v1/territories/cluster", {
      method: "POST",
      body: JSON.stringify({ n }),
    }),
};

export interface RoutePnL {
  route_id: string;
  route_name: string;
  total_distance_km: number;
  estimated_minutes: number;
  fuel_cost_usd: number;
  labor_cost_usd: number;
  vehicle_cost_usd: number;
  total_cost_usd: number;
  stop_count: number;
  completed_count: number;
  on_time_count: number;
  miles_per_stop: number;
  cost_per_delivery: number;
  on_time_rate_pct: number;
}

export interface FleetSummary {
  route_count: number;
  total_distance_km: number;
  total_cost_usd: number;
  avg_cost_per_delivery: number;
  avg_on_time_rate_pct: number;
  rates: Record<string, number>;
}

export const analyticsApi = {
  routes: () => fetchJson<RoutePnL[]>("/api/v1/analytics/routes"),
  summary: () => fetchJson<FleetSummary>("/api/v1/analytics/summary"),
};

export interface LoadingItem {
  delivery_id: string;
  stop_id: string;
  stop_name: string;
  load_position: number;
  delivery_sequence: number;
}

export interface LoadingManifest {
  route_id: string;
  route_name: string;
  dock_number: string | null;
  item_count: number;
  items: LoadingItem[];
}

export interface WmsSyncResult {
  routes_synced: number;
  deliveries_synced: number;
  timestamp: string;
}

export interface RouteForecast {
  route_id: string;
  route_name: string;
  hour: number;
  traffic_factor: number;
  weather_factor: number;
  combined_factor: number;
  baseline_minutes: number;
  adjusted_minutes: number;
}

export interface WeatherState {
  factor: number;
}

export const predictiveApi = {
  weather: () => fetchJson<WeatherState>("/api/v1/predictive/weather"),
  setWeather: (factor: number) =>
    fetchJson<WeatherState>("/api/v1/predictive/weather", {
      method: "POST",
      body: JSON.stringify({ factor }),
    }),
  routeForecast: (routeId: string) =>
    fetchJson<RouteForecast>(`/api/v1/predictive/routes/${routeId}/forecast`),
};

export const wmsApi = {
  loadingSequence: (routeId: string) =>
    fetchJson<LoadingManifest>(
      `/api/v1/wms/routes/${routeId}/loading-sequence`
    ),
  assignDock: (routeId: string, dock_number: string) =>
    fetchJson<{ route_id: string; dock_number: string }>(
      `/api/v1/wms/routes/${routeId}/dock`,
      { method: "POST", body: JSON.stringify({ dock_number }) }
    ),
  sync: () =>
    fetchJson<WmsSyncResult>("/api/v1/wms/sync", { method: "POST" }),
};

export interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  vehicle_type: string;
  status: string;
  current_lat: number | null;
  current_lng: number | null;
  location_updated_at: string | null;
  created_at: string;
}

export interface Delivery {
  id: string;
  route_id: string;
  stop_id: string;
  sequence: number;
  kind: "drop_off" | "pickup";
  status: string;
  notes: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Route {
  id: string;
  name: string;
  driver_id: string | null;
  vehicle_id: string | null;
  status: string;
  total_distance_km: number;
  estimated_minutes: number;
  dock_number: string | null;
  created_at: string;
  deliveries: Delivery[];
}

export interface Vehicle {
  id: string;
  plate: string;
  vehicle_type: string;
  capacity_kg: number;
  status: string;
  odometer_km: number;
  last_service_odometer_km: number;
  last_service_at: string | null;
  created_at: string;
}

export interface MaintenanceAlert {
  vehicle_id: string;
  plate: string;
  km_since_service: number;
  interval_km: number;
  severity: "ok" | "due_soon" | "overdue";
}

export interface AutoAssignResult {
  route_id: string;
  vehicle_id: string;
  plate: string;
  reason: string;
}

export interface FleetSyncResult {
  pulled: number;
  pushed: number;
  timestamp: string;
}

export interface NotificationTemplate {
  id: string;
  kind: string;
  subject: string;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationEvent {
  id: string;
  delivery_id: string | null;
  kind: string;
  channel: "email" | "sms";
  recipient: string;
  subject: string;
  body: string;
  status: string;
  sent_at: string;
}

export interface ReturnPickup {
  id: string;
  route_id: string;
  stop_id: string;
  sequence: number;
  kind: string;
  status: string;
  notes: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface ConsolidationResult {
  route_id: string;
  route_name: string;
  consolidated_count: number;
  total_distance_km: number;
  estimated_minutes: number;
}

export const returnsApi = {
  request: (stop_id: string, notes?: string) =>
    fetchJson<ReturnPickup>("/api/v1/returns/request", {
      method: "POST",
      body: JSON.stringify({ stop_id, notes: notes ?? null }),
    }),
  listPending: () => fetchJson<ReturnPickup[]>("/api/v1/returns/pending"),
  consolidate: () =>
    fetchJson<ConsolidationResult>("/api/v1/returns/consolidate", {
      method: "POST",
    }),
};

export const notificationsApi = {
  listTemplates: () =>
    fetchJson<NotificationTemplate[]>("/api/v1/notifications/templates"),
  updateTemplate: (id: string, data: { subject?: string; body?: string }) =>
    fetchJson<NotificationTemplate>(`/api/v1/notifications/templates/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  createTemplate: (data: { kind: string; subject: string; body: string }) =>
    fetchJson<NotificationTemplate>("/api/v1/notifications/templates", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  listEvents: () => fetchJson<NotificationEvent[]>("/api/v1/notifications/events"),
  manualSend: (delivery_id: string, kind: string) =>
    fetchJson<NotificationEvent>("/api/v1/notifications/send", {
      method: "POST",
      body: JSON.stringify({ delivery_id, kind }),
    }),
};

export const vehiclesApi = {
  list: () => fetchJson<Vehicle[]>("/api/v1/vehicles/"),
  create: (data: Pick<Vehicle, "plate"> & Partial<Vehicle>) =>
    fetchJson<Vehicle>("/api/v1/vehicles/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/vehicles/${id}`, { method: "DELETE" }),
  maintenanceAlerts: () =>
    fetchJson<MaintenanceAlert[]>("/api/v1/vehicles/maintenance/alerts"),
  autoAssign: (routeId: string) =>
    fetchJson<AutoAssignResult>(`/api/v1/vehicles/auto-assign/${routeId}`, {
      method: "POST",
    }),
  sync: () =>
    fetchJson<FleetSyncResult>("/api/v1/vehicles/sync", { method: "POST" }),
};

// ── Typed CRUD wrappers ──
export const stopsApi = {
  list: () => fetchJson<Stop[]>("/api/v1/stops/"),
  create: (
    data: Pick<Stop, "name" | "address" | "lat" | "lng"> & Partial<Stop>
  ) => fetchJson<Stop>("/api/v1/stops/", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/stops/${id}`, { method: "DELETE" }),
};

export const driversApi = {
  list: () => fetchJson<Driver[]>("/api/v1/drivers/"),
  create: (data: Pick<Driver, "name" | "email"> & Partial<Driver>) =>
    fetchJson<Driver>("/api/v1/drivers/", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/drivers/${id}`, { method: "DELETE" }),
};

export interface OptimizeResult {
  route_id: string;
  original_sequence: string[];
  optimized_sequence: string[];
  original_distance_km: number;
  optimized_distance_km: number;
  improvement_percent: number;
}

export const routesApi = {
  list: () => fetchJson<Route[]>("/api/v1/routes/"),
  get: (id: string) => fetchJson<Route>(`/api/v1/routes/${id}`),
  create: (data: { name: string; driver_id?: string | null; stop_ids?: string[] }) =>
    fetchJson<Route>("/api/v1/routes/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Route>) =>
    fetchJson<Route>(`/api/v1/routes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/routes/${id}`, { method: "DELETE" }),
  optimize: (id: string, max_stops?: number) =>
    fetchJson<OptimizeResult>(`/api/v1/routes/${id}/optimize`, {
      method: "POST",
      body: JSON.stringify({ max_stops: max_stops ?? null }),
    }),
  insertUrgent: (id: string, stop_id: string) =>
    fetchJson<InsertUrgentResult>(`/api/v1/routes/${id}/insert-urgent`, {
      method: "POST",
      body: JSON.stringify({ stop_id }),
    }),
};

export interface StopImpact {
  delivery_id: string;
  stop_name: string;
  old_sequence: number;
  new_sequence: number;
  eta_shift_minutes: number;
}

export interface InsertUrgentResult {
  route_id: string;
  inserted_delivery_id: string;
  inserted_at_position: number;
  extra_distance_km: number;
  extra_minutes: number;
  shifted_stops: StopImpact[];
}

export const deliveriesApi = {
  list: (routeId?: string) =>
    fetchJson<Delivery[]>(`/api/v1/deliveries/${routeId ? `?route_id=${routeId}` : ""}`),
  update: (id: string, data: Partial<Delivery>) =>
    fetchJson<Delivery>(`/api/v1/deliveries/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

export interface StopETA {
  delivery_id: string;
  stop_id: string;
  stop_name: string;
  sequence: number;
  distance_from_previous_km: number;
  cumulative_km: number;
  eta: string;
  minutes_from_now: number;
}

export interface RouteETA {
  route_id: string;
  driver_id: string | null;
  driver_position: [number, number] | null;
  stops: StopETA[];
  is_delayed: boolean;
}

export const trackingApi = {
  pushLocation: (driverId: string, lat: number, lng: number) =>
    fetchJson<{
      driver_id: string;
      current_lat: number;
      current_lng: number;
      location_updated_at: string;
    }>(`/api/v1/tracking/drivers/${driverId}/location`, {
      method: "POST",
      body: JSON.stringify({ lat, lng }),
    }),
  routeEta: (routeId: string) =>
    fetchJson<RouteETA>(`/api/v1/tracking/routes/${routeId}/eta`),
};

export interface DeliveryProof {
  id: string;
  status: string;
  photo_b64: string | null;
  signature_b64: string | null;
  barcode: string | null;
  geotag_lat: number | null;
  geotag_lng: number | null;
  photo_validated: boolean | null;
  notes: string | null;
  completed_at: string | null;
}

export interface ProofSubmit {
  photo_b64?: string | null;
  signature_b64?: string | null;
  barcode?: string | null;
  geotag_lat?: number | null;
  geotag_lng?: number | null;
  notes?: string | null;
}

export const proofApi = {
  complete: (deliveryId: string, data: ProofSubmit) =>
    fetchJson<DeliveryProof>(`/api/v1/deliveries/${deliveryId}/complete`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  get: (deliveryId: string) =>
    fetchJson<DeliveryProof>(`/api/v1/deliveries/${deliveryId}/proof`),
};

export interface DriverShift {
  id: string;
  driver_id: string;
  start_at: string;
  end_at: string | null;
  hours_worked: number;
  status: string;
  created_at: string;
}

export interface FatigueAlert {
  driver_id: string;
  driver_name: string;
  hours_last_7_days: number;
  limit_hours: number;
  remaining_hours: number;
  severity: "ok" | "warning" | "critical";
}

export const shiftsApi = {
  list: (driverId?: string) =>
    fetchJson<DriverShift[]>(
      `/api/v1/shifts/${driverId ? `?driver_id=${driverId}` : ""}`
    ),
  create: (data: {
    driver_id: string;
    start_at: string;
    end_at?: string | null;
    hours_worked?: number;
    status?: string;
  }) =>
    fetchJson<DriverShift>("/api/v1/shifts/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/shifts/${id}`, { method: "DELETE" }),
  fatigueAlerts: () => fetchJson<FatigueAlert[]>("/api/v1/shifts/fatigue/alerts"),
};
