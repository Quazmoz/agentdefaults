---
title: Use the published household price-level index for wider purchasing-power pricing
author: Quinn
date: 2026-11-20
branch: main
id: l-23763518
scope: repo
status: active
src: agent
touches:
  - skills/google-play-localized-pricing.md
---

## Decided

For a data-backed expansion beyond the fixed factors in skills/google-play-localized-pricing.md, use the World Bank household price-level index because it already expresses the cost of household consumption relative to the United States on a US=100 scale. Use Play's pricing converter for exact local price points, then compare those quotes with current Play prices.

## Tried and ruled out

Dividing a raw private consumption PPP by the official FX rate was considered before finding the direct World Bank series. The published index uses the World Bank's chosen market exchange rate basis, so reconstructing it from an official FX series can give a different result. GDP PPP values alone also use a broader spending basket than household consumption.

## Watch out

In the code: the World Bank series is PA.NUS.PRVT.PLI, with methodology at https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.PRVT.PLI. The PA.NUS.GDP.PLI series has wider recent coverage in some countries, but any use is a proxy and should be labeled. A price-level index is a benchmark for the relative cost of a basket. Revenue and paid conversion still require app-specific evidence. Keep the audit choices and the exact approved scope separate from the canonical ten-market policy.
