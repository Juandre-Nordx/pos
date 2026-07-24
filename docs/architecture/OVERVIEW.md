# NordxPOS Architecture (Revised)

## Deployment Model

**Single-tenant per customer** — each Railway deployment serves one business. No `organization_id` scoping. A singleton `company_settings` table holds tenant configuration.

## Locale

- Currency: **ZAR** (South African Rand)
- Locale: **en-ZA**
- Timezone: **Africa/Johannesburg**

## Module 3 — PPE (Personal Protective Equipment)

Replaces the original PPPoE module. Tracks safety equipment issued to employees.

| Table | Purpose |
|-------|---------|
| `ppe_categories` | Boots, gloves, helmets, hi-vis, eye protection |
| `ppe_items` | Catalog items with size, standard (SANS/EN), replacement interval |
| `ppe_employee_issues` | Issuance records linking employees to PPE |
| `ppe_inspections` | Condition checks and compliance audits |
| `ppe_replacement_alerts` | Upcoming replacement due dates |

PPE items link to `products` in Inventory for stock tracking.

## Demo Product Scope

The demo is a **client-facing showcase** with:

1. Premium dashboard (revenue, stock, PPE compliance, activity feed)
2. Authentication with demo credentials
3. Clients module (list + detail)
4. Inventory module (products, stock levels)
5. PPE module (catalog, employee assignments, compliance)
6. Navigation shell for all planned modules (Finance, Quotes, Invoices, etc.)

Seed data uses realistic South African business scenarios.

## Storage

Railway Volume mounted at `/data/uploads` for file storage. Cloudflare R2 integration planned for future.

## Base Table Mixin

Every table includes: `id`, `uuid`, `created_at`, `updated_at`, `created_by`, `updated_by`, `is_deleted`.

## API

All endpoints under `/api/v1/`. External references use UUID only.

## Security

JWT access + refresh tokens, RBAC, audit logs, rate limiting, bcrypt password hashing.
