"""
Minimal Firestore writer for the GexBot recorder.

Why the REST API rather than a client library: the rest of Gex-Bot is plain
Python, and this keeps the recorder to a single runtime in CI. The only
dependency is `google-auth`, purely to turn the service-account JSON into an
OAuth token. `xauusd-dashboard/scripts/sync-trades.ts` does the equivalent
server-side write with firebase-admin -- both bypass Firestore rules by
design, as that file's comment explains.

Credentials come from the same FIREBASE_SERVICE_ACCOUNT_JSON secret the
dashboard's sync already uses.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

SCOPE = "https://www.googleapis.com/auth/datastore"
API_ROOT = "https://firestore.googleapis.com/v1"
MAX_WRITES_PER_COMMIT = 500  # Firestore's hard cap
BATCH_SIZE = 400             # stay comfortably under it, as sync-trades.ts does

SERVICE_ACCOUNT_ENV = "FIREBASE_SERVICE_ACCOUNT_JSON"


class FirestoreError(RuntimeError):
    pass


def _candidates(raw: str):
    """Yield (label, text) repair candidates for a possibly-mangled secret.

    Two corruptions have been seen in practice, and they need opposite fixes:

    - **Escapes expanded.** The private key's backslash-n became real newlines.
      Illegal inside a JSON string, but the value is what we want -- PEM needs
      real newlines. Fixed by parsing leniently.
    - **Hard-wrapped.** Newlines were injected at arbitrary column positions,
      including mid-word: the observed failure was
      MismatchedTags("PRIVATE \\nKEY", "PRIVATE KEY"). Here the escapes are
      intact and every literal newline is corruption, so they must be stripped
      -- the opposite of the fix above. Removing them is safe because JSON
      ignores whitespace between tokens, and no field in a service account file
      legitimately contains a raw newline.

    Rather than guess which happened, every candidate is handed to the crypto
    library and the first one that yields usable credentials wins. That makes
    the key itself the oracle instead of our inference.
    """
    yield "as stored", raw
    unwrapped = raw.replace("\r", "").replace("\n", "")
    if unwrapped != raw:
        yield "with injected line breaks removed", unwrapped


def _parse_service_account(raw: str, warn: bool = True) -> dict:
    """Parse the service account JSON, tolerating a mangled private key.

    A downloaded service account file escapes the newlines in `private_key` as
    a literal backslash-n, which is valid JSON. It is easy to lose that in
    transit -- pasting through an editor or a shell that expands escapes turns
    them into real newlines, which are control characters and illegal inside a
    JSON string. The strict parser then fails at line 5, the private key.

    json.loads(..., strict=False) permits control characters inside strings and
    yields exactly the value we want anyway: PEM keys need real newlines, which
    is what the escapes would have decoded to. So the relaxed parse is a
    repair, not a fudge -- but it means the stored secret is malformed, so say
    so rather than fixing it silently.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError as strict_exc:
        try:
            info = json.loads(raw, strict=False)
        except json.JSONDecodeError:
            raise FirestoreError(
                f"{SERVICE_ACCOUNT_ENV} is not valid JSON: {strict_exc}. "
                "Re-copy the service account file verbatim into the secret."
            ) from strict_exc
        if warn:
            print(
                f"WARN: {SERVICE_ACCOUNT_ENV} contains unescaped newlines "
                f"({strict_exc}) -- parsed leniently. The secret is malformed: "
                "re-copy the downloaded service account file verbatim to fix it.",
                file=sys.stderr,
            )
        return info


def load_credentials(raw: str):
    """Build Google credentials from the secret, repairing it if necessary.

    Returns (credentials, service_account_info). Each repair candidate is
    validated by actually constructing the credentials, so a candidate that
    parses as JSON but yields a broken PEM key is rejected rather than used.
    """
    try:
        from google.oauth2 import service_account
    except ImportError as exc:  # pragma: no cover
        raise FirestoreError(
            "google-auth is required: pip install google-auth"
        ) from exc

    attempts = []
    for label, text in _candidates(raw):
        try:
            info = _parse_service_account(text, warn=False)
        except FirestoreError as exc:
            attempts.append(f"{label}: {exc}")
            continue
        try:
            creds = service_account.Credentials.from_service_account_info(
                info, scopes=[SCOPE]
            )
        except (ValueError, TypeError, KeyError) as exc:
            attempts.append(f"{label}: {exc}")
            continue

        if label != "as stored":
            print(
                f"WARN: {SERVICE_ACCOUNT_ENV} is malformed but was repaired "
                f"({label}). Re-add the secret from the downloaded service "
                "account file to remove this warning.",
                file=sys.stderr,
            )
        return creds, info

    detail = "; ".join(attempts) or "no candidates"
    raise FirestoreError(
        f"{SERVICE_ACCOUNT_ENV} could not be loaded -- the stored secret is "
        f"corrupted and no repair worked [{detail}]. Re-add it by copying the "
        "downloaded service account .json file verbatim, with no reformatting "
        "or line wrapping (on a desktop: "
        "gh secret set FIREBASE_SERVICE_ACCOUNT_JSON < service-account.json)."
    )


# ── value encoding ────────────────────────────────────────────────────────────
# Firestore's REST API wants every value tagged with its type. Getting this
# wrong is the easiest way to silently write junk, so it is kept small,
# explicit and unit-tested (see __tests__/test_firestore_encoding.py).

def encode_value(v):
    if v is None:
        return {"nullValue": None}
    if isinstance(v, bool):                 # must precede int -- bool is an int
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}     # REST expects int64 as a string
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, (list, tuple)):
        for x in v:
            # Firestore rejects an array whose elements are arrays with
            # "Nested arrays are not allowed". Fail here, naming the fix,
            # rather than sending a payload the API will refuse. Wrap each
            # element in a map instead (see _pairs_to_maps in
            # record_snapshot.py).
            if isinstance(x, (list, tuple)):
                raise TypeError(
                    "Firestore does not allow nested arrays; wrap each inner "
                    "array in a map before encoding"
                )
        return {"arrayValue": {"values": [encode_value(x) for x in v]}}
    if isinstance(v, dict):
        return {"mapValue": {"fields": encode_fields(v)}}
    raise TypeError(f"unsupported Firestore value type: {type(v).__name__}")


def encode_fields(d: dict) -> dict:
    return {k: encode_value(v) for k, v in d.items()}


# ── client ────────────────────────────────────────────────────────────────────

class FirestoreSink:
    def __init__(self, service_account_json: str | None = None,
                 project_id: str | None = None):
        raw = service_account_json or os.environ.get(SERVICE_ACCOUNT_ENV)
        if not raw:
            raise FirestoreError(
                f"{SERVICE_ACCOUNT_ENV} is not set -- cannot write to Firestore."
            )
        self._creds, info = load_credentials(raw)

        self.project_id = project_id or info.get("project_id")
        if not self.project_id:
            raise FirestoreError("No project_id in the service account JSON.")
        # Two different things that look alike, and mixing them up is a 400:
        #   _doc_root is a RESOURCE PATH, used for a document's "name" field.
        #             Firestore requires it to begin with "projects/".
        #   _base     is a URL, used to address the REST endpoint.
        self._doc_root = (
            f"projects/{self.project_id}/databases/(default)/documents"
        )
        self._base = f"{API_ROOT}/{self._doc_root}"

    def _token(self) -> str:
        try:
            from google.auth.transport.requests import Request
        except ImportError as exc:
            # google-auth signs the assertion but leaves the HTTP exchange to a
            # transport, and does not pull one in itself.
            raise FirestoreError(
                "google-auth's Request transport needs the requests package: "
                "pip install google-auth requests"
            ) from exc

        from google.auth.exceptions import RefreshError

        if not self._creds.valid:
            try:
                self._creds.refresh(Request())
            except RefreshError as exc:
                # The key was well-formed enough to sign with, so this is
                # Google rejecting the account rather than a malformed secret:
                # deleted service account, wrong project, or disabled key.
                raise FirestoreError(
                    f"Google rejected the service account: {exc}. The key "
                    "parsed and signed correctly, so check the account still "
                    "exists, is enabled, and belongs to this project."
                ) from exc
        return self._creds.token

    def commit(self, writes: list[dict]) -> int:
        """Apply document writes. Returns the number applied."""
        if not writes:
            return 0

        applied = 0
        for i in range(0, len(writes), BATCH_SIZE):
            chunk = writes[i:i + BATCH_SIZE]
            body = json.dumps({"writes": chunk}).encode("utf-8")
            req = urllib.request.Request(
                f"{self._base}:commit",
                data=body,
                headers={
                    "Authorization": f"Bearer {self._token()}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    json.loads(resp.read().decode("utf-8"))
                applied += len(chunk)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:400]
                raise FirestoreError(
                    f"Firestore commit failed: HTTP {exc.code} {detail}"
                ) from exc
            except urllib.error.URLError as exc:
                raise FirestoreError(
                    f"Could not reach Firestore: {exc.reason}"
                ) from exc
        return applied

    def make_write(self, collection: str, doc_id: str, fields: dict) -> dict:
        """A full-document write. No updateMask, so this replaces the document.

        That is what we want in both collections: history doc ids embed the
        source timestamp so a rewrite is byte-identical, and the latest doc is
        meant to be overwritten each poll.
        """
        return {
            "update": {
                # A resource path, NOT a URL -- see _doc_root above.
                "name": f"{self._doc_root}/{collection}/{doc_id}",
                "fields": encode_fields(fields),
            }
        }
