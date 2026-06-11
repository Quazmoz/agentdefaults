# US-Europe Baggage and Packing Research Skill

## Purpose

Use this skill to answer what a US traveler can bring to Europe, whether an item belongs in carry-on or checked baggage, and what should be packed for each European destination.

This skill is intentionally research-first. Baggage, customs, aviation safety, medicine, cash, food, battery, and airline rules change often.

## When To Use

Use this skill for:

- carry-on vs checked baggage decisions
- packing lists for European countries
- electronics, chargers, power banks, adapters, drones, cameras, and batteries
- liquids, toiletries, aerosols, medicine, medical devices, and refrigerated medicine
- food, snacks, alcohol, tobacco, gifts, souvenirs, plants, seeds, shells, leather, wool, and animal products
- customs allowance and declaration questions
- return-to-US restrictions
- country-specific money and outlet guidance

## Required Inputs

Ideal inputs:

```text
Destination country/countries:
Travel dates:
Airline and routing:
Item or packing category:
Carry-on, checked, or both:
Return-to-US item plan:
Trip type: city / beach / hiking / business / family / winter / long stay:
```

If missing, give a conditional answer and state what must be verified.

## Research Workflow

### 1. Classify the question

Classify as one or more:

```text
Aviation security
Hazardous materials
Airline baggage limit
Destination customs/import
Return-to-US customs/agriculture
Medicine/medical device
Power/outlet/money practicality
Country packing list
```

### 2. Check the right source layer

Use source layers in this order:

1. TSA for US security screening.
2. FAA PackSafe for hazardous materials and batteries.
3. Airline rules for stricter carry-on/checked limits.
4. Destination government customs/import rules.
5. EU, UK, Ireland, or country-specific official pages for food, cash, medicines, and duties.
6. CBP, USDA APHIS, FDA, and U.S. Fish and Wildlife for return-to-US rules.
7. IEC World Plugs, destination standards body, or reliable plug/voltage references for power guidance.

### 3. Produce the verdict

For item checks, always answer:

```text
Carry-on: yes/no/conditional
Checked: yes/no/conditional
Best place: carry-on / checked / do not bring / buy there
Declare: yes/no/conditional
Verify: airline / customs / medicine authority / return-to-US rule
```

### 4. Include conditions

List exact conditions when available:

- volume or container limits
- quantity limits
- watt-hour or lithium content limits
- original packaging or prescription documentation
- customs declaration thresholds
- airline approval requirements
- destination-specific restrictions
- return-to-US declaration or agriculture inspection risk

### 5. Add practical packing advice

Convert rules into practical advice:

- pack power banks and spare lithium batteries in carry-on
- put essential medicine in carry-on
- avoid packing perishable foods across borders
- buy heavy liquids or restricted toiletries after arrival
- leave single-voltage high-watt appliances at home
- carry a universal adapter and dual-voltage USB-C charger
- keep receipts for expensive gifts or VAT-refund purchases
- photograph documents and prescriptions

## Output Format: Single Item

```markdown
## Verdict

Carry-on: Yes / No / Conditional
Checked: Yes / No / Conditional
Best choice: Carry-on / Checked / Do not bring / Buy there
Declare: Yes / No / Conditional

## Conditions

- condition

## Destination Notes

- destination customs/import notes

## Return-to-US Notes

- CBP/agriculture/wildlife notes

## Practical Recommendation

- exact packing action

## Sources Checked

- source — access date
```

## Output Format: Country Packing List

```markdown
## Trip Snapshot

Countries:
Dates / season:
Airline/routing:
Assumptions:

## Must Bring

- item — reason

## Carry-On Only

- item — reason

## Checked-Bag OK

- item — reason

## Buy There

- item — reason

## Leave Home

- item — reason

## Country Notes

### <country>
Entry:
Money:
Power:
Customs/baggage:
What to bring:
Gotchas:

## Verify Before Departure

- airline baggage limits
- destination customs page
- medicine rules if applicable
- return-to-US restrictions for souvenirs or food

## Sources Checked

- source — access date
```

## Common Rules To Re-Verify

Do not answer these from memory without current research:

- liquid limits and airport CT-scanner exceptions
- power bank and lithium battery limits
- drone batteries and drone registration rules
- aerosols and flammable toiletries
- knives, tools, sporting equipment, camping gear, and souvenirs
- medication, injectables, syringes, and refrigerated medication
- meat, dairy, seeds, plants, soil, shells, coral, leather, fur, honey, cheese, and cured foods
- alcohol and tobacco allowances
- large cash or negotiable instruments
- VAT refund rules
- country-specific plug types and voltage for less common destinations

## Quality Bar

A good answer:

- gives a direct carry-on vs checked verdict
- explains which rule layer applies
- cites current sources
- identifies airline-specific and destination-specific uncertainty
- includes return-to-US gotchas
- ends with an exact packing recommendation
