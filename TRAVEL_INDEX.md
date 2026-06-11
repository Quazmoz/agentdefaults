# Travel AgentDefaults Index

Fast lookup for the US-to-Europe travel-prep pack.

## Quick Selection

| Need | Start With | Add Skills |
|------|------------|------------|
| Plan a US-to-Europe trip | `agents/us-europe-travel-advisor.md` | `skills/us-europe-baggage-packing-research.md`, `skills/token-efficient-response-compression.md` |
| Check if an item can fly carry-on or checked | `agents/us-europe-travel-advisor.md` | `skills/us-europe-baggage-packing-research.md` |
| Build a full country-by-country packing guide | `prompts/planning/us-europe-trip-prep.md` | `skills/us-europe-baggage-packing-research.md` |
| Keep answers concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md` |

## Files Added

### Agent

- `agents/us-europe-travel-advisor.md` — research-first travel advisor for US travelers visiting European countries.

### Skill

- `skills/us-europe-baggage-packing-research.md` — baggage, customs, packing, money, outlet, and return-to-US research workflow.

### Prompt

- `prompts/planning/us-europe-trip-prep.md` — one-shot trip-prep guide prompt.

### Stack Example

- `examples/stacks/us-europe-travel-prep.md` — composed stack showing which agent, skill, behavior layer, and prompt to combine.

## Recommended Stack

```text
Base agent:
  agents/us-europe-travel-advisor.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/us-europe-baggage-packing-research.md
  skills/token-efficient-response-compression.md

Task prompt:
  prompts/planning/us-europe-trip-prep.md
```

## Best For

- US to Europe travel planning
- carry-on vs checked baggage item checks
- country-specific packing lists
- lithium batteries, power banks, chargers, adapters, electronics, and drones
- liquids, toiletries, aerosols, medicines, and medical devices
- food, alcohol, tobacco, gifts, plants, seeds, animal products, and souvenirs
- destination customs and return-to-US rules
- Schengen, UK, Ireland, EU, non-EU Europe, ETIAS, EES, ETA, and 90/180 gotchas
- money, cards, ATMs, cash, tipping, and dynamic currency conversion
- outlets, voltage, adapters, and converters
- common local gotchas such as transit validation, strikes, city taxes, closures, and pickpockets

## Research Rules

This pack must research current sources before answering rule-sensitive travel questions. Do not answer from memory for:

- baggage restrictions
- carry-on vs checked placement
- hazardous-material rules
- airline baggage limits
- customs declarations
- food, plant, animal, and agriculture rules
- medicines and medical devices
- large cash movement
- entry requirements
- power outlet/voltage for less common destinations
- local laws, fees, strikes, holidays, and current disruptions

## Source Hierarchy

Prefer:

1. TSA, FAA PackSafe, and operating airline rules for flight/baggage questions.
2. U.S. State Department and destination government pages for entry/safety.
3. EU, UK, Ireland, and country customs pages for destination import rules.
4. CBP, USDA APHIS, FDA, and U.S. Fish and Wildlife for return-to-US rules.
5. IEC World Plugs or a reliable plug/voltage reference for outlets.

## Minimal Use

```text
Use the US-Europe Travel Prep Stack from AgentDefaults.

Destination countries:
Travel dates:
Airline and route:
Special items:
Need advice for: packing / baggage / money / outlets / entry / all

Research current official sources first. Give a practical checklist with sources checked.
```
