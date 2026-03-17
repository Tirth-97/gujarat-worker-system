# agent_orchestrator.py
# Master Orchestrator Agent
# Routes tasks to specialist agents, handles sequencing and error recovery
# JD requirement: "Agent orchestration (multi-step workflows, chained reasoning)"

from datetime import datetime


class WorkerRegistrationOrchestrator:
    """
    Orchestrates the complete worker registration pipeline.

    Each step delegates to a specialist agent:
      Step 1 → ai_agent.py        (Vision extraction)
      Step 2 → ai_agent.py        (Deterministic validation)
      Step 3 → ai_agent.py        (Confidence audit — AI audits AI)
      Step 4 → agent_compliance   (Legal compliance check)
      Step 5 → Orchestrator       (Decides final routing)

    app.py calls run_registration_pipeline() and receives
    a single aggregated result dict. No agent is called directly.
    """

    def __init__(self):
        self.pipeline_log = []   # Every step logged here
        self.start_time   = None

    def _log(self, step: int, agent: str, status: str, output: dict):
        """Internal: append a step to the pipeline log."""
        self.pipeline_log.append({
            "step":      step,
            "agent":     agent,
            "status":    status,
            "output":    output,
            "timestamp": datetime.now().isoformat(),
        })

    def run_registration_pipeline(
        self,
        image_bytes: bytes,
        language:    str = "Gujarati",
    ) -> dict:
        """
        Full registration pipeline: image → extracted data → checks
        → compliance → routing decision.

        Args:
            image_bytes: Raw Aadhaar card image bytes
            language:    Worker's preferred language

        Returns:
            {
              "final_status":  "AUTO_PROCEED" | "MANUAL_REVIEW" | "FLAG_FOR_REVIEW" | "EXTRACTION_FAILED",
              "aadhaar_data":  AadhaarData | None,
              "checks":        dict (deterministic risk),
              "audit":         dict (AI confidence scores),
              "compliance":    dict (legal check per law),
              "pipeline_log":  list (every step with timing),
              "routing_reason": str,
            }
        """
        from ai_agent import (
            extract_aadhaar_data,
            run_deterministic_checks,
            run_confidence_audit,
        )
        from agent_compliance import run_compliance_check

        self.pipeline_log = []
        self.start_time   = datetime.now()
        result = {
            "final_status":   "PENDING",
            "aadhaar_data":   None,
            "checks":         {},
            "audit":          {},
            "compliance":     {},
            "pipeline_log":   [],
            "routing_reason": "",
        }

        # ── Step 1: Document Agent — Vision extraction ──
        try:
            aadhaar_data, msg = extract_aadhaar_data(image_bytes)
            del image_bytes  # DPDP Act 2023
            self._log(1, "document_agent", "DONE", {"message": msg})

            if not aadhaar_data:
                self._log(1, "document_agent", "FAILED", {"error": msg})
                result["final_status"]   = "EXTRACTION_FAILED"
                result["routing_reason"] = f"Step 1 failed: {msg}"
                result["pipeline_log"]   = self.pipeline_log
                return result

            result["aadhaar_data"] = aadhaar_data

        except Exception as e:
            result["final_status"]   = "EXTRACTION_FAILED"
            result["routing_reason"] = f"Step 1 exception: {str(e)}"
            result["pipeline_log"]   = self.pipeline_log
            return result

        # ── Step 2: Verification Agent — Deterministic checks ──
        try:
            checks = run_deterministic_checks(aadhaar_data)
            self._log(2, "verification_agent", "DONE", checks)
            result["checks"] = checks
        except Exception as e:
            checks = {"risk_score": "Medium", "notes": f"Check error: {str(e)}",
                      "flags": [], "age": None}
            self._log(2, "verification_agent", "ERROR", {"error": str(e)})
            result["checks"] = checks

        # ── Step 3: Confidence Agent — AI audits AI ──
        try:
            audit = run_confidence_audit(aadhaar_data)
            self._log(3, "confidence_agent", "DONE", audit)
            result["audit"] = audit
        except Exception as e:
            audit = {"overall_score": 50, "recommendation": "MANUAL_REVIEW_REQUIRED",
                     "concerns": f"Audit error: {str(e)}", "field_scores": {}}
            self._log(3, "confidence_agent", "ERROR", {"error": str(e)})
            result["audit"] = audit

        # ── Step 4: Compliance Agent — Legal checks ──
        try:
            mock_worker = {
                "full_name":     aadhaar_data.full_name,
                "date_of_birth": aadhaar_data.date_of_birth,
                "consent_given": 1,
                "status":        "Pending",
            }
            compliance = run_compliance_check(mock_worker)
            self._log(4, "compliance_agent", "DONE", compliance)
            result["compliance"] = compliance
        except Exception as e:
            compliance = {"overall_clearance": "REVIEW",
                          "summary": f"Compliance check error: {str(e)}"}
            self._log(4, "compliance_agent", "ERROR", {"error": str(e)})
            result["compliance"] = compliance

        # ── Step 5: Orchestrator — Final routing decision ──
        final_status, reason = self._decide_routing(checks, audit, compliance)
        result["final_status"]   = final_status
        result["routing_reason"] = reason
        self._log(5, "orchestrator", "DONE",
                  {"decision": final_status, "reason": reason})

        result["pipeline_log"] = self.pipeline_log
        return result

    def _decide_routing(
        self,
        checks:     dict,
        audit:      dict,
        compliance: dict,
    ) -> tuple[str, str]:
        """
        Orchestrator decision logic.
        Combines outputs from all 3 agents into one routing decision.
        Returns: (final_status, reason_string)
        """
        risk_score    = checks.get("risk_score",         "Low")
        conf_score    = audit.get("overall_score",        50)
        ai_rec        = audit.get("recommendation",      "MANUAL_REVIEW_REQUIRED")
        clearance     = compliance.get("overall_clearance", "REVIEW")

        # BLOCK — child labour or major legal violation
        if risk_score == "High" or clearance == "BLOCK":
            return (
                "FLAG_FOR_REVIEW",
                f"Blocked: risk={risk_score}, clearance={clearance}. "
                "Officer must review before any approval."
            )

        # AUTO_PROCEED — all green
        if (conf_score >= 80
                and risk_score == "Low"
                and clearance == "CLEAR"
                and ai_rec == "AUTO_APPROVE"):
            return (
                "AUTO_PROCEED",
                f"All checks passed: confidence={conf_score}/100, "
                f"risk={risk_score}, clearance={clearance}. "
                "Routed to fast-track review."
            )

        # MANUAL_REVIEW — some uncertainty
        return (
            "MANUAL_REVIEW",
            f"Manual review required: confidence={conf_score}/100, "
            f"risk={risk_score}, clearance={clearance}, AI={ai_rec}."
        )


class LeaveRequestOrchestrator:
    """
    Orchestrates the leave logging pipeline.
    Generates notifications for both worker and employer.
    """

    def run_leave_pipeline(
        self,
        worker:           dict,
        leave_date:       str,
        reason:           str,
        notify_employer:  bool,
        language:         str = "Gujarati",
    ) -> dict:
        """
        Pipeline: log leave → notify worker → optionally notify employer.
        Returns: {"worker_msg": str, "employer_msg": str | None}
        """
        from agent_notify import notify_leave, notify_employer_leave

        worker_msg   = notify_leave(worker, leave_date, language)
        employer_msg = None

        if notify_employer and worker.get("employer_id"):
            employer_msg = notify_employer_leave(
                worker, leave_date, reason, language
            )

        return {
            "worker_msg":   worker_msg,
            "employer_msg": employer_msg,
        }


class ExtraHoursOrchestrator:
    """
    Orchestrates extra work hour requests.
    Parses natural language, checks Labour Code, generates notification.
    """

    def run_extra_hours_pipeline(
        self,
        natural_language: str,
        worker:           dict,
        employer:         dict,
        language:         str = "Gujarati",
    ) -> dict:
        """
        Pipeline: parse request → Labour Code check → notification.
        Returns: {"allowed": bool, "parsed": dict, "message": str, "notification": str}
        """
        from ai_agent    import parse_work_request
        from agent_notify import notify_extra_hours

        # Step 1: Parse natural language request
        parsed = parse_work_request(natural_language, worker.get("full_name", ""))

        if "error" in parsed:
            return {"allowed": False, "parsed": parsed,
                    "message": parsed["error"], "notification": ""}

        extra_hrs  = parsed.get("extra_hours", 1)
        req_date   = parsed.get("request_date", "")
        reason_str = parsed.get("reason", "Extra work")

        # Step 2: Labour Code 2020 check
        total_hours = 8 + extra_hrs
        if total_hours > 9:
            return {
                "allowed":      False,
                "parsed":       parsed,
                "message":      f"Labour Code 2020: total {total_hours}h exceeds 9h/day limit",
                "notification": "",
            }

        # Step 3: Generate notification
        notification = notify_extra_hours(
            worker,
            employer.get("business_name", "Employer"),
            extra_hrs,
            req_date,
            reason_str,
            language,
        )

        return {
            "allowed":      True,
            "parsed":       parsed,
            "message":      f"Request approved: {extra_hrs} extra hours on {req_date}",
            "notification": notification,
        }