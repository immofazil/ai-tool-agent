# System Observability: Logs, Metrics, and Health Checks

Effective observability relies on three distinct pillars: logs, metrics, and health checks. Structured logs detail specific events, execution context, and error stack traces to explain what happened during execution. Metrics aggregate numerical measurements over time to show how often events occur, how much resource is consumed, and how fast endpoints respond. Health checks provide instantaneous status checks to answer whether the service is currently up, responsive, and properly connected to internal dependencies.

## The Role of the Health Check Endpoint

The /health endpoint serves as a vital signal for automated infrastructure. Load balancers query health endpoints to route traffic away from failing server instances. Cloud deployment pipelines monitor health routes during zero-downtime updates to confirm successful rollouts before terminating older application containers. Uptime monitoring services poll health endpoints continuously to trigger automated failover procedures the moment availability degrades.

## Critical Metrics for AI Agent Systems

In an AI agent system, tracking domain-specific metrics is essential for maintaining service level agreements and managing API expenses. Critical metrics include total request counts to measure incoming traffic volume across time windows, error rates to monitor unhandled exceptions and HTTP failure codes, average response latency to spot system bottlenecks and slow model calls, tool-call counts to observe external tool and database dependency usage & token and cost estimates to track resource consumption and vendor spending

## Alerting Strategies and Thresholds

Alerting systems evaluate these metrics continuously to warn engineering teams of system degradation before outages occur. High-priority alerting triggers include sharp error spikes signaling broken integrations or invalid API keys, latency spikes indicating upstream model throttling or database locks, and unexpected cost runaways caused by infinite tool loops or prompt injection exploits. Combining real-time health routing with automated metric alerts ensures continuous system stability.