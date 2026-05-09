# DClaw Route — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (osrm, graphhopper), AI product research (Route4Me, OptimoRoute, Onfleet, Circuit)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Stop/destination management
- [ ] Route creation & editing
- [ ] Driver assignment
- [ ] Basic map visualization
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Route Copilot (Dispatch Optimizer)
**Description:** AI assistant that optimizes routes, handles last-minute changes, and answers delivery questions. "Add urgent stop #5 with minimal delay."
- **AI Angle:** Dynamic VRP solver + LLM natural language dispatch commands.
- **Backend:** `/api/v1/ai/route-chat` endpoint. Re-optimization engine.
- **Frontend:** Chat panel with route map. Voice command support.
- **Files:** `backend/app/services/route_ai.py`, `frontend/src/components/route-copilot.tsx`

#### 2. Multi-Constraint Route Optimization
**Description:** Optimize routes with: time windows, vehicle capacity, driver skills, traffic, delivery priorities.
- **AI Angle:** Operations research (OR-Tools) + real-time traffic.
- **Backend:** Optimization solver API.
- **Frontend:** Route planner with constraint editor. Before/after comparison.
- **Files:** `backend/app/services/optimizer.py`

#### 3. Real-Time Driver Tracking & ETA
**Description:** Live driver location. Dynamic ETA updates for customers. Delay alerts.
- **Backend:** GPS ingestion. ETA recalculation.
- **Frontend:** Customer tracking page. Dispatcher live board.
- **Files:** `backend/app/services/eta_engine.py`

#### 4. Proof of Delivery & Photo Capture
**Description:** Digital signature, photo confirmation, barcode scan, notes per stop.
- **Backend:** Delivery confirmation API. Photo storage.
- **Frontend:** Mobile delivery form. Photo gallery per stop.
- **Files:** `frontend/src/app/mobile/delivery.tsx`

### P1 — Should Have (v1.1–1.2)

#### 5. Territory Planning & Balancing
**Description:** Auto-divide regions into balanced territories by volume, drive time, and customer density.
- **Backend:** Territory clustering algorithm.
- **Frontend:** Territory map editor. Balance metrics.

#### 6. Customer Delivery Notifications
**Description]:** Automated SMS/email notifications: on the way, 15-min warning, delivered.
- **Backend:** Notification engine with templates.
- **Frontend:** Notification template editor.

#### 7. Route Performance Analytics
**Description:** On-time rate, miles per stop, cost per delivery, driver efficiency.
- **Backend:** Performance aggregation.
- **Frontend:** Analytics dashboard with benchmarks.

#### 8. Reverse Logistics (Returns/Pickups)
**Description:** Schedule return pickups alongside regular deliveries. Optimize mixed routes.
- **Backend:** Mixed route optimizer.
- **Frontend:** Return request portal.

### P2 — Could Have (v1.3+)

#### 9. Predictive Traffic & Weather Routing
**Description:** AI adjusts routes based on predicted traffic and weather conditions.

#### 10. Crowdsourced Delivery Network
**Description:** On-demand gig driver integration for surge capacity.

#### 11. Autonomous Vehicle Route Integration
**Description:** API integration with AV fleet dispatch systems.

#### 12. Carbon-Optimized Routing
**Description:** Prefer eco-friendly routes. Track and report emissions per delivery.

---

## Implementation Priority

1. **Week 1–2:** AI Route Copilot (P0.1) + Route Optimization (P0.2)
2. **Week 3–4:** Real-Time Tracking (P0.3) + Proof of Delivery (P0.4)
3. **Week 5–6:** Territory Planning (P1.5) + Customer Notifications (P1.6)
4. **Week 7–8:** Performance Analytics (P1.7) + Reverse Logistics (P1.8)
