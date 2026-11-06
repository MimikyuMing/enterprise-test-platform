import json
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CaseResultData:
    nodeid: str
    outcome: str
    duration: float
    message: str | None = None


@dataclass
class ExecutionResult:
    total: int
    passed: int
    failed: int
    duration_seconds: float
    output: str
    error: str | None = None
    case_results: list[CaseResultData] | None = None


class TestExecutor(ABC):
    @abstractmethod
    def execute(self, total_cases: int) -> ExecutionResult:
        ...


class SubprocessPytestExecutor(TestExecutor):
    def __init__(self, workdir: str, python: str, timeout: int = 300):
        self.workdir = workdir
        self.python = python
        self.timeout = timeout

    def execute(self, total_cases: int) -> ExecutionResult:
        report_dir = tempfile.mkdtemp(prefix="pytest-report-")
        report_file = os.path.join(report_dir, "report.json")
        try:
            cmd = [
                self.python,
                "-m",
                "pytest",
                "-q",
                "--json-report",
                f"--json-report-file={report_file}",
            ]
            proc = subprocess.run(
                cmd,
                cwd=self.workdir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            output = (proc.stdout or "") + (proc.stderr or "")

            if proc.returncode not in (0, 1):
                return ExecutionResult(
                    total=0,
                    passed=0,
                    failed=0,
                    duration_seconds=0.0,
                    output=output,
                    error=f"pytest exitcode={proc.returncode}",
                )

            if not os.path.exists(report_file):
                return ExecutionResult(
                    total=0,
                    passed=0,
                    failed=0,
                    duration_seconds=0.0,
                    output=output,
                    error="report file not generated",
                )

            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)

            summary = report.get("summary", {})
            case_results = _parse_case_results(report)
            return ExecutionResult(
                total=summary.get("total", 0),
                passed=summary.get("passed", 0),
                failed=summary.get("failed", 0) + summary.get("error", 0),
                duration_seconds=report.get("duration", 0.0),
                output=output,
                case_results=case_results,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                total=0,
                passed=0,
                failed=0,
                duration_seconds=float(self.timeout),
                output="",
                error=f"pytest timeout after {self.timeout}s",
            )
        finally:
            shutil.rmtree(report_dir, ignore_errors=True)


def get_executor() -> TestExecutor:
    return SubprocessPytestExecutor(
        workdir=os.getenv("PYTEST_WORKDIR"),
        python=os.getenv("PYTEST_PYTHON"),
        timeout=int(os.getenv("PYTEST_TIMEOUT", "300")),
    )


# 解析Report的JSON
def _extract_message(test: dict) -> str | None :
    for phase in ("call", "setup", "teardown"):
        phase_data = test.get(phase)
        if isinstance(phase_data, dict):
            longrepr = phase_data.get("longrepr")
            if longrepr:
                return str(longrepr)
    return None


def _parse_case_results(report: dict) -> list[CaseResultData]:
    results = []
    for test in report.get("tests", []):
        nodeid = test.get("nodeid","")
        if not nodeid:
            continue
        results.append(
            CaseResultData(
                nodeid=nodeid,
                outcome=test.get("outcome", "unknown"),
                duration=float(test.get("duration", 0.0)),
                message=_extract_message(test),
            )
        )
    return results