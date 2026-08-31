# Configs

**Empty on purpose.** The strategy lives in the bot's own parameter defaults
(`src/DAX_RVOL_Breakout.cs`), so the first test needs **no config import at all** —
add the bot to a GER40 chart and the correct settings are already loaded.

A `.cbotset` was written here initially by copying the NAS100 config and editing the
DAX fields. It was removed: it carried **29 inherited NAS settings** that silently
overrode the DAX defaults on load, including

- `Bot Label Prefix = ORBV`, which would collide with the live NAS bot's trade labels
  and position history,
- `Enable Trend Filter = true`, an extra untested filter,
- `Min Risk Pips = 20` against a 25-point stop, close to blocking entries,
- `Enable Force Close = false`, so positions would not be flat before the Xetra close,
- `Enable Catch-Up Entry = true`, a path that bypasses the volume filter entirely.

A config file whose values disagree with the source defaults is worse than none. Once
the bot runs and the parameters are settled, export a `.cbotset` from cTrader itself
and commit it here — that one will be correct by construction.
