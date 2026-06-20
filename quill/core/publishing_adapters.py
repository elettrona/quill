"""Trusted first-party publishing provider adapter contract.

Bundled adapters are imported explicitly by Quill. This module does not scan
packages, load third-party code, persist secrets, or perform network requests.
It only pairs reviewed provider metadata with its in-process client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quill.core.publishing_clients import PublishingProviderClient
    from quill.core.publishing_providers import PublishingProviderDefinition

HOST_OWNED_SECRET_ACCESS = "host_owned"
IN_PROCESS_EXECUTION = "in_process"


@dataclass(frozen=True, slots=True)
class BundledPublishingProviderAdapter:
    """A reviewed, package-facing contribution from a bundled provider."""

    provider_id: str
    definition: PublishingProviderDefinition
    client: PublishingProviderClient
    network_capability_rationale: str
    secret_access: str = HOST_OWNED_SECRET_ACCESS
    execution: str = IN_PROCESS_EXECUTION


_BUNDLED_PUBLISHING_PROVIDER_ADAPTERS: dict[str, BundledPublishingProviderAdapter] = {}


def register_bundled_publishing_provider(
    adapter: BundledPublishingProviderAdapter,
) -> None:
    """Register one trusted bundled adapter through the existing registries."""
    normalized = adapter.provider_id.strip().lower()
    definition_id = adapter.definition.id.strip().lower()
    client_id = adapter.client.provider_id.strip().lower()
    if not normalized:
        raise ValueError("Bundled publishing provider id is required.")
    if definition_id != normalized:
        raise ValueError("Bundled publishing provider definition id must match adapter id.")
    if client_id != normalized:
        raise ValueError("Bundled publishing provider client id must match adapter id.")
    if not adapter.network_capability_rationale.strip():
        raise ValueError("Bundled publishing provider network capability rationale is required.")
    if adapter.secret_access != HOST_OWNED_SECRET_ACCESS:
        raise ValueError("Bundled publishing provider secrets must remain host-owned.")
    if adapter.execution != IN_PROCESS_EXECUTION:
        raise ValueError("Only trusted in-process bundled publishing providers are supported.")

    from quill.core.publishing_clients import register_publishing_provider_client
    from quill.core.publishing_providers import register_publishing_provider

    register_publishing_provider(adapter.definition)
    register_publishing_provider_client(adapter.client)
    _BUNDLED_PUBLISHING_PROVIDER_ADAPTERS[normalized] = adapter


def bundled_publishing_provider_adapters() -> tuple[BundledPublishingProviderAdapter, ...]:
    """Return explicitly registered first-party adapters in registration order."""
    return tuple(_BUNDLED_PUBLISHING_PROVIDER_ADAPTERS.values())


def bundled_publishing_provider_adapter(
    provider_id: str,
) -> BundledPublishingProviderAdapter | None:
    return _BUNDLED_PUBLISHING_PROVIDER_ADAPTERS.get(provider_id.strip().lower())
