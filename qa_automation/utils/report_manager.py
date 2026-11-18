"""Manage generated Allure report copies and archive retention."""

import argparse
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_RETENTION = 30


def _retention(value: str | None) -> int:
    raw_value = value or os.getenv("ALLURE_REPORT_RETENTION", str(DEFAULT_RETENTION))
    try:
        retention = int(raw_value)
    except ValueError as error:
        raise ValueError("ALLURE_REPORT_RETENTION must be a positive integer") from error
    if retention < 1:
        raise ValueError("ALLURE_REPORT_RETENTION must be a positive integer")
    return retention


def _archive_name() -> str:
    build_number = (
        os.getenv("BUILD_BUILDID")
        or os.getenv("RELEASE_RELEASEID")
        or os.getenv("BUILD_BUILDNUMBER")
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    return f"build-{build_number}-{timestamp}" if build_number else timestamp


def _replace_directory(source: Path, destination: Path) -> None:
    temporary_destination = destination.with_name(f".{destination.name}.tmp")
    shutil.rmtree(temporary_destination, ignore_errors=True)
    shutil.copytree(source, temporary_destination)
    shutil.rmtree(destination, ignore_errors=True)
    temporary_destination.replace(destination)


def _remove_old_archives(archive_directory: Path, retention: int) -> None:
    archives = sorted(
        (path for path in archive_directory.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for archive in archives[retention:]:
        shutil.rmtree(archive)


def restore_history(
    results_directory: str | Path = "allure-results",
    reports_directory: str | Path = "reports",
) -> bool:
    """Restore persisted Allure history before generating the next report."""
    source = Path(reports_directory).resolve() / "history"
    destination = Path(results_directory).resolve() / "history"
    if not source.is_dir():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(source, destination)
    return True


def save_history(
    report_directory: str | Path = "allure-report",
    reports_directory: str | Path = "reports",
) -> bool:
    """Persist generated Allure history for the next execution."""
    source = Path(report_directory).resolve() / "history"
    destination = Path(reports_directory).resolve() / "history"
    if not source.is_dir():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(source, destination)
    return True


def manage_report(
    report_directory: str | Path = "allure-report",
    reports_directory: str | Path = "reports",
    retention: int | None = None,
) -> tuple[Path, Path]:
    """Copy one generated report to latest and to a retained archive."""
    source = Path(report_directory).resolve()
    reports_root = Path(reports_directory).resolve()
    latest = reports_root / "latest"
    archive_directory = reports_root / "archive"

    if not source.is_dir() or not (source / "index.html").is_file():
        raise FileNotFoundError(
            f"Generated report was not found or has no index.html: {source}"
        )

    archive_directory.mkdir(parents=True, exist_ok=True)
    latest.parent.mkdir(parents=True, exist_ok=True)
    archive = archive_directory / _archive_name()
    _replace_directory(source, latest)
    _replace_directory(source, archive)
    _remove_old_archives(archive_directory, _retention(str(retention) if retention is not None else None))
    return latest, archive


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage generated Allure reports")
    parser.add_argument("--report-dir", default="allure-report")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--retention", type=int, default=None)
    parser.add_argument("--restore-history", action="store_true")
    parser.add_argument("--save-history", action="store_true")
    args = parser.parse_args()

    if args.restore_history:
        print(f"Allure history restored: {restore_history(args.report_dir, args.reports_dir)}")
        return 0
    if args.save_history:
        print(f"Allure history saved: {save_history(args.report_dir, args.reports_dir)}")
        return 0

    latest, archive = manage_report(args.report_dir, args.reports_dir, args.retention)
    print(f"Latest report: {latest}")
    print(f"Archived report: {archive}")
    print(f"Archive retention: {_retention(str(args.retention) if args.retention is not None else None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
