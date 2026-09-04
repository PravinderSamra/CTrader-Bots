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
import urllib.error
import urllib.request

SCOPE = "https://www.googleapis.com/auth/datastore"
API_ROOT = "https://firestore.googleapis.com/v1"
MAX_WRITES_PER_COMMIT = 500  # Firestore's hard cap
BATCH_SIZE = 400             # stay comfortably under it, as sync-trades.ts does

SERVICE_ACCOUNT_ENV = "FIREBASE_SERVICE_ACCOUNT_JSON"


class FirestoreError(RuntimeError):
    pass


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
        try:
            info = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FirestoreError(
                f"{SERVICE_ACCOUNT_ENV} is not valid JSON: {exc}"
            ) from exc

        self.project_id = project_id or info.get("project_id")
        if not self.project_id:
            raise FirestoreError("No project_id in the service account JSON.")

        try:
            from google.oauth2 import service_account
        except ImportError as exc:  # pragma: no cover
            raise FirestoreError(
                "google-auth is required: pip install google-auth"
            ) from exc

        self._creds = service_account.Credentials.from_service_account_info(
            info, scopes=[SCOPE]
        )
        self._base = (
            f"{API_ROOT}/projects/{self.project_id}/databases/(default)/documents"
        )

    def _token(self) -> str:
        from google.auth.transport.requests import Request

        if not self._creds.valid:
            self._creds.refresh(Request())
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
                "name": f"{self._base}/{collection}/{doc_id}",
                "fields": encode_fields(fields),
            }
        }
