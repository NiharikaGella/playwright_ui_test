param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $PytestArgs = @(
        "qa_automation/tests/ui/step_definitions/amazon_steps.py",
        "-s"
    )
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
if ($IsWindows) {
    $python = Join-Path $root ".venv\Scripts\python.exe"
}
else {
    $python = Join-Path $root ".venv/bin/python"
}
$allureResults = Join-Path $root "allure-results"
$allureHistory = Join-Path $root "allure-report-history"
$allureReport = Join-Path $root "allure-report"

# Keep only the structured reports folder; remove transient root-level outputs after use.
Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue

& $python -m pytest @PytestArgs --alluredir=$allureResults
$pytestExitCode = $LASTEXITCODE

& $python -m qa_automation.utils.report_manager --restore-history --report-dir $allureResults --reports-dir (Join-Path $root "reports")
if ($LASTEXITCODE -ne 0) {
    Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue
    exit $LASTEXITCODE
}

allure generate $allureResults -o $allureHistory --clean
if ($LASTEXITCODE -ne 0) {
    Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue
    exit $LASTEXITCODE
}

& $python -m qa_automation.utils.report_manager --save-history --report-dir $allureHistory --reports-dir (Join-Path $root "reports")
if ($LASTEXITCODE -ne 0) {
    Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue
    exit $LASTEXITCODE
}

allure generate $allureResults -o $allureReport --clean --single-file
if ($LASTEXITCODE -ne 0) {
    Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue
    exit $LASTEXITCODE
}

& $python -m qa_automation.utils.report_manager --report-dir $allureReport --reports-dir (Join-Path $root "reports")
if ($LASTEXITCODE -ne 0) {
    Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue
    exit $LASTEXITCODE
}

# Clean transient Allure output but keep structured archived reports under reports/
Remove-Item $allureResults, $allureHistory, $allureReport -Recurse -Force -ErrorAction SilentlyContinue

if ($pytestExitCode -ne 0) {
    exit $pytestExitCode
}

exit 0
