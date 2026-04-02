 from __future__ import annotations
  2 
  3 from typing import Any, Dict, List
  4 
  5 import requests
  6 from msal import ConfidentialClientApplication
  7 
  8 from ..models import EvidenceItem
  9 
 10 
 11 class PowerBIExporter:
 12     def __init__(self, tenant_id: str, client_id: str, client_secret: str, group_id: str, dataset_id: str):
 13         self.group_id = group_id
 14         self.dataset_id = dataset_id
 15         self.app = ConfidentialClientApplication(
 16             client_id=client_id,
 17             authority=f"https://login.microsoftonline.com/{tenant_id}",
 18             client_credential=client_secret,
 19         )
 20 
 21     def _token(self) -> str:
 22         result = self.app.acquire_token_for_client(scopes=["https://analysis.windows.net/powerbi/api/.default"])
 23         if "access_token" not in result:
 24             raise RuntimeError(f"Power BI token error: {result}")
 25         return result["access_token"]
 26 
 27     def export_items(self, items: List[EvidenceItem]) -> Dict[str, Any]:
 28         headers = {"Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"}
 29         rows = [
 30             {
 31                 "control_id": item.control_id,
 32                 "control_family": item.control_family,
 33                 "source": item.source,
 34                 "artifact_type": item.artifact_type,
 35                 "artifact_name": item.artifact_name,
 36                 "timestamp_utc": item.timestamp_utc,
 37                 "status": item.status.value,
 38                 "owner": item.owner or "",
 39                 "evidence_uri": item.evidence_uri or "",
 40             }
 41             for item in items
 42         ]
 43         url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.group_id}/datasets/{self.dataset_id}/tables/Evidence/rows"
 44         resp = requests.post(url, headers=headers, json={"rows": rows}, timeout=30)
 45         resp.raise_for_status()
 46         return resp.json()
