from __future__ import annotations

from typing import Any, List, Optional

import requests

from ..models import EvidenceItem, EvidenceStatus
from ..utils import utc_now
from .base import BaseCollector


class GitHubCollector(BaseCollector):
    def __init__(self, token: str, org: str, repos: Optional[List[str]] = None):
        self.token = token
        self.org = org 
        self.repos = repos or []
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update(
            {   
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }   
        )   

    def _get_json(self, url: str) -> Any:
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _repo_targets(self) -> List[str]:
        if self.repos:
            return self.repos
        repos = self._get_json(f"{self.base_url}/orgs/{self.org}/repos?per_page=100")
        return [r["name"] for r in repos]

    def collect(self) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        for repo in self._repo_targets():
            items.extend(self._collect_repo(repo))
        return items

    def _collect_repo(self, repo: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        code_alerts = self._get_json(f"{self.base_url}/repos/{self.org}/{repo}/code-scanning/alerts?per_page=100")
        items.append(
            EvidenceItem(
                control_id="SI-03",
                control_family="SI",
                source="GitHub",
                artifact_type="code_scanning_alerts",
                artifact_name=f"{repo} code scanning alerts",
                timestamp_utc=utc_now(),
                evidence_uri=f"github://{self.org}/{repo}/code-scanning/alerts",
                details={"count": len(code_alerts), "sample": code_alerts[:3]},
            )           try:
            secret_alerts = self._get_json(f"{self.base_url}/repos/{self.org}/{repo}/secret-scanning/alerts?per_page=100")
            items.append(
                EvidenceItem(
                    control_id="SI-03",
                    control_family="SI", dep_alerts = self._get_json(f"{self.base_url}/repos/{self.org}/{repo}/dependabot/alerts?per_page=100")
        items.append(
            EvidenceItem(
                control_id="SI-03",
                control_family="SI",
                source="GitHub",
                artifact_type="dependabot_alerts",
                artifact_name=f"{repo} Dependabot alerts",            )   
        except requests.HTTPError as exc:
            items.append(
                EvidenceItem(
                    control_id="SI-03",
                    control_family="SI",
                    source="GitHub",
                    artifact_type="secret_scanning_alerts",
                    artifact_name=f"{repo} secret scanning alerts",
                    timestamp_utc=utc_now(),
                    status=EvidenceStatus.pending,
                    evidence_uri=f"github://{self.org}/{repo}/secret-scanning/alerts",
                    details={"error": str(exc), "note": "Secret scanning may be disabled for this repo."},
                )   
            )   
        dep_alerts = self._get_json(f"{self.base_url}/repos/{self.org}/{repo}/dependabot/alerts?per_page=100")
        items.append(
            EvidenceItem(
                control_id="SI-03",
                control_family="SI",
                source="GitHub",
                artifact_type="dependabot_alerts",
                artifact_name=f"{repo} Dependabot alerts",
                timestamp_utc=utc_now(),
                evidence_uri=f"github://{self.org}/{repo}/dependabot/alerts",
                details={"count": len(dep_alerts), "sample": dep_alerts[:3]},
            )   
        )   

        try:
            branch = self._get_json(f"{self.base_url}/repos/{self.org}/{repo}/branches/main/protection")
            items.append(
                EvidenceItem(
                    control_id="AC-3",
                    control_family="AC",
                    source="GitHub",
                    artifact_type="branch_protection",
                    artifact_name=f"{repo} branch protection",
                    timestamp_utc=utc_now(),
                    evidence_uri=f"github://{self.org}/{repo}/branches/main/protection",
                    details=branch,
                )   
            )   
        except requests.HTTPError as exc:
            items.append(
                EvidenceItem(
                    control_id="AC-3",
                    control_family="AC",
                    source="GitHub",
                    artifact_type="branch_protection",
                    artifact_name=f"{repo} branch protection",
                    timestamp_utc=utc_now(),
                    status=EvidenceStatus.pending,
                    evidence_uri=f"github://{self.org}/{repo}/branches/main/protection",
                    details={"error": str(exc)},
                )   
            )   

        return items
                timestamp_utc=utc_now(),
                evidence_uri=f"github://{self.org}/{repo}/dependabot/alerts",
                details={"count": len(dep_alerts), "sample": dep_alerts[:3]},
            )
        )
