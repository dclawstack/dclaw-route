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
  created_at: string;
  updated_at: string;
}

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
  create: (data: Omit<Stop, "id" | "created_at" | "updated_at">) =>
    fetchJson<Stop>("/api/v1/stops/", { method: "POST", body: JSON.stringify(data) }),
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
};

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
