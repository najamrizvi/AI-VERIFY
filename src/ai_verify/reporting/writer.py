import json
from pathlib import Path

from ai_verify.reporting.report import VerificationReport
from ai_verify.reporting.serialization import serialize_report


class ReportWriter:
    """Write a verification report as JSON and Markdown files."""

    def write_json(
        self,
        report: VerificationReport,
        output_directory: Path | str,
    ) -> Path:
        directory = Path(output_directory)
        directory.mkdir(parents=True, exist_ok=True)

        output_path = directory / f"{report.run_id}.json"
        payload = serialize_report(report)

        output_path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return output_path

    def write_markdown(
        self,
        report: VerificationReport,
        output_directory: Path | str,
    ) -> Path:
        directory = Path(output_directory)
        directory.mkdir(parents=True, exist_ok=True)

        output_path = directory / f"{report.run_id}.md"

        content = self._build_markdown(report)

        output_path.write_text(
            content,
            encoding="utf-8",
        )

        return output_path

    def write(
        self,
        report: VerificationReport,
        output_directory: Path | str,
    ) -> tuple[Path, Path]:
        json_path = self.write_json(
            report,
            output_directory,
        )

        markdown_path = self.write_markdown(
            report,
            output_directory,
        )

        return json_path, markdown_path

    @staticmethod
    def _build_markdown(
        report: VerificationReport,
    ) -> str:
        lines = [
            "# AI-VERIFY Verification Report",
            "",
            "## Verification Result",
            "",
            f"- **Status:** {report.status}",
            f"- **Decision Rule:** {report.decision_rule}",
            f"- **Rationale:** {report.rationale}",
            "",
            "## Run",
            "",
            f"- **Run ID:** {report.run_id}",
            "",
            "## Requirement",
            "",
            report.requirement,
            "",
            "## Invariant",
            "",
            report.invariant,
            "",
            "## Verification Scope",
            "",
            "```json",
            json.dumps(
                report.scope,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Verification Plan",
            "",
            "```json",
            json.dumps(
                report.verification_plan,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Evidence",
            "",
        ]

        if report.evidence:
            for item in report.evidence:
                lines.extend(
                    [
                        f"### {item['evidence_id']}",
                        "",
                        f"- **Status:** {item['status']}",
                        f"- **Type:** {item['evidence_type']}",
                        f"- **Description:** {item['description']}",
                        f"- **Source:** {item['source']}",
                        f"- **Observation:** {item['observation']}",
                        f"- **Execution ID:** {item['execution_id']}",
                        "",
                    ]
                )
        else:
            lines.extend(
                [
                    "No evidence was collected.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Provenance",
                "",
                "```json",
                json.dumps(
                    report.provenance,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                "```",
                "",
            ]
        )

        return "\n".join(lines)


__all__ = ["ReportWriter"]
