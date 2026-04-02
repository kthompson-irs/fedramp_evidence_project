from __future__ import annotations

import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from ..config import load_settings
from ..exporters.powerbi import PowerBIExporter
from ..exporters.sharepoint import SharePointExporter
from ..store import DashboardStore
from .orchestrator import run_collectors


store = DashboardStore()


def refresh_job() -> None:
    items, collectors = run_collectors()
    store.refresh(items, collectors)


def export_job() -> None:
    settings = load_settings()
    snapshot = store.snapshot()

    if settings.graph_tenant_id and settings.graph_client_id and settings.graph_client_secret and settings.sharepoint_site_id and settings.sharepoint_list_id:
        SharePointExporter(
            settings.graph_tenant_id,
            settings.graph_client_id,
            settings.graph_client_secret,
            settings.sharepoint_site_id,
            settings.sharepoint_list_id,
        ).export_items(snapshot.evidence)

    if settings.powerbi_tenant_id and settings.powerbi_client_id and settings.powerbi_client_secret and settings.powerbi_group_id and settings.powerbi_dataset_id:
        PowerBIExporter(
            settings.powerbi_tenant_id,
            settings.powerbi_client_id,
            settings.powerbi_client_secret,
            settings.powerbi_group_id,
            settings.powerbi_dataset_id,
        ).export_items(snapshot.evidence)


def main() -> None:
    settings = load_settings()
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_job, "interval", seconds=settings.collect_interval_seconds, id="collect")
    scheduler.add_job(export_job, "interval", seconds=settings.export_interval_seconds, id="export")
    scheduler.start()

    refresh_job()  # initial run

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
