# Allure Reporting

The Azure YAML pipeline is configured in `azure-pipelines.yml` and uses `pipelines/templates/ui-test-steps.yml`.

## Pipeline reports

Each environment/browser job runs pytest with Allure and JUnit output:

- `allure-results/` is published as a browser- and environment-specific pipeline artifact.
- JUnit results are published to Azure DevOps. `failTaskOnFailedTests: true` makes any failed test fail the job.
- `PublishAllureReport@2` publishes the Allure report for the job in the Azure DevOps run.

`conftest.py` generates `environment.properties`, `executor.json`, and `categories.json` at pytest session start when an Allure results directory is configured. The environment and browser values come from the pipeline parameters and matrix variables.

## Local reports

Run tests and generate Allure results from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -m smoke --alluredir allure-results
```

Generate and open a report with the Allure CLI installed:

```powershell
allure generate allure-results -o allure-report --clean
allure open allure-report
```

The metadata generator can also be invoked directly:

```powershell
.\.venv\Scripts\python.exe -m qa_automation.utils.allure_metadata --env-name Test --results-dir allure-results
```

Default failure categories are defined in `qa_automation/utils/allure_metadata.py`. To customize them for a run, edit `allure-results/categories.json` after generation or update the defaults in that module.

For local report archiving and history management, see [REPORT-MANAGEMENT.md](REPORT-MANAGEMENT.md).
