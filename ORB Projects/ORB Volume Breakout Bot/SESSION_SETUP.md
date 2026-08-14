# Setting the session times — plain English

The bot trades a **London range** and a **New York open**. Those two things run on
different clocks, and the clocks do not stay a fixed distance apart: the UK and
US change their clocks on different weekends, so for about four weeks a year the
New York opening bell happens at **13:30 London** instead of the usual 14:30.

So the settings are split into two boxes, **one per clock**. Each box has its own
time-zone dropdown at the top. **A time is always read in the zone of the box it
sits in** — you never have to work out which clock a field is on.

---

## Session 1 — Range Window

| Setting | What it means |
|---|---|
| **Range Time Zone** | The clock the range start below is read in. Leave on `EuropeLondon`. |
| **Range Start** | When the bot begins recording the high and low. `08:00:00` = 8am London. |

That's it — the range *end* is in the next box, because the range ends at the New
York bell, which is a New York time.

---

## Session 2 — Trading Window

| Setting | What it means |
|---|---|
| **Trading Time Zone** | The clock everything below is read in. Leave on `AmericaNewYork`. |
| **Range End / Market Open** | When the range stops recording. `09:30:00` = the NYSE bell. |
| **First Entry Time** | Earliest the bot may open a trade. `09:31:00` = one minute after the bell. |
| **Enable Last Entry Cutoff** | Set to `Yes` if you want entries to stop at a set time. |
| **Last Entry Time** | **No NEW trades after this.** A trade already open is left alone to reach its stop or target. |
| **Enable Force Close** | Set to `Yes` if you want any open trade closed at a set time. |
| **Force Close Time** | Closes whatever is still open. Use this to make sure you are flat before the close. |

### The two "end" settings are not the same thing

This is the part that catches people out:

- **Last Entry Time** stops the bot *taking* new trades. It does not touch a trade
  that is already running.
- **Force Close Time** closes a trade that is still open, whatever it is doing.

If you want a one-hour entry window but trades allowed to run afterwards, set
**Last Entry Time** to the end of your hour and **Force Close Time** to late in the
day. If you want everything shut at the end of the hour, set both the same.

---

## Session 3 — Legacy

**Ignore Zones - Use Fixed UTC.** Leave this **off**. Turning it on ignores both
time-zone dropdowns and reads every time as a plain UTC clock — which is the old
behaviour, correct only from November to March and an hour out for the rest of
the year.

---

## Worked example: a 09:31–10:31 New York window

This is the original method — London range, entries only in the hour after the
bell, trade left to run to its target afterwards.

```
Session 1 - Range Window
  Range Time Zone .................. EuropeLondon
  Range Start ...................... 08:00:00        <- 8am London

Session 2 - Trading Window
  Trading Time Zone ................ AmericaNewYork
  Range End / Market Open .......... 09:30:00        <- the bell
  First Entry Time ................. 09:31:00        <- window opens
  Enable Last Entry Cutoff ......... Yes
  Last Entry Time .................. 10:31:00        <- window closes
  Enable Force Close ............... Yes
  Force Close Time ................. 16:00:00        <- flat by the NY close

Session 3 - Legacy
  Ignore Zones - Use Fixed UTC ..... No
```

**To move the window later** — say 10:00 to 11:00 New York — change only two
fields: **First Entry Time** to `10:00:00` and **Last Entry Time** to `11:00:00`.
Nothing else needs touching, and it stays correct through every clock change.

---

## Checking it is working

On the first bar of each day the bot writes a line to the log starting
`SESSION_TIMEZONE`. It shows the resolved times converted to UTC, for example:

```
SESSION_TIMEZONE mode=Local rangeTz=EuropeLondon execTz=AmericaNewYork
  rangeUtc=07:00-13:30 tradingStartUtc=13:31 killUtc=14:31 closeUtc=20:00
```

Those UTC numbers **shift by an hour across the year** — that is the fix working,
not a fault. What must stay constant is the gap: `tradingStartUtc` should always
be one minute after `rangeUtc`'s end.
