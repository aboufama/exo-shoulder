# The knuckle design is the new verified leader (2026-10-16)

Two independent checks re-measured the min-arc stop knuckle (BDp), and neither could break it.
- **On the full test bench:** gap 19.06 (score 93.1), against 27.20 for the old leader H1.
- **On 1154 poses neither design was fitted to:** 23.24, against H1's 31.39.

Every rule applies: the 5-degree fold margin, a real dowel stop on J2, O20 hubs, and only poses the arm reaches by
moving.

**The cost.** It has 4 joints instead of 3. The extra knuckle is spring-held but needs a sensor. Complexity is 33,
against H1's 19.5.

**The weak spot.** Hub 2 comes within 0.05 mm of the skin at the top of an overhead raise.

**The feel at the stops** (`docs/research/fold-stop-feel.md`):
- a light click at the J2 stop (0.5-2 mJ), with no jam;
- about 0.2 N of friction at the cuff;
- about 1.5 N of spring once the knuckle opens (estimated for the new spring);
- among your motions, only "wash opposite shoulder" opens it.
