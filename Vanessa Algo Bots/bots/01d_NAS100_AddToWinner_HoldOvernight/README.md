# NAS100 London Range — v3.3 Hold Overnight, flat for the weekend

A copy of `01_NAS100_London_Range_AddToWinner` (v3.0) with one extra setting in "Session 2 – Trading Window":
**Force Close On Fridays Only**.

| Enable Force Close | Force Close On Fridays Only | Behaviour |
|---|---|---|
| Yes | (ignored) | Closes every day at Force Close Time (exactly v3.0) |
| **No** | **Yes** | **Holds overnight Monday–Thursday (until target or stop); closes everything at Force Close Time on Friday** |
| No | No | Holds until target or stop, including weekends |

Unchanged from v3.0:
- It never opens a new trade while a bot position is still open.
- Risk reduction, the add and the stop keep working across days.

On Fridays, no add is opened in the last "No Adds In Last Minutes" before the close.

Class `OrbVolumeBreakoutBotV33Hold`, label prefix `ORBVH`. Compiles with 0 errors and 0 warnings.
