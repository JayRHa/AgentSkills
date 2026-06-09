# Worked Example: "5 days in Tokyo, mid budget, love food and temples"

This shows the full skill flow from a one-line prompt to a delivered plan. Costs are illustrative estimates (USD) and must be verified near travel.

## Step 1 — Confirm the frame
- **Destination:** Tokyo (single base)
- **Duration:** 5 days / 5 nights, assumed spring (cherry-blossom shoulder, mild)
- **Travelers:** 2 adults (couple), assumed no mobility constraints
- **Budget:** assumed all-in ~$3,000 for two, flights included
- **Interests:** food, temples; secondary: neighborhoods, views
- **Pace:** balanced
- **Origin:** assumed US West Coast (~11h flight, large time-zone shift → jet lag day 1)

*Assumptions stated; user can correct.*

## Step 2 — Budget envelope (mid tier)
Using `scripts/budget_calc.py allocate --total 3000 --tier mid`:

| Category | % | Amount |
|---|---|---|
| Transport | 30% | $900 |
| Lodging | 30% | $900 |
| Food | 18% | $540 |
| Activities | 10% | $300 |
| Local transit | 4% | $120 |
| Buffer | 8% | $240 |

Reality check: round-trip flights from US West Coast often exceed $900 alone in spring, so flights may push this toward tight. Flag to user: either raise budget, travel off-peak, or treat $3,000 as on-the-ground-only.

## Step 3 — Base
Stay near **Shinjuku or Tokyo Station / Yaesu** — both are major rail hubs giving fast access to all zones. Pick Shinjuku for nightlife/food density; Tokyo Station for calm + Shinkansen access if a day trip is added.

## Step 4 — Highlight pool (ranked by fit: food + temples)
| # | Experience | Zone | Duration | Cost | Best time | Book? |
|---|---|---|---|---|---|---|
| 1 | Sensō-ji temple + Nakamise street | Asakusa | 2h | free/$ | early AM | no |
| 2 | Tsukiji Outer Market food crawl | Tsukiji | 2h | $$ | morning | no |
| 3 | Meiji Shrine + Yoyogi Park | Harajuku | 1.5h | free | morning | no |
| 4 | Sushi/izakaya dinner (Shinjuku) | Shinjuku | 1.5h | $$$ | evening | yes |
| 5 | teamLab digital art museum | Odaiba/Toyosu | 2.5h | $$ | timed | yes (timed) |
| 6 | Shibuya Crossing + Sky observation | Shibuya | 1.5h | $$ | sunset | recommended |
| 7 | Ramen + in-area food hopping | varies | 1h | $ | any | no |
| 8 | Day trip: Nikkō or Kamakura temples | out of city | full day | $$ | full day | no |
| 9 | Tokyo National Museum | Ueno | 2h | $ | midday | no |

## Step 5 — Geographic zones
- **East/Old Tokyo:** Asakusa, Ueno, Tsukiji
- **West/Modern:** Shibuya, Harajuku, Shinjuku
- **Waterfront:** Toyosu/Odaiba (teamLab)
- **Out-of-city:** Kamakura (temples + coast, ~1h by train)

## Step 6–7 — Sequenced days

**Day 1 — Arrival (light).** Land, train/limousine bus to lodging, settle. Easy dinner near base (ramen or izakaya), short orientation walk. Nothing ticketed — jet lag. Day cost ~$45/pp.

**Day 2 — East/Old Tokyo.** 8:00 Sensō-ji before crowds → Nakamise snacks → Ueno (Tokyo National Museum, midday/indoor) → late afternoon Tsukiji-area food. Dinner in Asakusa. Balanced, one zone, minimal transit. Day cost ~$70/pp. *Rainy swap:* more museum time in Ueno.

**Day 3 — West/Modern.** Morning Meiji Shrine + Yoyogi Park (temple fix + greenery) → Harajuku/Omotesandō lunch + browse → late afternoon Shibuya, sunset at a sky observation deck → izakaya dinner in Shinjuku (reserved). Day cost ~$95/pp. *Rainy swap:* indoor shopping complexes, skip park.

**Day 4 — Day trip: Kamakura.** Train out (~1h). Great Buddha, Hase-dera, Komachi-dori food street, beach if warm. Back by evening; light dinner near base. This is the flex/variety day; if weather is bad, swap with Day 5 plan. Day cost ~$80/pp.

**Day 5 — Waterfront + departure prep OR teamLab.** If late flight: morning teamLab (timed ticket booked) → lunch → return for luggage → airport. If early flight: move teamLab earlier in the week and keep Day 5 minimal. Day cost ~$75/pp.

## Step 8 — Connective tissue
- **Airport transfer:** Narita Express or Limousine Bus (~$30/pp each way); Haneda is cheaper/closer if available.
- **Connectivity:** eSIM ordered before arrival.
- **Payments:** carry cash — many small eateries are cash-only; IC card (Suica/Pasmo) for transit and convenience stores.
- **Local transit:** load an IC card; a multi-day subway pass can pay off given the zone-hopping.
- **Reservations now:** teamLab timed ticket; one nice dinner; Shibuya sky deck.

## Step 9 — Reconcile
On-the-ground estimate via `budget_calc.py estimate --days 5 --travelers 2 --daily 75 --lodging 130 --flights 1400 --buffer 0.12`:
- On-the-ground: 5 x 2 x $75 = $750
- Lodging: 5 x $130 = $650
- Flights: $1,400
- Subtotal: $2,800 + 12% buffer ($336) = **$3,136**

Slightly over the $3,000 frame. Trade-downs offered: (1) lodging one tier down to ~$100/night saves $150; (2) shift one $$$ dinner to a casual spot. Applying both lands near budget while protecting the signature food + temple experiences.

## Step 10 — Deliver + caveat
Present the day-by-day, the reconciled budget table, packing pointer (spring = layers + packable rain jacket + comfortable walking shoes for ~8 km/day), and remind: verify temple/museum hours (some close Mondays), book timed entries, and confirm flight-day transfer times.
