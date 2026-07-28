# Archive — do not run these

Reference copies of the **pre-fix** ORB bot, kept only so the v2.0 changes can be
diffed and audited.

| File | Notes |
|---|---|
| `ORB_Bot_Original.cs` | The version reviewed in `../docs/Phase1_Review_and_Spec.md`. Contains the ORB-lock inconsistency, phantom-entry, position-sizing and naked-entry defects. |

The bot to actually run is **`../ORB_Bot.cs`** (v2.0).

A byte-identical duplicate of this file previously sat in the parent folder as
`ORB_Bot_V_Code_ORB_lock_fixed.cs`; it was removed to avoid confusion and remains
recoverable from git history.
