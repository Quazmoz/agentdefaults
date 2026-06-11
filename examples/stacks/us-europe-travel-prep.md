# US-Europe Travel Prep Stack

## Purpose

Use this composed stack when answering travel-prep questions for trips from the United States to European countries.

## Stack

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

- US to Europe trip preparation
- carry-on vs checked baggage questions
- country-specific packing lists
- medicines, batteries, electronics, food, gifts, and souvenirs
- EU, Schengen, UK, Ireland, and non-Schengen Europe gotchas
- customs declarations and return-to-US considerations
- money, currency, cash, card, ATM, and tipping guidance
- outlet, voltage, adapter, and converter guidance
- concise country-by-country travel checklists

## Inputs To Provide

```text
Destination countries:
Travel dates:
Airline and route:
Trip length:
Trip type: city / business / family / hiking / beach / winter / long stay
Special items:
Medicines or medical devices:
Food, gifts, or souvenirs:
Need advice for: packing / baggage item / money / outlets / entry / all
```

## Suggested Prompt

```text
Use the US-Europe Travel Prep Stack from AgentDefaults.

Read or apply these defaults:

- agents/us-europe-travel-advisor.md
- agents/token-efficient-response-agent.md
- skills/us-europe-baggage-packing-research.md
- skills/token-efficient-response-compression.md
- prompts/planning/us-europe-trip-prep.md

Build a current, source-backed travel-prep guide for this itinerary. Research official sources before answering rule-sensitive questions. Separate TSA/security screening, FAA hazardous-material rules, airline baggage policy, destination customs/import rules, and return-to-US rules.

Return a practical checklist with carry-on only, checked-bag OK, do-not-bring/buy-there, country-by-country entry, money, power/outlet, packing, gotchas, verify-before-departure, and sources checked.
```

## Minimal Item-Check Prompt

```text
Use the US-Europe Travel Advisor defaults. Can I bring this item from the US to <country>?

Item:
Amount/size:
Battery Wh or volume, if applicable:
Carry-on, checked, or both:
Airline:
Returning to the US with it:

Give carry-on verdict, checked verdict, best packing choice, conditions, destination customs notes, return-to-US notes, and sources checked.
```

## Expected Final Response

```markdown
## Bottom Line

## Carry-On Only

## Checked-Bag OK

## Do Not Bring / Buy There

## Country Notes

### <country>
Entry:
Money:
Power:
Customs/baggage:
What to bring:
Gotchas:

## Verify Before Departure

## Sources Checked
```
