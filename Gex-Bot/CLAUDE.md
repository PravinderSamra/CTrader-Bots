# Working rules for the Gex-Bot project

Written after four errors in this project that all had the **same shape**:
a conclusion drawn from one instance, or from inference, when a source that
would have settled it already existed and was not read.

| What was claimed | What was true | How the error was made |
|---|---|---|
| "No history exists on our tier" | `/hist/eod/` returns a full session | Guessed URL paths, read 404s as absence |
| "`?date=` is ignored" | The endpoint declares **no** parameters, and silently serves the prior session before 17:00 ET | Probed responses instead of reading the contract already extracted to disk |
| "24 videos are genuinely uncaptioned" | 6 had captions and auto-translation | Checked **one**, generalised to all |
| "The majors are exits, not entries" | Both uses are in the source, stated in one passage | Read one founder's preference as doctrine; quoted one trade as the rule |

None were reasoning failures. All four were **verification failures**.

## The rules

**1. Read the source before inferring from behaviour.**
Check `research/SOURCES.md` first — material already extracted in an earlier
session is easy to forget exists. Probing tells you what happened once;
documentation tells you what is guaranteed, what fails silently, and what
exists but is not yours. A 404 or a 200 from a guessed path is evidence about
your guess, not about the system.

**2. Never generalise from n=1. Check the set or state the n.**
If a claim covers a set ("all the videos", "every endpoint"), either test each
member or write the claim as "1 of N checked". Both are fine. Silently
promoting one observation to a universal is not.

**3. Attributed claims carry a verbatim quote and a location.**
Anything of the form "the vendor says" / "the author does" needs the words and
the timestamp or file. Then **read around it** — enough context to see whether
it is a rule or an aside.

**4. Distinguish these, explicitly:**
- a *rule* from a *preference* ("this is my setup" vs "that seems more effective")
- *the method* from *one trade* ("I always" vs "here I did")
- *disagreement between sources* from *one source being wrong* — two people can
  both be right about their own approach

**5. Prefer narrowing to overturning.**
When new material seems to contradict established understanding, first ask
whether both can be true. Three of the four errors above were "correcting"
something that was not wrong. A correction that turns out to be an
overstatement costs more than the original gap.

**6. Record the uncertainty you actually have.**
"Verified", "documented", "inferred" and "assumed" are different words. Use
the right one in the file. A confident sentence hiding a guess is what makes
the next session repeat the work.

**7. When a source is handed to you, that is an instruction, not context.**
Read it before doing the thing it would inform.

## Cheap checks that would have caught all four

- Before concluding a capability is absent: does a spec, bundle, FAQ or route
  table exist? Have I opened it *this session*?
- Before writing "all" / "every" / "none": what n did I actually check?
- Before writing "X was wrong": can both be true? Am I quoting a rule or a
  remark?
