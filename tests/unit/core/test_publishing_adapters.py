from __future__ import annotations

import pytest

from quill.core import publishing_clients, publishing_validation
from quill.core.publishing_adapters import (
    HOST_OWNED_SECRET_ACCESS,
    IN_PROCESS_EXECUTION,
    BundledPublishingProviderAdapter,
    bundled_publishing_provider_adapter,
    register_bundled_publishing_provider,
)
from quill.core.publishing_bundled import bootstrap_bundled_publishing_providers
from quill.core.publishing_bundled.wordpress import wordpress_bundled_provider_adapter
from quill.core.publishing_providers import (
    AUTH_METHOD_APP_PASSWORD,
    PUBLISHING_OPERATION_VERIFY,
    PublishingProviderDefinition,
    publishing_provider_definition,
)


class _MismatchedClient:
    provider_id = "other"


def _definition(provider_id: str) -> PublishingProviderDefinition:
    return PublishingProviderDefinition(
        id=provider_id,
        name="Package CMS",
        help_text="Bundled adapter test provider.",
        default_content_format="html",
        supported_auth_methods=(AUTH_METHOD_APP_PASSWORD,),
        implemented_auth_methods=(AUTH_METHOD_APP_PASSWORD,),
        supported_content_kinds=("article",),
        implemented_content_kinds=("article",),
        supported_operations=(PUBLISHING_OPERATION_VERIFY,),
        implemented_operations=(PUBLISHING_OPERATION_VERIFY,),
        content_kind_labels={"article": "Article"},
        content_kind_plural_labels={"article": "Articles"},
    )


def test_wordpress_can_register_through_bundled_package_adapter() -> None:
    adapter = wordpress_bundled_provider_adapter()
    original_definition = publishing_provider_definition("wordpress")
    original_client = publishing_clients.publishing_provider_client("wordpress")

    register_bundled_publishing_provider(adapter)

    assert bundled_publishing_provider_adapter("wordpress") is adapter
    assert publishing_provider_definition("wordpress") is original_definition
    assert publishing_clients.publishing_provider_client("wordpress") is original_client
    assert adapter.secret_access == HOST_OWNED_SECRET_ACCESS
    assert adapter.execution == IN_PROCESS_EXECUTION
    assert adapter.network_capability_rationale
    assert publishing_validation.validate_registered_publishing_provider_clients() == ()


def test_normal_startup_bootstrap_preserves_wordpress_registry_identity() -> None:
    original_definition = publishing_provider_definition("wordpress")
    original_client = publishing_clients.publishing_provider_client("wordpress")

    bootstrap_bundled_publishing_providers()
    first_adapter = bundled_publishing_provider_adapter("wordpress")
    bootstrap_bundled_publishing_providers()
    second_adapter = bundled_publishing_provider_adapter("wordpress")

    assert first_adapter is not None
    assert second_adapter is not None
    assert second_adapter.definition is original_definition
    assert second_adapter.client is original_client
    assert publishing_provider_definition("wordpress") is original_definition
    assert publishing_clients.publishing_provider_client("wordpress") is original_client


def test_mismatched_adapter_is_rejected_before_registry_exposure() -> None:
    adapter = BundledPublishingProviderAdapter(
        provider_id="packagecms",
        definition=_definition("packagecms"),
        client=_MismatchedClient(),
        network_capability_rationale="User-initiated test requests.",
    )

    with pytest.raises(ValueError, match="client id must match"):
        register_bundled_publishing_provider(adapter)

    assert publishing_provider_definition("packagecms") is None
    assert publishing_clients.publishing_provider_client("packagecms") is None


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"network_capability_rationale": ""}, "rationale is required"),
        ({"secret_access": "provider_owned"}, "secrets must remain host-owned"),
        ({"execution": "cloud_function"}, "Only trusted in-process"),
        ({"execution": "worker"}, "Worker-boundary .* not implemented yet"),
    ],
)
def test_adapter_rejects_unsupported_security_or_runtime_shape(changes, message) -> None:
    values = {
        "provider_id": "packagecms",
        "definition": _definition("packagecms"),
        "client": type("PackageClient", (), {"provider_id": "packagecms"})(),
        "network_capability_rationale": "User-initiated test requests.",
    }
    values.update(changes)

    with pytest.raises(ValueError, match=message):
        register_bundled_publishing_provider(BundledPublishingProviderAdapter(**values))

    assert publishing_provider_definition("packagecms") is None
    assert publishing_clients.publishing_provider_client("packagecms") is None
