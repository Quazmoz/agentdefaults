"""RevenueCat project and integration management beyond the core catalog client."""

from __future__ import annotations

from typing import Any

from . import redaction
from . import revenuecat as rc_module


class RevenueCatManagementClient:
    def __init__(self, client: rc_module.RevenueCatClient) -> None:
        self.client = client

    def create_project(self, name: str) -> dict:
        normalized = name.strip()
        if not normalized:
            raise rc_module.RevenueCatError("project name cannot be blank")
        return redaction.redact(
            self.client._request("POST", "/projects", f"create project {normalized}", json={"name": normalized})  # noqa: SLF001
        )

    def list_webhooks(self, project_id: str) -> list[dict]:
        return redaction.redact(
            list(
                self.client._paginate(  # noqa: SLF001
                    f"/projects/{project_id}/integrations/webhooks",
                    "list webhook integrations",
                )
            )
        )

    def get_webhook(self, project_id: str, webhook_id: str) -> dict:
        return redaction.redact(
            self.client._request(  # noqa: SLF001
                "GET",
                f"/projects/{project_id}/integrations/webhooks/{webhook_id}",
                f"get webhook integration {webhook_id}",
            )
        )

    def create_webhook(
        self,
        project_id: str,
        *,
        name: str,
        url: str,
        authorization_header: str | None = None,
        environment: str | None = None,
        event_types: list[str] | None = None,
        app_id: str | None = None,
    ) -> dict:
        body = self._webhook_body(
            name=name,
            url=url,
            authorization_header=authorization_header,
            environment=environment,
            event_types=event_types,
            app_id=app_id,
            partial=False,
        )
        response = self.client._request(  # noqa: SLF001
            "POST",
            f"/projects/{project_id}/integrations/webhooks",
            f"create webhook integration {name}",
            json=body,
        )
        return redaction.redact(response)

    def update_webhook(
        self,
        project_id: str,
        webhook_id: str,
        *,
        name: str | None = None,
        url: str | None = None,
        authorization_header: str | None = None,
        environment: str | None = None,
        event_types: list[str] | None = None,
        app_id: str | None = None,
        clear_authorization_header: bool = False,
        clear_environment: bool = False,
        clear_event_types: bool = False,
        clear_app_id: bool = False,
    ) -> dict:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name.strip()
        if url is not None:
            body["url"] = url.strip()
        if authorization_header is not None:
            body["authorization_header"] = authorization_header
        elif clear_authorization_header:
            body["authorization_header"] = None
        if environment is not None:
            self._validate_environment(environment)
            body["environment"] = environment
        elif clear_environment:
            body["environment"] = None
        if event_types is not None:
            body["event_types"] = event_types
        elif clear_event_types:
            body["event_types"] = None
        if app_id is not None:
            body["app_id"] = app_id
        elif clear_app_id:
            body["app_id"] = None
        if not body:
            raise rc_module.RevenueCatError("no webhook fields supplied for update")
        response = self.client._request(  # noqa: SLF001
            "POST",
            f"/projects/{project_id}/integrations/webhooks/{webhook_id}",
            f"update webhook integration {webhook_id}",
            json=body,
        )
        return redaction.redact(response)

    def delete_webhook(self, project_id: str, webhook_id: str) -> dict:
        return redaction.redact(
            self.client._request(  # noqa: SLF001
                "DELETE",
                f"/projects/{project_id}/integrations/webhooks/{webhook_id}",
                f"delete webhook integration {webhook_id}",
            )
        )

    @staticmethod
    def _validate_environment(environment: str | None) -> None:
        if environment not in (None, "production", "sandbox"):
            raise rc_module.RevenueCatError(
                "webhook environment must be 'production', 'sandbox', or null"
            )

    @classmethod
    def _webhook_body(
        cls,
        *,
        name: str,
        url: str,
        authorization_header: str | None,
        environment: str | None,
        event_types: list[str] | None,
        app_id: str | None,
        partial: bool,
    ) -> dict[str, Any]:
        normalized_name = name.strip()
        normalized_url = url.strip()
        if not partial and not normalized_name:
            raise rc_module.RevenueCatError("webhook name cannot be blank")
        if not partial and not normalized_url:
            raise rc_module.RevenueCatError("webhook URL cannot be blank")
        cls._validate_environment(environment)
        body: dict[str, Any] = {"name": normalized_name, "url": normalized_url}
        if authorization_header is not None:
            body["authorization_header"] = authorization_header
        if environment is not None:
            body["environment"] = environment
        if event_types is not None:
            body["event_types"] = event_types
        if app_id is not None:
            body["app_id"] = app_id
        return body
