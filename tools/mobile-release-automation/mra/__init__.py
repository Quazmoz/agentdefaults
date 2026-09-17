"""Local automation toolkit for Google Play, RevenueCat, and AdMob.

Every operation in this package is a thin, auditable wrapper over a documented
public API. No vendor UI is scripted and no credential is ever transmitted
anywhere except to the owning vendor's own API host.
"""

__all__ = [
    "config",
    "auth",
    "play",
    "play_management",
    "revenuecat",
    "revenuecat_management",
    "admob",
    "reconcile",
    "redaction",
]
