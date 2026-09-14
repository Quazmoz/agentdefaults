"""RevenueCat API v2 operations.

Reference: https://www.revenuecat.com/docs/api-v2

RevenueCat ships a first-party MCP server at https://mcp.revenuecat.ai/mcp, which
is the preferred agent surface. This module exists for the gaps: anything the MCP
server does not expose, and any step that must run unattended in a script.
"""

from __future__ import annotations

from typing import Any, Iterator
import json

import requests

from . import auth

BASE = "https://api.revenuecat.com/v2"
REQUEST_TIMEOUT_SECONDS = 60

PRODUCT_TYPES = (
    "subscription",
    "one_time",
    "consumable",
    "non_consumable",
    "non_renewing_subscription",
)
APP_TYPES = (
    "play_store",
    "app_store",
    "amazon",
    "mac_app_store",
    "stripe",
    "paddle",
    "roku",
    "rc_billing",
)


class RevenueCatError(RuntimeError):
    pass


class RevenueCatClient:
    def __init__(self, api_key: str | None = None, session=None) -> None:
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key or auth.revenuecat_key()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "mobile-release-automation/1.5",
            }
        )

    # ---- plumbing ----------------------------------------------------------

    def _request(self, method: str, path: str, action: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        response = self.session.request(method, f"{BASE}{path}", **kwargs)
        if not response.ok:
            try:
                detail = json.dumps(response.json(), indent=2)
            except ValueError:
                detail = response.text
            raise RevenueCatError(
                f"{action} failed with HTTP {response.status_code}:\n{detail}"
            )
        return response.json() if response.content else {}

    def _paginate(self, path: str, action: str) -> Iterator[dict]:
        starting_after = None
        while True:
            params = {"limit": 100}
            if starting_after:
                params["starting_after"] = starting_after
            payload = self._request("GET", path, action, params=params)
            items = payload.get("items", [])
            yield from items
            if not items or not payload.get("next_page"):
                return
            starting_after = items[-1]["id"]

    # ---- projects and apps -------------------------------------------------

    def list_projects(self) -> list[dict]:
        return list(self._paginate("/projects", "list projects"))

    def list_apps(self, project_id: str) -> list[dict]:
        return list(self._paginate(f"/projects/{project_id}/apps", "list apps"))

    def create_play_app(
        self, project_id: str, name: str, package_name: str, service_account_json: str
    ) -> dict:
        """Create a Play Store app in RevenueCat, wired to Play credentials.

        service_account_json is the entire contents of the Google Cloud service
        account key file, which RevenueCat uses for Play purchase validation.
        """
        body = {
            "name": name,
            "type": "play_store",
            "play_store": {
                "package_name": package_name,
                "play_service_account_credentials_json": service_account_json,
            },
        }
        return self._request(
            "POST", f"/projects/{project_id}/apps", f"create app {name}", json=body
        )

    # ---- products ----------------------------------------------------------

    def list_products(self, project_id: str) -> list[dict]:
        return list(self._paginate(f"/projects/{project_id}/products", "list products"))

    def create_product(
        self,
        project_id: str,
        app_id: str,
        store_identifier: str,
        product_type: str,
        display_name: str | None = None,
    ) -> dict:
        """Register an existing store product with RevenueCat.

        The product must already exist in Play; this records it, it does not
        create it in the store. Use create_product_in_store for that.
        """
        if product_type not in PRODUCT_TYPES:
            raise RevenueCatError(
                f"invalid product type {product_type!r}; expected one of {PRODUCT_TYPES}"
            )
        body: dict[str, Any] = {
            "store_identifier": store_identifier,
            "app_id": app_id,
            "type": product_type,
        }
        if display_name:
            body["display_name"] = display_name
        return self._request(
            "POST",
            f"/projects/{project_id}/products",
            f"create product {store_identifier}",
            json=body,
        )

    def create_product_in_store(self, project_id: str, product_id: str) -> dict:
        return self._request(
            "POST",
            f"/projects/{project_id}/products/{product_id}/create_in_store",
            f"create product {product_id} in store",
        )

    # ---- entitlements ------------------------------------------------------

    def list_entitlements(self, project_id: str) -> list[dict]:
        return list(
            self._paginate(f"/projects/{project_id}/entitlements", "list entitlements")
        )

    def list_entitlement_products(self, project_id: str, entitlement_id: str) -> list[dict]:
        """Read the product relationships for one entitlement."""
        return list(
            self._paginate(
                f"/projects/{project_id}/entitlements/{entitlement_id}/products",
                f"list products attached to entitlement {entitlement_id}",
            )
        )

    def create_entitlement(
        self, project_id: str, lookup_key: str, display_name: str
    ) -> dict:
        return self._request(
            "POST",
            f"/projects/{project_id}/entitlements",
            f"create entitlement {lookup_key}",
            json={"lookup_key": lookup_key, "display_name": display_name},
        )

    def attach_products_to_entitlement(
        self, project_id: str, entitlement_id: str, product_ids: list[str]
    ) -> dict:
        return self._request(
            "POST",
            f"/projects/{project_id}/entitlements/{entitlement_id}/actions/attach_products",
            f"attach products to entitlement {entitlement_id}",
            json={"product_ids": product_ids},
        )

    # ---- offerings and packages -------------------------------------------

    def list_offerings(self, project_id: str) -> list[dict]:
        return list(self._paginate(f"/projects/{project_id}/offerings", "list offerings"))

    def list_packages(self, project_id: str, offering_id: str) -> list[dict]:
        """Read all packages currently attached to one offering."""
        return list(
            self._paginate(
                f"/projects/{project_id}/offerings/{offering_id}/packages",
                f"list packages in offering {offering_id}",
            )
        )

    def list_package_products(self, project_id: str, package_id: str) -> list[dict]:
        """Read the product relationships for one package."""
        return list(
            self._paginate(
                f"/projects/{project_id}/packages/{package_id}/products",
                f"list products attached to package {package_id}",
            )
        )

    def inspect_wiring(self, project_id: str) -> dict[str, Any]:
        """Return RevenueCat offering/package and entitlement/product wiring.

        This intentionally favors explicit read-back over relying on creation responses.
        It is used by agents before and after high-risk attachment mutations.
        """
        offerings = []
        for offering in self.list_offerings(project_id):
            packages = []
            for package in self.list_packages(project_id, offering["id"]):
                packages.append(
                    {
                        **package,
                        "products": self.list_package_products(project_id, package["id"]),
                    }
                )
            offerings.append({**offering, "packages": packages})

        entitlements = []
        for entitlement in self.list_entitlements(project_id):
            entitlements.append(
                {
                    **entitlement,
                    "products": self.list_entitlement_products(project_id, entitlement["id"]),
                }
            )

        return {
            "project_id": project_id,
            "offerings": offerings,
            "entitlements": entitlements,
        }

    def create_offering(
        self,
        project_id: str,
        lookup_key: str,
        display_name: str,
        is_current: bool = False,
    ) -> dict:
        return self._request(
            "POST",
            f"/projects/{project_id}/offerings",
            f"create offering {lookup_key}",
            json={
                "lookup_key": lookup_key,
                "display_name": display_name,
                "is_current": is_current,
            },
        )

    def create_package(
        self,
        project_id: str,
        offering_id: str,
        lookup_key: str,
        display_name: str,
        position: int | None = None,
    ) -> dict:
        body: dict[str, Any] = {"lookup_key": lookup_key, "display_name": display_name}
        if position is not None:
            body["position"] = position
        return self._request(
            "POST",
            f"/projects/{project_id}/offerings/{offering_id}/packages",
            f"create package {lookup_key}",
            json=body,
        )

    def attach_products_to_package(
        self, project_id: str, package_id: str, products: list[dict]
    ) -> dict:
        """Attach products to a package.

        products is a list of {"product_id": ..., "eligibility_criteria": ...}.
        """
        return self._request(
            "POST",
            f"/projects/{project_id}/packages/{package_id}/actions/attach_products",
            f"attach products to package {package_id}",
            json={"products": products},
        )
