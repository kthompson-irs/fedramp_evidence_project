from __future__ import annotations

from typing import List, Optional

import boto3

from ..models import EvidenceItem
from ..utils import utc_now
from .base import BaseCollector


class AWSCollector(BaseCollector):
    def __init__(self, region: str, profile: Optional[str] = None):
        session_kwargs = {"region_name": region}
        if profile:
            session_kwargs["profile_name"] = profile
        self.session = boto3.Session(**session_kwargs)
        self.config = self.session.client("config")
        self.guardduty = self.session.client("guardduty")

    def collect(self) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        items.extend(self._collect_config())
        items.extend(self._collect_guardduty())
        return items

    def _collect_config(self) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        rules = self.config.describe_config_rules().get("ConfigRules", []) 
        for rule in rules:
            rule_name = rule.get("ConfigRuleName")
            if not rule_name:
                continue
            compliance = self.config.describe_compliance_by_config_rule(ConfigRuleNames=[rule_name])
            items.append(
                EvidenceItem(
                    control_id="CM-8",
                    control_family="CM",
                    source="AWS Config",
                    artifact_type="config_rule_compliance",
                    artifact_name=rule_name,
                    timestamp_utc=utc_now(),
                    evidence_uri=f"awsconfig://config-rule/{rule_name}",
                    details=compliance,
                )   
            )   
        return items

    def _collect_guardduty(self) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        detector_ids = self.guardduty.list_detectors().get("DetectorIds", []) 
        for detector_id in detector_ids:
            finding_ids = self.guardduty.list_findings(detectorId=detector_id).get("FindingIds", []) 
            findings = []
            if finding_ids:
                findings = self.guardduty.get_findings(detectorId=detector_id, findingIds=finding_ids[:50]).get("Findings", []) 
            items.append(
                EvidenceItem(
                    control_id="SI-03",
                    control_family="SI",
                    source="GuardDuty",
                    artifact_type="guardduty_findings",
                    artifact_name=f"Detector {detector_id}",
                    timestamp_utc=utc_now(),
                    evidence_uri=f"guardduty://detector/{detector_id}/findings",
                    details={"finding_count": len(finding_ids), "sample": findings[:3]},
                )   
            )   
        return items
