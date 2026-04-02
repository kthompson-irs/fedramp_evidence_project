from __future__ import annotations

from typing import List, Tuple

from ..collectors.aws import AWSCollector
from ..collectors.azure import AzureCollector
from ..collectors.github import GitHubCollector
from ..config import load_settings
from ..models import CollectorHealth, EvidenceItem
from ..utils import utc_now


def run_collectors() -> Tuple[List[EvidenceItem], List[CollectorHealth]]:
    settings = load_settings()
    items: List[EvidenceItem] = []
    health: List[CollectorHealth] = []

    if settings.github_token and settings.github_org:
        try:
            gh = GitHubCollector(settings.github_token, settings.github_org, settings.github_repos)
            gh_items = gh.collect()
            items.extend(gh_items)
            health.append(gh.health(True, f"Collected {len(gh_items)} items"))
        except Exception as exc:  # noqa: BLE001
            health.append(CollectorHealth(source="GitHubCollector", healthy=False, last_run_utc=utc_now(), message=str(exc)))
    else:
        health.append(CollectorHealth(source="GitHubCollector", healthy=False, last_run_utc=utc_now(), message="Missing GitHub settings"))

    try:
        aws = AWSCollector(settings.aws_region, settings.aws_profile or None)
        aws_items = aws.collect()
        items.extend(aws_items)
        health.append(aws.health(True, f"Collected {len(aws_items)} items"))
    except Exception as exc:  # noqa: BLE001
        health.append(CollectorHealth(source="AWSCollector", healthy=False, last_run_utc=utc_now(), message=str(exc)))

    if settings.azure_tenant_id and settings.azure_client_id and settings.azure_client_secret and settings.azure_subscription_id:
        try:
            az = AzureCollector(
                settings.azure_tenant_id,
                settings.azure_client_id,
                settings.azure_client_secret,
                settings.azure_subscription_id,
            )   
            az_items = az.collect()
            items.extend(az_items)
            health.append(az.health(True, f"Collected {len(az_items)} items"))
        except Exception as exc:  # noqa: BLE001
            health.append(CollectorHealth(source="AzureCollector", healthy=False, last_run_utc=utc_now(), message=str(exc)))
    else:
        health.append(CollectorHealth(source="AzureCollector", healthy=False, last_run_utc=utc_now(), message="Missing Azure settings"))

    return items, health
