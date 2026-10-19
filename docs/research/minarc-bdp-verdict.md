# The knuckle design is the new verified leader (2026-10-16)

Two independent checks re-measured the min-arc stop knuckle (BDp), and neither could break it.
- **On the full test bench:** gap 19.54 (score 92.9), including machining tolerance on its stops. The old leader, H1,
  scores 27.20.
- **On 1154 poses neither design was fitted to:** 24.18, against H1's 31.39.

Every rule holds: the 5-degree fold margin, a real dowel stop and O20 hubs.

**The cost.** It has 4 joints instead of 3, and the spring-held knuckle needs a sensor. Complexity is 33, against H1's
19.5.

**The weak spot.** Hub 2 comes within 0.05 mm of the skin at the top of an overhead raise.

**The feel at the stops** (`docs/research/fold-stop-feel.md`):
- a light click (0.5-2 mJ), with no jam;
- about 0.2 N of friction at the cuff;
- about 1.5 N of spring once the knuckle opens (an estimate);
- among your motions, only "wash opposite shoulder" opens it.
