#!/usr/bin/env python3
"""
sync_archive.py — commit and push the evidence archive, and nothing else.

The container is ephemeral and the repo is cloned fresh each session, so a
journal entry that is written but never pushed dies with the container. Nothing
committed it automatically: the stop hook only *asks* the model to, and a
session that ends early, errors, or simply forgets loses the scan.

That is the one failure this project cannot absorb. The whole method — the
3-day thresholds, the hypothesis register, comparing today against every
previous day — rests on the archive being complete. A silently missing session
does not announce itself; it just makes the evidence quietly wrong, which is
the same shape as every defect recorded in HYPOTHESES.md.

**Scope is deliberately narrow.** Only the archive paths are staged, never code.
A scan must never push half-finished work as a side effect.

    python3 sync_archive.py            # commit + push if anything changed
    python3 sync_archive.py --no-push  # commit only
"""
import os, subprocess, sys, time

PATHS = [
    "NAS100 Daily Brief agent skill/journal",
    "NAS100 Daily Brief agent skill/research/chart-ladders",
    "NAS100 Daily Brief agent skill/research/live-walls",
    # gexbot/ladders was tracked in git but missing from this list, so every
    # scan wrote two ladder files that were never staged. They then sat
    # untracked while origin gained the same paths from another session, and
    # the rebase below died on "untracked working tree files would be
    # overwritten" — which is how a scan that ran fine pushed nothing on
    # 2026-09-10. Writing a path the archive does not carry is the same defect
    # as not writing it at all.
    "NAS100 Daily Brief agent skill/research/gexbot/ladders",
]


def _repo_root(start=None):
    d = start or os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=d,
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def _git(root, *args, check=False):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r


def sync(push=True, message=None):
    root = _repo_root()
    if not root:
        return {"ok": False, "why": "not a git repository"}

    existing = [p for p in PATHS if os.path.exists(os.path.join(root, p))]
    if not existing:
        return {"ok": True, "why": "no archive paths present"}

    _git(root, "add", "--", *existing)
    # Anything actually staged for those paths?
    diff = _git(root, "diff", "--cached", "--name-only", "--", *existing)
    changed = [l for l in diff.stdout.splitlines() if l.strip()]
    if not changed:
        # Nothing NEW to commit is not the same as "the archive is safe". A
        # previous run in this container may have committed and then failed to
        # push — that is D11's exact failure — and this path used to return
        # "already up to date" and exit 0, so the retry never happened and the
        # observation stayed stranded until the container was reclaimed.
        if not push:
            return {"ok": True, "why": "archive already up to date", "files": 0}
        branch = (_git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
                  or "main")
        out = {"ok": True, "files": 0}
        _push_and_verify(root, branch, out)
        out["why"] = ("archive already up to date" if out["pushed"] else
                      out.get("why", "unpushed local commits remain"))
        return out

    msg = message or (
        f"NAS100 archive: {len(changed)} file(s) from a scan/review\n\n"
        "Journal entries, chart ladders and live-wall snapshots. Committed by "
        "sync_archive.py so the evidence survives the container — the archive "
        "is what every threshold and cross-day comparison is computed from."
    )
    # Commit ONLY these paths. Leaves any staged code changes alone.
    c = _git(root, "commit", "-m", msg, "--", *existing)
    if c.returncode:
        return {"ok": False, "why": f"commit failed: {c.stderr.strip()[:200]}"}

    out = {"ok": True, "committed": len(changed), "files": changed[:10]}
    if not push:
        out["pushed"] = False
        return out

    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "main"
    _push_and_verify(root, branch, out)
    return out


def _push_and_verify(root, branch, out):
    """Push, then ask ORIGIN what it has. Sets out["pushed"] to that answer.

    main is a busy branch: xauusd-data-bot and GEX Agent Bot both push to it on
    their own schedules, so a scan losing the race is the normal case, not the
    exception. Rebase-and-retry is therefore the main path through this loop
    rather than an error path.
    """
    for attempt in range(4):
        if _git(root, "push", "origin", branch).returncode == 0:
            break
        # Someone else moved the branch — rebase this commit on top and retry.
        # --autostash because the scan leaves unrelated scratch in the tree
        # (chart SVGs, /tmp fixtures re-read into the repo) and a rebase that
        # refuses on a dirty tree loses the whole observation over a file that
        # was never going to be committed.
        _git(root, "fetch", "origin", branch)
        rb = _git(root, "rebase", "--autostash", f"origin/{branch}")
        if rb.returncode:
            _git(root, "rebase", "--abort")
            # Do NOT give up here. A conflict on this attempt is usually
            # index.json touched by a concurrent scan, and the next loop
            # re-fetches a settled origin. Only a conflict that survives every
            # attempt is a real one.
            if attempt == 3:
                out["pushed"] = False
                out["why"] = ("push rejected and rebase conflicted on every "
                              "attempt — push by hand")
                return
        time.sleep(2 ** attempt)

    # Whether the push command returned 0 is NOT evidence the commit is on
    # origin. On 2026-09-10 a scan pushed successfully, then a later rebase
    # --abort rewound the local branch off the commit it had just pushed, and
    # the local repo no longer contained what origin held. Both directions of
    # that confusion are silent. So ask origin what it actually has, and report
    # only that.
    _git(root, "fetch", "origin", branch)
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    landed = _git(root, "merge-base", "--is-ancestor", head,
                  f"origin/{branch}").returncode == 0
    out["pushed"] = landed
    out["head"] = head[:9]
    if not landed:
        out["why"] = (f"push did not land — origin/{branch} does not contain "
                      f"{head[:9]}; commit and push by hand")


if __name__ == "__main__":
    want_push = "--no-push" not in sys.argv
    r = sync(push=want_push)
    if not r.get("ok"):
        print(f"ARCHIVE SYNC FAILED — {r.get('why')}", file=sys.stderr)
        sys.exit(1)

    # Check "did it reach origin" BEFORE the tidy summaries. The files==0 path
    # can also be unpushed — a commit stranded by an earlier failed push — and
    # ordering this last is how that stayed quiet.
    if want_push and not r.get("pushed"):
        n = r.get("committed", 0)
        where = (f"{n} file(s) committed locally as {r.get('head')}" if n
                 else f"local commits ({r.get('head')})")
        print(f"ARCHIVE NOT PUSHED — {where} but NOT on origin: "
              f"{r.get('why')}", file=sys.stderr)
        for f in r.get("files", []):
            print(f"   {f}", file=sys.stderr)
        sys.exit(1)

    if not r.get("committed"):
        print(f"archive: {r.get('why')}")
    else:
        pushed = f"pushed=True ({r.get('head')})" if want_push else "not pushed"
        print(f"archive: committed {r['committed']} file(s), {pushed}")
        for f in r.get("files", []):
            print(f"   {f}")
