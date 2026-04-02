# Architecture

- `app/collectors/` pulls evidence from GitHub, AWS, and Azure.
- `app/exporters/` pushes normalized evidence to SharePoint and Power BI. 
- `app/services/scheduler.py` runs periodic collection/export jobs.
- `app/main.py` exposes a simple API for the dashboard.
