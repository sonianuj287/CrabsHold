# 🦀 CrabsHold

> The Governance Layer Between AI Agents and Enterprise Systems.

CrabsHold is an open-source Identity-Aware Agent Gateway, Execution Proxy, and Governance Platform for enterprise AI agents.

As organizations adopt MCP servers, autonomous agents, and LLM-powered workflows, a critical question emerges:

**Who governs the agent?**

Most AI frameworks focus on helping agents do more.

CrabsHold focuses on ensuring agents only do what they are allowed to do.

---

## The Problem

Modern AI agents can:

* Access databases
* Query internal APIs
* Modify records
* Trigger workflows
* Access customer information
* Execute business operations

However, today's agent ecosystems suffer from several fundamental issues:

### Unbounded Tool Access

Agents often operate using privileged service credentials.

If an agent can access a tool, it often gains access to everything behind that tool.

### Prompt Injection Attacks

A malicious document, email, webpage, or user prompt can manipulate the agent into:

* Ignoring instructions
* Revealing sensitive data
* Executing unauthorized actions

### Lack of Human Oversight

Agents make decisions continuously without sufficient opportunities for human intervention.

### No Deterministic Governance

Most agent frameworks rely on probabilistic reasoning.

Enterprise systems require deterministic guarantees.

### Compliance and Audit Challenges

Organizations need answers to questions such as:

* What data was accessed?
* Which tool was executed?
* Why was it executed?
* Who authorized it?
* What was the financial cost?

Most current systems cannot answer these questions reliably.

---

# Our Vision

The future of enterprise AI will not be built on unrestricted autonomous agents.

It will be built on governed autonomy.

CrabsHold acts as the operating system for AI agents.

Just as Kubernetes became the control plane for containers,

CrabsHold aims to become the control plane for AI agents.

---

# Core Principles

## 1. Identity Before Intelligence

Agents should never have more permissions than the human they represent.

Every tool invocation must be executed on behalf of a verified identity.

## 2. Deterministic Over Probabilistic

Critical workflows must be enforced by code, not by model reasoning.

## 3. Human Oversight By Design

High-risk operations must pause and wait for approval.

## 4. Everything Is Auditable

Every decision must be traceable.

## 5. Cost Is A Security Concern

Runaway agents can create operational and financial damage.

Token consumption must be governed.

---

# Architecture

```
               ┌───────────────────────┐
               │    User / Initiator   │
               └───────────┬───────────┘
                           │ (Identity Token)
                           ▼
               ┌───────────────────────┐
               │   AI Agent / LLM      │
               └───────────┬───────────┘
                           │ (MCP Tool Call Request)
                           ▼
 ┌───────────────────────────────────────────────────────────┐
 │                       CrabsHold                           │
 │                Governance Control Plane                   │
 ├───────────┬─────────────┬────────────┬─────────────┬──────┤
 │  Policy   │  Identity   │    Risk    │  Approval   │ Cost │
 │  Engine   │   Engine    │   Engine   │   Engine    │ Mgmt │
 └───────────┴──────┬──────┴────────────┴─────────────┴──────┘
                    │
                    ▼ (Authorized & Clean Payload)
         ┌─────────────────────┐
         │   Execution Proxy   │
         └──────────┬──────────┘
                    │
                    ▼
      ┌───────────────────────────┐
      │ Databases / APIs / Tools  │
      └───────────────────────────┘
---
```
# Features

## Stateful Workflow Orchestration

Agents execute within explicit workflow graphs.

Allowed transitions are defined in advance.

Invalid state transitions are rejected immediately.

Example:

Data Extraction
↓
Compliance Review
↓
Manager Approval
↓
Execute Action

The agent cannot bypass required governance checkpoints.

---

## Identity-Aware Tool Execution

Every tool call is executed using scoped credentials.

Instead of:

Agent → Database

We enforce:

User → Agent → CrabsHold → Database

The effective permissions never exceed the user's permissions.

---

## Human-In-The-Loop Interruptions

CrabsHold can suspend execution at predefined checkpoints.

Examples:

* Database modification
* Customer communication
* Financial transactions
* Regulatory actions
* Budget threshold violations

Workflow state is persisted and execution can resume later.

---

## Immutable Audit Trails

Every action is recorded.

Captured information includes:

* Incoming prompt
* Agent reasoning metadata
* Tool invocation
* Parameters
* Response payload
* User identity
* Approval history
* Cost metrics

---

## Agent Cost Governance

Track:

* Token usage
* API spend
* Tool invocation count
* Runtime duration

Policies can automatically terminate workflows when limits are exceeded.

---

## Policy-as-Code

Governance rules are declarative.

Example:

```yaml
action: customer_delete
requires:
  - manager_approval
```

Example:

```yaml
max_token_cost: 5
action: suspend
```

Policies are versioned and auditable.

---

## Prompt Injection Protection

Incoming context is inspected before reaching downstream tools.

Potential threats include:

* Instruction overrides
* Data exfiltration attempts
* Tool abuse patterns
* Hidden prompt attacks

Detected violations can be blocked, quarantined, or escalated.

---

# What Makes CrabsHold Different?

Most projects focus on:

"How can agents do more?"

CrabsHold focuses on:

"How can agents safely operate inside enterprises?"

We treat governance as a first-class primitive.

---

# Future Innovations

## Dynamic Trust Scores

Every workflow accumulates a trust score.

Trust score is influenced by:

* Historical behavior
* Tool access patterns
* Policy violations
* User approvals
* Anomaly detection

Higher trust enables greater autonomy.

Lower trust increases oversight.

---

## Adaptive Autonomy

Not all agents deserve the same level of freedom.

CrabsHold aims to dynamically adjust governance requirements based on:

* Risk
* Context
* Historical reliability

An agent that consistently behaves correctly earns additional autonomy.

---

## Semantic Governance Engine

Traditional security evaluates actions.

CrabsHold will evaluate intent.

Example:

Reading customer records for support purposes may be allowed.

Reading the same records for unrelated purposes may be blocked.

The governance engine will reason about the business objective behind every action.

---

## Agent Time Travel

Every workflow checkpoint is persisted.

Developers can:

* Rewind
* Replay
* Fork
* Simulate

This enables deterministic debugging for agent systems.

---

## Multi-Agent Governance

Future enterprises will operate thousands of cooperating agents.

CrabsHold will govern:

* Agent-to-agent communication
* Delegation chains
* Cross-agent trust
* Shared budgets
* Collective approvals

---

# Technology Stack

Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Redis

Workflow Engine

* Custom DAG Runtime
* Event-Driven State Machine

Frontend

* React
* TypeScript
* WebSockets

Observability

* OpenTelemetry
* Prometheus
* Grafana

Security

* RBAC
* OBO Token Injection
* Policy Engine
* Audit Framework

---

# Long-Term Goal

We believe AI governance should become infrastructure.

Every enterprise adopting autonomous agents will eventually require:

* Identity enforcement
* Workflow governance
* Human oversight
* Auditability
* Cost controls

CrabsHold exists to become that layer.

Not another AI agent.

The system that keeps AI agents accountable.

---

Built for the future of governed autonomy.
