# Allure Report Management

The local `run-tests-and-manage-report.ps1` workflow calls `qa_automation.utils.report_manager` after generating an Allure report. The Azure YAML pipeline publishes Allure results and reports directly; it does not invoke the report manager.

## Layout

```text
reports/
├── latest/
└── archive/
    ├── 20260915-132847-102505/
    └── ...
```

`reports/latest` is replaced on every successful execution. Each execution also creates a unique archive directory.

## Retention

The default archive retention is 30 reports. Override it with:

```powershell
$env:ALLURE_REPORT_RETENTION = "10"
```

The report manager reads `ALLURE_REPORT_RETENTION` and removes older archive directories during report management.

## Local use

After the existing Allure command completes, manage the generated report with:

```powershell
.\.venv\Scripts\python.exe -m qa_automation.utils.report_manager --report-dir allure-report --reports-dir reports
```

Or provide retention explicitly:

```powershell
.\.venv\Scripts\python.exe -m qa_automation.utils.report_manager --report-dir allure-report --reports-dir reports --retention 10
```

The manager requires `allure-report/index.html` and does not change test execution or Allure report generation.
