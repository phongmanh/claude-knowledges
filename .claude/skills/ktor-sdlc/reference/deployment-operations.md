# Deployment & operations reference

How a Ktor service is packaged, configured, deployed, migrated, rolled back and operated. The platform (Kubernetes, a managed container service such as Cloud Run or ECS, or VMs) is chosen in a Phase 2 ADR; the rules below hold on any of them. Examples use Kubernetes terms where a concrete example helps.

## Packaging
- **One immutable OCI image per commit,** built once by CI and promoted from environment to environment **by digest**. Never rebuild for production.
- **The Ktor Gradle plugin** builds it with Jib, no Dockerfile needed:
  ```kotlin
  ktor {
      docker {
          jreVersion.set(JavaVersion.VERSION_21) // the JDK LTS you build with
          localImageName.set("notes-api")
          imageTag.set(project.version.toString())
      }
  }
  ```
  `./gradlew publishImageToLocalRegistry` builds to the local Docker daemon; `./gradlew publishImage` pushes to the registry configured in the same block.
- **Or a multi-stage `Dockerfile`,** when the base image must be controlled:
  ```dockerfile
  FROM eclipse-temurin:21-jdk AS build
  WORKDIR /src
  COPY . .
  RUN ./gradlew --no-daemon buildFatJar

  FROM gcr.io/distroless/java21-debian12:nonroot
  COPY --from=build /src/build/libs/*-all.jar /app/app.jar
  EXPOSE 8080
  ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-XX:+ExitOnOutOfMemoryError", "-Duser.timezone=UTC", "-jar", "/app/app.jar"]
  ```
- **Image rules:**
  - a minimal base (distroless or a slim JRE) with the same JDK major version as the build;
  - a non-root user and a read-only root filesystem;
  - container-aware memory (`-XX:MaxRAMPercentage`), exit on `OutOfMemoryError` so the platform restarts the instance, UTC as the time zone;
  - scanned in CI; an SBOM attached; signed.
- **Version** the image with the release version and the commit; the service reports both in its logs and metrics.

## Configuration and secrets
- **Environments differ only by environment variables.** Non-secret settings come from the platform's config (e.g. a ConfigMap); secrets from the secret manager, injected at runtime.
- **The service fails fast** on a missing or invalid setting ([architecture.md](architecture.md#configuration)), so a bad deploy never becomes ready.
- **No `development` mode,** and no API docs (`SERVE_API_DOCS=false`) in production unless the API is public and the docs are meant to be.

## Runtime platform
- **Replicas:** at least two in production, spread across availability zones; a disruption budget so maintenance never takes all of them down.
- **Resources:** CPU and memory requests from the load test; a memory limit; no CPU limit unless the platform requires one (it throttles the JIT and GC).
- **Probes:**

  | Probe | Endpoint | Settings (e.g.) |
  |---|---|---|
  | Startup | `/health/live` | Allow ~60 s for the JVM to start |
  | Liveness | `/health/live` | Period 10 s, 3 failures; never checks dependencies |
  | Readiness | `/health/ready` | Period 5 s; fails when the database is unreachable |
- **Shutdown:** a termination grace period longer than Ktor's `shutdownTimeout` (e.g. 30 s vs 20 s), and a short pre-stop delay (e.g. 5 s) so the load balancer stops routing before the server stops accepting.
- **Autoscaling** on request concurrency, latency or queue depth, with a minimum replica count; CPU only as a secondary signal.
- **Network:** the database and internal services on private networks only; `/metrics` reachable from the monitoring system only; egress restricted to known destinations where the platform allows.

## Database migrations
- **Expand → migrate → contract,** so every deploy is compatible with both the old and the new version of the code, which run side by side during a rollout:
  1. **Expand:** add new columns (nullable or with a default), tables and indexes (`CREATE INDEX CONCURRENTLY` in its own migration, outside a transaction). Old code ignores them.
  2. **Migrate:** deploy code that writes both shapes; backfill in batches with a job, not in the migration.
  3. **Contract:** after every running version uses the new shape, drop the old columns in a later release.
- **Never in the same release:** renaming or dropping a column that the previous version still reads, or adding a `NOT NULL` column without a default.
- **The migration job runs before the rollout,** from the same image (`java -cp /app/app.jar com.example.notes.core.persistence.MigrateKt`), with a database user that has DDL rights. If it fails, the rollout doesn't start.
- **Long-running changes** (big backfills, table rewrites) are planned operations with a runbook, a lock-timeout setting (`SET lock_timeout`), and a time window.
- **Rehearse** each release's migrations on a copy of production-sized data in Phase 5 and measure how long they take.

## Rollout
| Strategy | How | Use when |
|---|---|---|
| Rolling | Replace replicas a few at a time; readiness gates each step | The default for compatible changes |
| Canary | Route a small share of traffic (e.g. 5% → 25% → 100%) to the new version and compare its error rate and latency with the old one | Risky changes, high traffic |
| Blue-green | Start the full new version beside the old; switch traffic at once; keep the old one for a quick switch back | Changes that are hard to run side by side, or when instant rollback matters most |

- **Halt criteria are agreed before the rollout** (e.g. 5xx rate > 0.5%, p99 > the SLO threshold, error-budget burn rate > 10× for 10 minutes), and automated where the platform supports it.
- **Feature flags separate deploy from release.** New behaviour ships dark and is turned on per percentage, tenant or client version; every risky feature has a kill switch.
- **Deploy markers** on the dashboards show when each version went out.

## Rollback
- **Code:** redeploy the previous image digest. Because migrations are expand-only within a release, the previous version still works with the new schema.
- **Data:** never roll a migration back in production; fix forward with a new migration. Restoring a backup is a disaster-recovery action, not a rollback.
- **Flags first:** if a flag isolates the problem, turning it off is faster and safer than a redeploy.

## Backups and disaster recovery
- **Automated, encrypted backups** with point-in-time recovery where the RPO needs it, copied to another account or region.
- **Restore drills** on a schedule (e.g. quarterly) and before launch: restore into a separate environment, run smoke tests, and record the time it took against the RTO.
- **The DR plan** names the tier (backup and restore, pilot light, warm standby, active-active), the steps, the owners and how DNS or traffic moves.

## Infrastructure as code
- **Everything is code:** networks, databases, the cluster or service definitions, secrets wiring, alerts and dashboards (e.g. Terraform or OpenTofu, Helm or the platform's manifests).
- **Reviewed and scanned** like application code (e.g. Checkov or tfsec for misconfiguration); applied by CI, not from laptops; no manual console changes.
- **Environments come from the same code,** with documented differences in size only.

## Operations
- **Runbooks** for each alert and each routine task: what it means, how to confirm, how to mitigate (flags, scaling, failover, rollback), who to escalate to. Linked from the alert.
- **On-call** with a named owner per service, an escalation path, and handover notes.
- **Incidents:** declare, mitigate first, communicate on a schedule, then a blameless postmortem with action items that are tracked to closure.
- **Capacity reviews** (e.g. monthly): traffic and data growth against the capacity model; database size, connections and slow queries.
- **Cost:** resources tagged by service and environment, budgets with alerts, idle environments scaled down.
