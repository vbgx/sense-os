
All workers communicate through durable queues and persist to Postgres.

---

## 3. Bounded Contexts

### Domain (packages/domain)

The **single source of truth** for:
- Scoring (pain, recurrence, monetizability, etc.)
- Trend metrics logic
- Business rules
- Contracts (versioned)
- Core models

Guarantee:
- No infrastructure imports
- Pure logic
- Deterministic outputs

### Application (packages/application)

- Use-case orchestration
- Ports + UoW abstraction
- No infra implementation

### Infrastructure (packages/db, packages/queue, infra_shared)

- Persistence
- Queue client
- Logging + metrics
- Environment configuration

### Services (services/*)

Workers are **orchestrators only**:
- Load data
- Call domain logic
- Persist results
- Publish events

They do not own business logic.

---

## 4. End-to-End Data Flow

1. ingestion_worker
   - Fetches external signals
   - Normalizes into RawSignal (contract_v1)
   - Deduplicates + persists

2. processing_worker
   - Loads raw signals
   - Builds domain models
   - Applies domain scoring
   - Persists PainInstance

3. clustering_worker
   - Loads PainInstances
   - Vectorizes
   - Clusters
   - Applies domain scoring
   - Persists PainCluster

4. trend_worker
   - Loads daily aggregates only
   - Applies pure metrics(history) → score
   - Persists daily metrics + timeline

5. api_gateway
   - Reads projections
   - Exposes REST contracts
   - No domain scoring

---

## 5. Core Guarantees

### Idempotency
- Dedup keys per signal
- Queue idempotency support
- Checkpoints per vertical/source

### Contracts
- Versioned contracts in domain
- Inter-worker contract tests
- Snapshot tests for clustering + trends

### Determinism
- Domain scoring pure functions
- Trend metrics pure functions
- Golden tests for cluster output

### Boundary Enforcement
- Domain cannot import infra
- Services cannot contain business scoring
- CI checks enforce structure

---

## 6. Operational Design

- Event-driven via Redis queue
- Postgres as durable store
- Docker Compose for local stack
- Single command bootstrap + CI
- Standardized metrics:
  - job_duration_seconds
  - items_loaded_total
  - items_processed_total
  - items_persisted_total
  - errors_total

---

## 7. Scalability Strategy

- Workers horizontally scalable
- Vertical sharding via vertical_id
- Incremental vectorization
- Gated clustering optimization
- Daily pre-aggregation for trends

---

## 8. Why This Architecture Scales

- Clear separation of domain vs infrastructure
- Versioned contracts across boundaries
- Deterministic scoring core
- Event-driven extensibility
- Testable at each layer

Sense OS is built as a composable intelligence engine, not a monolith.

EOF
