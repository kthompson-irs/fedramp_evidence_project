from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    github_token: str = os.getenv("GITHUB_TOKEN", "") 
    github_org: str = os.getenv("GITHUB_ORG", "") 
    github_repos: List[str] = None  # type: ignore[assignment]

    aws_region: str = os.getenv("AWS_REGION", "us-gov-west-1")
    aws_profile: str = os.getenv("AWS_PROFILE", "") 

    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "") 
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "") 
    azure_client_secret: str = os.getenv("AZURE_CLIENT_SECRET", "") 
    azure_subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "") 

    graph_tenant_id: str = os.getenv("GRAPH_TENANT_ID", "") 
    graph_client_id: str = os.getenv("GRAPH_CLIENT_ID", "") 
    graph_client_secret: str = os.getenv("GRAPH_CLIENT_SECRET", "") 
    sharepoint_site_id: str = os.getenv("SHAREPOINT_SITE_ID", "") 
    sharepoint_list_id: str = os.getenv("SHAREPOINT_LIST_ID", "") 

    powerbi_tenant_id: str = os.getenv("POWERBI_TENANT_ID", "") 
    powerbi_client_id: str = os.getenv("POWERBI_CLIENT_ID", "") 
    powerbi_client_secret: str = os.getenv("POWERBI_CLIENT_SECRET", "") 
    powerbi_group_id: str = os.getenv("POWERBI_GROUP_ID", "") 
    powerbi_dataset_id: str = os.getenv("POWERBI_DATASET_ID", "") 

    collect_interval_seconds: int = int(os.getenv("COLLECT_INTERVAL_SECONDS", "3600"))
    export_interval_seconds: int = int(os.getenv("EXPORT_INTERVAL_SECONDS", "3600"))

    def __post_init__(self):
        object.__setattr__(self, "github_repos", _split_csv(os.getenv("GITHUB_REPOS", "")))


def load_settings() -> Settings:
    return Settings()
