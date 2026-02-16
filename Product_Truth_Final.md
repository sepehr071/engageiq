# Product Truth / Asset Definition

**Purpose**: This document defines the *immutable core asset* of the
company.

It describes **what the product fundamentally is**, **what it must
always do**, and **what it will never become** --- independent of
market, vertical, pricing, or sales strategy.

All Vertical Playbooks, offers, and sales motions must conform to this
document.

If there is a conflict, this document wins.

## 0. Authority & Change Control

**Document authority:** Highest

**Who can change this document:**

- Founder / CEO

- Head of Product (with CEO approval)

**Valid reasons for change (must meet at least one):**

- The core mechanism fails to capture usable interaction data or intent
  signals

- A technological shift invalidates a currently supported interaction
  surface

- A deliberate strategic decision to replace (not extend) the product
  category

**Invalid reasons for change:**

- Sales objections or lost deals

- Single-vertical requirements

- Competitive feature parity requests

- Revenue pressure or churn from misfit customers

All changes require explicit approval and versioning.

## 1. Product Name & Classification

**Product name:** EngageIQ

**Product class:** Conversational Demand Interface

**Primary philosophy:** Signal, not automation

**One-sentence definition (mechanism-focused):**

A cloud-based conversational system that engages visitors across digital
and physical surfaces, conducts structured conversations, detects
intent, and captures interaction data.

Rules:

- Describe what it does, not who it's for

- No benefits language

- No personas

## 2. Core Mechanism (The Engine)

When a visitor encounters an EngageIQ interaction surface, an AI avatar
initiates or responds to conversation using pre-ingested and structured
content. The system guides the interaction through conversational flows
designed to clarify visitor intent, records interaction signals, and
outputs structured data for review or routing.

As part of the conversation, EngageIQ may present visual content (e.g.,
inventory items, services, products) within the interface to support
intent clarification. Visitor engagement with displayed content (views,
clicks, selections) is captured as interaction data.

Value is created by converting otherwise unobserved or unstructured
visitor interactions into measurable intent and behavioral data.

## 3. Non-Negotiable Outputs (Product Invariants)

The product is considered **broken** if it fails to produce these
outputs:

**Required outputs (must always occur):**

- Captured interaction data for every conversation

- Detected and stored intent signals derived from conversations

- Structured records of interaction outcomes (engaged, dropped, routed)

Rules:

- Outputs must be observable and measurable

- Contact or lead data is not required unless explicitly configured

## 4. Supported Interaction Surfaces

**Explicitly supported surfaces:**

- Web (desktop and mobile browsers)

- QR-triggered mobile web experiences

- Kiosks

- Interactive displays (browser- or app-based)

**Conditionally supported surfaces:**

- Social or third-party channels deployed via web-based integrations
  (e.g. Instagram link-in-bio), gated by plan or add-on

**Explicitly NOT supported:**

- Offline inference

- Fully on-device inference

Device Mode is not required for the product to be considered whole and
may be sunset without invalidating the core asset.

Adding or removing a surface is a product change, not a vertical or
sales decision.

## 5. Capability Scope (What the Product Does)

**Must-have capabilities (always present):**

1.  Content ingestion and structuring

2.  Conversational AI avatar (text and voice)

3.  Intent detection and qualification

4.  Interaction data capture and storage

5.  Routing and handoff logic (to humans or systems)

6.  Device Mode support for kiosks and displays (while supported)

7.  Minimum analytics dashboard

8.  Visual content presentation within conversation (e.g., inventory,
    services, products) to support intent clarification

9.  Visual engagement tracking (views, clicks, selections on displayed
    content)

10. Campaign and source attribution (UTM parameters, referrer tracking)
    to link interactions to marketing channels

**Hard boundary for routing & handoff:**

- EngageIQ may route to humans or systems and may schedule or book

- EngageIQ may send transactional messages to visitors (e.g.,
  conversation summaries) when explicitly requested and consented

- EngageIQ will never transact (payments, orders, or financial
  execution)

**Optional capabilities (tier- or add-on--gated):**

- Contact information capture

- Advanced analytics and optimization layers

- White-label branding

- Custom onboarding and priority support

- Intent quality scoring (quantified readiness/seriousness indicators
  per interaction)

- Real-time high-intent alerts (notifications when high-value
  interactions occur)

- Automated periodic reports (e.g., weekly demand digest delivered to
  stakeholders)

- Executive ROI dashboard (aggregated view of interaction volume,
  intent distribution, and campaign attribution)

Rules:

- Capabilities define what is possible, not how it is sold

## 6. Tier Philosophy (What Tiers Change --- and Don't)

**Tiers may change:**

- Depth of configuration and personalization

- Data inputs and ingestion sources

- Optimization cadence and analytics sophistication

- Access to optional capabilities

**Tiers may NOT change:**

- Core conversational mechanism

- Required interaction and intent outputs

- Obligation to capture interaction data

If a tier requires a different mechanism, it is a different product.

**Tier Intent Clarification (Non-Commercial)**

Tiers exist to control *how the captured interaction and intent data is
used*, not whether it is captured.

- **Bronze** exposes raw interaction and intent signals to confirm that
  demand exists.

- **Silver** structures conversations to actively clarify intent and
  optionally route qualified interactions to humans or systems.

- **Gold** analyzes intent signals longitudinally to detect patterns,
  shifts, and changes in demand over time.

All tiers rely on the same conversational engine. Tiers change
interpretation depth, not the underlying mechanism.

## 7. Data Philosophy

**What data the product must always capture:**

- Interaction events

- Conversational paths and outcomes

- Intent signals inferred from interactions

- Visual engagement data (content viewed, clicked, selected within
  conversation)

- Campaign and source attribution (UTM parameters, referrer, entry
  point) for every interaction

- Aggregated visibility into intent distributions over time (minimum
  viable form)

**What data capture is optional:**

- Contact details and lead information

**What the product will never guarantee:**

- Lead volume

- Conversion rates

- Revenue outcomes

Data is treated as a primary product output, not a byproduct.

In higher tiers, captured intent signals may be analyzed across time to
surface longitudinal patterns such as seasonal shifts, emerging topics
of interest, and changes in visitor behavior.

These analyses describe *what demand is doing*, not *what actions must
be taken*.

## 8. Explicit Exclusions (Anti-Features)

The product explicitly does **not**:

- Replace human staff or sales teams

- Operate without internet connectivity

- Perform offline or on-device inference

- Guarantee leads, bookings, or revenue

These exclusions are intentional and defensible.

## 9. Success & Failure Criteria

**The product is successful when:**

- Usable interaction and intent data is consistently captured

- Buyers gain visibility into previously unobserved demand

**The product is failing when:**

- Conversations occur without data capture

- Intent signals cannot be reliably extracted

These criteria override revenue-based interpretations.

## 10. Dependency Boundaries

**What this product depends on:**

- Cloud-based infrastructure

- Web and device runtime environments

**What must never depend on a specific vertical:**

- Core interaction logic

- Data capture requirements

- Tier philosophy

If a dependency is vertical-specific, it belongs in a Vertical Playbook.

## 11. Relationship to Vertical Playbooks

Vertical Playbooks:

- Translate product language into vertical-specific terms

- Define buyer roles, pricing, and commercial sequencing

- Configure defaults and allowed options

Vertical Playbooks may NOT:

- Redefine product capabilities

- Add or remove interaction surfaces

- Override exclusions or invariants

- Change success criteria

## 12. Product Integrity Check (Final Gate)

Answer YES / NO:

- Can this product exist without any specific vertical? YES

- Would removing all playbooks leave the product intact? YES

- Can multiple unrelated verticals share this asset? YES

- Can sales lose deals without triggering product change? YES

## 13. Versioning & Sign-off

**Version:** 1.3

**Date:** 31.01.2026

**Approved by:**

**Notes on changes (v1.3):**

- Added campaign and source attribution as a must-have capability
  (Section 5, #10)
- Added campaign/source data to required data capture (Section 7)
- Added optional capabilities for Marketing Manager use cases:
  - Intent quality scoring
  - Real-time high-intent alerts
  - Automated periodic reports (weekly demand digest)
  - Executive ROI dashboard

**Reason for change:** Enable Marketing Manager value proposition.
Campaign attribution and reporting features are required to demonstrate
ROI and justify ad spend — critical for selling to Marketing buyers.

---

**Notes on changes (v1.2):**

- Added visual content presentation as a core capability (Section 2, 5)
- Added visual engagement tracking as a must-have capability (Section 5)
- Added visual engagement data to required data capture (Section 7)
- Clarified that transactional messages (e.g., conversation summaries)
  may be sent when explicitly requested and consented (Section 5)

**Reason for change:** Align Product Truth with implemented demo
functionality. Visual content presentation and engagement tracking are
now considered core to the conversational demand interface.
