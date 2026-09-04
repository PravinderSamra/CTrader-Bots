#!/usr/bin/env python3
"""Tests for the Firestore REST value encoder.

The encoder is the one part of the sink that can fail silently -- a wrong type
tag writes junk rather than erroring -- and it is testable without
credentials, so it is covered here.

Run: python3 __tests__/test_firestore_encoding.py
"""

import os
import sys
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json  # noqa: E402

from firestore_sink import (  # noqa: E402
    FirestoreError,
    _parse_service_account,
    encode_fields,
    encode_value,
)

# A service account file, and the corruption seen in CI: the private key's
# newline escapes expanded into real newlines, which are control characters
# and illegal inside a JSON string.
_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "pravzella-test",
    "private_key_id": "abc123",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANB\n-----END PRIVATE KEY-----\n",
    "client_email": "svc@pravzella-test.iam.gserviceaccount.com",
}
_VALID_TEXT = json.dumps(_SERVICE_ACCOUNT, indent=2)
_MANGLED_TEXT = _VALID_TEXT.replace("\\n", "\n")


class TestParseServiceAccount(unittest.TestCase):
    def test_valid_json_parses(self):
        self.assertEqual(
            _parse_service_account(_VALID_TEXT)["project_id"], "pravzella-test"
        )

    def test_mangled_private_key_is_recovered(self):
        # The first CI run failed here: "Invalid control character at: line 5".
        with self.assertRaises(json.JSONDecodeError):
            json.loads(_MANGLED_TEXT)

        info = _parse_service_account(_MANGLED_TEXT)
        # The recovered key must equal what the escaped original decodes to --
        # otherwise this is papering over corruption rather than repairing it.
        self.assertEqual(info["private_key"], _SERVICE_ACCOUNT["private_key"])
        self.assertIn("\n", info["private_key"])  # PEM needs real newlines
        self.assertEqual(info["project_id"], "pravzella-test")

    def test_genuinely_broken_json_still_raises(self):
        with self.assertRaises(FirestoreError):
            _parse_service_account("{not json at all")


try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    import firestore_sink

    _CRYPTO = True
except ImportError:  # pragma: no cover
    _CRYPTO = False


@unittest.skipUnless(_CRYPTO, "cryptography/google-auth not installed")
class TestLoadCredentials(unittest.TestCase):
    """Repairing a mangled secret, validated against a real RSA key.

    Both corruptions below were hit for real in CI. They need opposite fixes,
    which is why the loader validates each candidate by building credentials
    rather than guessing which one happened.
    """

    @classmethod
    def setUpClass(cls):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        cls.email = "svc@pravzella-test.iam.gserviceaccount.com"
        cls.good = json.dumps({
            "type": "service_account",
            "project_id": "pravzella-test",
            "private_key_id": "abc123",
            "private_key": cls.pem,
            "client_email": cls.email,
            "token_uri": "https://oauth2.googleapis.com/token",
        })

    def _assert_recovers_real_key(self, text):
        creds, info = firestore_sink.load_credentials(text)
        self.assertEqual(creds.service_account_email, self.email)
        # The key must be the real one, not merely something that parsed --
        # that distinction is the whole point of validating each candidate.
        self.assertEqual(info["private_key"], self.pem)

    def test_correct_secret(self):
        self._assert_recovers_real_key(self.good)

    def test_hard_wrapped_secret_is_repaired(self):
        # The second CI failure: newlines injected at fixed columns, landing
        # mid-word -- MismatchedTags("PRIVATE \nKEY", "PRIVATE KEY").
        self._assert_recovers_real_key("\n".join(textwrap.wrap(self.good, 64)))

    def test_expanded_escapes_are_repaired(self):
        # The first CI failure: "Invalid control character at: line 5".
        self._assert_recovers_real_key(self.good.replace("\\n", "\n"))

    def test_unrecoverable_secret_raises_with_guidance(self):
        # Wrapping on top of expanded escapes destroys the PEM line structure.
        # Failing loudly beats handing back a subtly broken key.
        both = "\n".join(textwrap.wrap(self.good.replace("\\n", "\n"), 64))
        with self.assertRaises(FirestoreError) as ctx:
            firestore_sink.load_credentials(both)
        self.assertIn("Re-add it", str(ctx.exception))


class TestEncodeValue(unittest.TestCase):
    def test_none(self):
        self.assertEqual(encode_value(None), {"nullValue": None})

    def test_bool_before_int(self):
        # bool is a subclass of int in Python; if the int branch ran first,
        # True would be written as the integer 1 and every boolean field in
        # the recorder (regimes_agree, walls_agree) would be silently wrong.
        self.assertEqual(encode_value(True), {"booleanValue": True})
        self.assertEqual(encode_value(False), {"booleanValue": False})

    def test_int_is_stringified(self):
        # Firestore REST represents int64 as a string.
        self.assertEqual(encode_value(5), {"integerValue": "5"})
        self.assertEqual(encode_value(-1788552000), {"integerValue": "-1788552000"})

    def test_float(self):
        self.assertEqual(encode_value(1.5), {"doubleValue": 1.5})
        self.assertEqual(encode_value(-5668.521), {"doubleValue": -5668.521})

    def test_string(self):
        self.assertEqual(encode_value("SPX"), {"stringValue": "SPX"})

    def test_array(self):
        self.assertEqual(
            encode_value([1, 2.5]),
            {"arrayValue": {"values": [
                {"integerValue": "1"}, {"doubleValue": 2.5},
            ]}},
        )

    def test_nested_array_like_max_priors(self):
        # max_priors is a list of [strike, change] pairs -- the real shape.
        out = encode_value([[7715, 823541.587]])
        inner = out["arrayValue"]["values"][0]["arrayValue"]["values"]
        self.assertEqual(inner[0], {"integerValue": "7715"})
        self.assertEqual(inner[1], {"doubleValue": 823541.587})

    def test_map(self):
        self.assertEqual(
            encode_value({"a": 1}),
            {"mapValue": {"fields": {"a": {"integerValue": "1"}}}},
        )

    def test_unsupported_type_raises(self):
        with self.assertRaises(TypeError):
            encode_value({1, 2})  # a set

    def test_encode_fields_shape(self):
        self.assertEqual(
            encode_fields({"ticker": "SPX", "spot": 7717.85}),
            {"ticker": {"stringValue": "SPX"},
             "spot": {"doubleValue": 7717.85}},
        )


class TestRealRecord(unittest.TestCase):
    """Encode a record with the exact shape record_snapshot.py produces."""

    def test_full_record_round_trips(self):
        record = {
            "fetched_at": "2026-09-04T21:47:25.797291+00:00",
            "source_ts": 1788552000,
            "ticker": "SPX",
            "scope": "zero",
            "spot": 7717.85,
            "zero_gamma": 7712.5,
            "major_pos_vol": 7720,          # ints and floats both occur
            "sum_gex_vol": 311384.75,
            "sum_gex_oi": -5668.521,
            "min_dte": 0,
            "max_priors": [[7715, 823541.587], [7720, -628489.845]],
            "regime_vol": 1,
            "regimes_agree": False,         # the bool trap
            "walls_agree": False,
            "spot_vs_zero_gamma": 1,
        }
        fields = encode_fields(record)

        self.assertEqual(fields["ticker"], {"stringValue": "SPX"})
        self.assertEqual(fields["source_ts"], {"integerValue": "1788552000"})
        self.assertEqual(fields["spot"], {"doubleValue": 7717.85})
        self.assertEqual(fields["regimes_agree"], {"booleanValue": False})
        self.assertEqual(fields["major_pos_vol"], {"integerValue": "7720"})
        self.assertEqual(len(fields["max_priors"]["arrayValue"]["values"]), 2)
        # every field must carry exactly one type tag
        for name, value in fields.items():
            self.assertEqual(len(value), 1, f"{name} has {len(value)} type tags")


if __name__ == "__main__":
    unittest.main(verbosity=2)
