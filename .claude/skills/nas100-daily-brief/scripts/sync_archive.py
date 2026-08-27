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
        return {"ok": True, "why": "archive already up to date", "files": 0}

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
    for attempt in range(4):
        p = _git(root, "push", "origin", branch)
        if p.returncode == 0:
            out["pushed"] = True
            return out
        # Someone else moved the branch — rebase this commit on top and retry.
        _git(root, "fetch", "origin", branch)
        rb = _git(root, "rebase", f"origin/{branch}")
        if rb.returncode:
            _git(root, "rebase", "--abort")
            out["pushed"] = False
            out["why"] = "push rejected and rebase conflicted — push by hand"
            return out
        time.sleep(2 ** attempt)
    out["pushed"] = False
    out["why"] = "push failed after 4 attempts"
    return out


if __name__ == "__main__":
    r = sync(push="--no-push" not in sys.argv)
    if not r.get("ok"):
        print(f"ARCHIVE SYNC FAILED — {r.get('why')}", file=sys.stderr)
        sys.exit(1)
    if r.get("files") == 0 or "committed" not in r:
        print(f"archive: {r.get('why')}")
    else:
        print(f"archive: committed {r['committed']} file(s), "
              f"pushed={r.get('pushed')}")
        for f in r.get("files", []):
            print(f"   {f}")
