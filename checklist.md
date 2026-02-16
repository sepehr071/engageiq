# Entity Information Checklist for LiveKit Agent

## 1. Basic Identity

| Field      | Description                          | Required?                  |
|------------|--------------------------------------|----------------------------|
| Name       | Official name (DE + EN)              | ✅ Yes                     |
| Type       | Partner / Client / Product / Demo System / Competitor | ✅ Yes                     |
| Logo/Image | URL to logo or product image         | ⚠️ Optional (for frontend display) |
| Website    | Official URL                         | ⚠️ Optional               |

## 2. Relationship to Ayand

| Field                | Description                                      | Required? |
|----------------------|--------------------------------------------------|-----------|
| Partnership type     | Integration partner / Reseller / Joint demo / Client / Vendor | ✅ Yes |
| Booth arrangement    | Shared booth / Adjacent / Separate / Demo station | ✅ Yes |
| What Ayand provides  | EngageIQ instance / Avatar overlay / Technical support / Nothing | ✅ Yes |
| What they provide    | Hardware / Space / Data / Referrals / Nothing     | ✅ Yes |
| Contact person       | Name + email for booth coordination              | ⚠️ Optional |

## 3. What the Agent Must Know (Conversation)

| Field               | Description                                      | Required? |
|---------------------|--------------------------------------------------|-----------|
| One-liner           | What is it? (1 sentence, product-agnostic)       | ✅ Yes |
| Problem solved      | What customer pain does it address?              | ✅ Yes |
| Target audience     | Who uses/buys it?                                | ✅ Yes |
| Value proposition   | Why does it matter?                              | ✅ Yes |
| Key features        | 3-5 bullet points                                | ✅ Yes |
| How it works        | Brief technical explanation (non-technical language) | ⚠️ Optional |
| Pricing model       | Rough pricing tier or "contact for pricing"      | ⚠️ Optional |
| Languages supported | If multilingual                                  | ⚠️ Optional |

## 4. Agent Behavior Rules for This Entity

- **Should the agent proactively mention it?**  
  Yes / No / Only if asked  
  **Required?** ✅ Yes

- **Cross-sell opportunity?**  
  Does this entity lead to EngageIQ sales?  
  **Required?** ✅ Yes

- **Qualifying questions**  
  What should agent ask to identify fit?  
  **Required?** ⚠️ If cross-sell

- **Handoff action**  
  Refer to partner booth / Collect lead / Schedule call  
  **Required?** ✅ Yes

- **Off-topic handling**  
  If visitor asks too much about this entity, redirect?  
  **Required?** ⚠️ Optional

## 5. EuroShow/Booth Context

| Field            | Description                           | Required?             |
|------------------|---------------------------------------|-----------------------|
| Hall/Stand number| Where is their booth?                 | ⚠️ If visitor should visit |
| Demo schedule    | Fixed demo times?                     | ⚠️ If applicable     |
| Demo location    | At Ayand booth / At their booth / Both| ✅ Yes                |
| Staff names      | Who's manning the booth?              | ⚠️ Optional          |
| QR codes         | Does this entity have its own QR code at the booth? | ⚠️ Optional |

## 6. Lead Routing

| Field                  | Description                              | Required?            |
|------------------------|------------------------------------------|----------------------|
| Lead destination       | Ayand / Partner / Both                   | ✅ Yes               |
| Lead notification email| Who gets notified?                       | ⚠️ If partner leads |
| Lead data sharing      | What fields can be shared with partner?  | ⚠️ If partner leads |
| Attribution            | How to track leads from this entity?     | ⚠️ If applicable    |

## 7. Product Integration (If Applicable)

| Field                  | Description                              | Required?            |
|------------------------|------------------------------------------|----------------------|
| Integrates with EngageIQ?| Yes / No / Planned                      | ✅ Yes               |
| Integration type       | Data feed / Avatar overlay / Hardware / None | ⚠️ If integrated |
| Demo available?        | Can visitors see the integration live?   | ⚠️ If integrated    |
| Screenshots/images     | Visual assets for agent to show          | ⚠️ If demo          |

## 8. Competitor Intelligence (If Competitor)

| Field                     | Description                                           | Required? |
|---------------------------|-------------------------------------------------------|-----------|
| How they position themselves | Their messaging                                    | ✅ Yes |
| Key differentiators vs EngageIQ | Why we're better                                   | ✅ Yes |
| Their weaknesses          | What they don't do well                               | ✅ Yes |
| Pricing comparison        | Are they cheaper/more expensive?                      | ⚠️ Optional |
| When to steer away        | What visitor signals indicate they're a better fit for competitor? | ⚠️ Optional |

## 9. Prompt Integration

| Field             | Description                                           | Required? |
|-------------------|-------------------------------------------------------|-----------|
| Section in prompt | Where does this info go? (Identity / Products / Partners / Behavior Rules) | ✅ Yes |
| Language variants | DE + EN versions of all text                          | ✅ Yes |
| Tone/formality    | How should agent speak about this entity?             | ⚠️ Optional |

## 10. Data & Attribution

| Field                 | Description                                           | Required?       |
|-----------------------|-------------------------------------------------------|-----------------|
| UTM/campaign parameter| How to track traffic from this entity?                | ⚠️ If applicable |
| Source ID             | Internal identifier for attribution                   | ⚠️ If applicable |
| Lead score modifier   | Does interest in this entity increase/decrease intent score? | ⚠️ Optional |

## Quick Reference: Minimum Viable Entity Info

For an entity to be conversation-ready, you need at minimum:

- Name: ___________
- Type: ___________
- One-liner: ___________
- Problem solved: ___________
- Target audience: ___________
- Should agent mention proactively? ___________
- Handoff action: ___________
- Lead destination: ___________

## Example: Filled Checklist for CarIQ

| Field              | Value                                                                 |
|--------------------|-----------------------------------------------------------------------|
| Name               | CarIQ                                                                 |
| Type               | Product (Ayand's own)                                                 |
| One-liner          | Multilingual digital lot attendant for car dealerships                |
| Problem solved     | 98% of dealership traffic leaves silently; 47-hour lead response time |
| Target audience    | Marketing/Digital Manager at car dealerships                          |
| Value proposition  | Shows what website traffic actually wants, routes serious buyers to sales in real time |
| Key features       | Intent scoring (1-10), hot lead alerts, campaign attribution, multilingual, weekly reports |
| Proactive mention? | Only if visitor is in automotive industry                             |
| Handoff action     | Collect lead, offer pilot discussion                                  |
| Lead destination   | Ayand (moniri@ayand.ai)                                               |
| Pricing            | €3,000 pilot (€750 setup + 3×€750/month)                              |
| Images             | https://image.ayand.cloud/Images/cariq/...                            |