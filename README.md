This program forecasts GTA VI trophy earn rates one week out as five quantiles per trophy.

The model uses a per‑trophy trend of logit(rate) against ln(1 + hours since release). It is fitted by weighted least squares on the case history, with the slope shrunk 65/35 toward a tier prior (platinum .55, gold .75, silver .90, bronze 1.00) and clamped to [-0.5, 2.5]. Saturation damping is applied as rates approach 50 +, caps are added for rare trophies, and the spread combines a 0.5 × sqrt(horizon‑days) random walk with the fit residuals.

The main entry point is `main.py`, while the mathematical core lives in `model.py`.

Validation is performed against the practice histories, which are the flat pre‑refresh launch page. This validates format and runtime, not accuracy.
