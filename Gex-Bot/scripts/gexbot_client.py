"""
Minimal GexBot API client.

Auth is an `Authorization: Bearer <token>` header. The `?key=` query
parameter documented in some places is NOT accepted by this API and
returns 401 -- see docs/api-reference.md.

Our token is on the Classic package, so only the /classic/ endpoints are
available; /state/ and /orderflow/ return 403.

Stdlib only, no dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

BASE_URL = "https://api.gex.bot/v2"
TOKEN_ENV_VAR = "GEX_BOT_API_TOKEN"

# Aggregation scopes accepted by /{ticker}/classic/{scope}
SCOPES = ("zero", "one", "full")

DEFAULT_TIMEOUT = 30


class GexBotError(RuntimeError):
    """Any non-success response from the GexBot API."""


class GexBotAuthError(GexBotError):
    """401 -- token missing, malformed, or not sent as a Bearer header."""


class GexBotTierError(GexBotError):
    """403 -- endpoint exists but is outside this token's subscription package."""


@dataclass(frozen=True)
class GexSnapshot:
    """One gamma-exposure snapshot for a single ticker and scope."""

    ticker: str
    scope: str
    timestamp: int
    spot: float
    zero_gamma: float
    major_pos_oi: float
    major_neg_oi: float
    major_pos_vol: float
    major_neg_vol: float
    sum_gex_oi: float
    sum_gex_vol: float
    delta_risk_reversal: float
    strikes: list
    raw: dict

    @property
    def call_wall(self) -> float:
        """Largest positive-gamma strike by OI -- resistance / pinning level."""
        return self.major_pos_oi

    @property
    def put_wall(self) -> float:
        """Largest negative-gamma strike by OI -- support / acceleration level."""
        return self.major_neg_oi

    def strike_rows(self) -> list[dict]:
        """Decode the packed strikes array into dicts."""
        return [
            {
                "strike": row[0],
                "gex_vol": row[1],
                "gex_oi": row[2],
                "priors": row[3] if len(row) > 3 else [],
            }
            for row in self.strikes
        ]


class GexBotClient:
    def __init__(self, token: str | None = None, base_url: str = BASE_URL,
                 timeout: int = DEFAULT_TIMEOUT):
        self.token = token or os.environ.get(TOKEN_ENV_VAR)
        if not self.token:
            raise GexBotAuthError(
                f"No API token. Set the {TOKEN_ENV_VAR} environment variable."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, authenticated: bool = True) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Accept": "application/json"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                raise GexBotAuthError(
                    f"401 Unauthorized for {path}. The token was rejected -- "
                    "check it is current and sent as an Authorization: Bearer header."
                ) from exc
            if exc.code == 403:
                raise GexBotTierError(
                    f"403 Forbidden for {path}. The endpoint exists but is "
                    "outside this token's package (ours is Classic)."
                ) from exc
            if exc.code == 404:
                raise GexBotError(
                    f"404 Not Found for {path}. Check the ticker is in /tickers "
                    f"and the scope is one of {SCOPES}."
                ) from exc
            raise GexBotError(f"HTTP {exc.code} for {path}") from exc
        except urllib.error.URLError as exc:
            raise GexBotError(f"Could not reach {self.base_url}: {exc.reason}") from exc

    def tickers(self) -> dict:
        """Supported symbols, grouped into stocks / indexes / futures.

        This endpoint is public and needs no token.
        """
        return self._get("/tickers", authenticated=False)

    def gex(self, ticker: str, scope: str = "zero") -> GexSnapshot:
        """Fetch a gamma snapshot.

        scope: "zero" (nearest expiry / 0DTE), "one" (next expiry),
               "full" (all expiries combined).
        """
        if scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}, got {scope!r}")
        data = self._get(f"/{ticker.lower()}/classic/{scope}")
        return GexSnapshot(
            ticker=data.get("ticker", ticker.upper()),
            scope=scope,
            timestamp=data["timestamp"],
            spot=data["spot"],
            zero_gamma=data["zero_gamma"],
            major_pos_oi=data["major_pos_oi"],
            major_neg_oi=data["major_neg_oi"],
            major_pos_vol=data["major_pos_vol"],
            major_neg_vol=data["major_neg_vol"],
            sum_gex_oi=data["sum_gex_oi"],
            sum_gex_vol=data["sum_gex_vol"],
            delta_risk_reversal=data["delta_risk_reversal"],
            strikes=data["strikes"],
            raw=data,
        )
