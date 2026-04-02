from __future__ import annotations

from typing import List

import requests
from azure.identity import ClientSecretCredential

from ..models import EvidenceItem
from ..utils import utc_now
from .base import BaseCollector


class AzureCollector(BaseCollector):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    def _token(self) -> str:
        return self.credential.get_token("https://management.azure.com/.default").token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token()}",
            "Content-Type": "application/json",
        }   

    def collect(self) -> List[EvidenceItem]:
        return [*self._collect_policy_compliance(), *self._collect_defender_alerts()]

    def _collect_policy_compliance(self) -> List[EvidenceItem]:
        url = ( 
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/providers/Microsoft.PolicyInsights/policyStates/latest/summarize?api-version=2024-10-01"
        )   
        resp = requests.post(url, headers=self._headers(), json={}, timeout=30)
        resp.raise_for_status()
        return [
            EvidenceItem(
                control_id="CM-6",
                control_family="CM",
                source="Azure Policy",
                artifact_type="policy_compliance_summary",
                artifact_name=f"Subscription {self.subscription_id} policy compliance",
                timestamp_utc=utc_now(),
                evidence_uri=f"azurepolicy://subscriptions/{self.subscription_id}/policyStates/latest/summarize",
                details=resp.json(),
            )   
        ]   

    def _collect_defender_alerts(self) -> List[EvidenceItem]:
        url = ( 
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/providers/Microsoft.Security/alerts?api-version=2022-01-01"
        )   
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()            )
        ]
        data = resp.json()
        alerts = data.get("value", data)
        return [
            EvidenceItem(
                control_id="SI-03",
                control_family="SI",
                source="Defender for Cloud",
                artifact_type="security_alerts",
                artifact_name=f"Subscription {self.subscription_id} security alerts",
                timestamp_utc=utc_now(),
                evidence_uri=f"azuredefender://subscriptions/{self.subscription_id}/alerts",
                details={"count": len(alerts), "sample": alerts[:3]},
                  )
        ]
