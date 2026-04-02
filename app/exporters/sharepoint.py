from __future__ import annotations

from typing import Any, Dict, List

import requests
from msal import ConfidentialClientApplication

from ..models import EvidenceItem


class SharePointExporter:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, site_id: str, list_id: str):
        self.site_id = site_id
        self.list_id = list_id
        self.app = ConfidentialClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret,
        )   

    def _token(self) -> str:
        result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in result:
            raise RuntimeError(f"SharePoint token error: {result}")
        return result["access_token"]

    def export_items(self, items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"}
        responses = []
        for item in items:
            payload = { 
                "fields": {
                    "Title": item.artifact_name,
                    "ControlId": item.control_id,
                    "ControlFamily": item.control_family,
                    "Source": item.source,
                    "ArtifactType": item.artifact_type,
                    "TimestampUtc": item.timestamp_utc,
                    "Status": item.status.value,
                    "Owner": item.owner or "", 
                    "EvidenceUri": item.evidence_uri or "", 
                }   
            }   
            url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items"
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            responses.append(resp.json())
        return responses
