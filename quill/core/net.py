from __future__ import annotations

import ssl

__all__ = ["verified_ssl_context"]


def verified_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that always verifies certificates.

    Certificate verification and hostname checking are required for every
    outbound HTTPS request in Quill: AI provider calls, update checks, and
    optional downloads. Python on macOS ships without trusted roots wired into
    ``urllib`` (which otherwise raises ``CERTIFICATE_VERIFY_FAILED``), so prefer
    certifi's CA bundle and fall back to the system default. The context is
    never weakened: ``check_hostname`` and ``verify_mode`` stay at their secure
    defaults (``True`` and ``CERT_REQUIRED``).
    """
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001 - certifi is optional; system roots suffice
        context = ssl.create_default_context()
    # Defensive: guarantee verification even if a future default changes.
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context
