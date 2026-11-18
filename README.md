## **Overview:**

**Dataspine-TEST-AUTOMATION-REPO** This comprehensive test automation framework leverages various open-source **Python** libraries for Web/UI testing.

## **First-Time Setup (Windows):**

Run these steps from the repository root after cloning the repository. Python 3.12 is used by the current Azure pipeline configuration; use a supported Python 3.8+ installation locally.

### 1. Clone and open the repository

```powershell
git clone <repository-url>
cd qa_dataspine_ui_test_automation
code .
```

### 2. Create and activate a virtual environment

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
where.exe python
```

The `where.exe python` result should include `<project>\.venv\Scripts\python.exe`. If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal and activate again.

### 3. Install dependencies and browsers

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
```

The browser command installs Chromium, Firefox, and WebKit. The Windows `--with-deps` option is not required here.

### 4. Configure VS Code test discovery

Install the Python, Pylance, Python Debugger, and Cucumber (Gherkin) Full Support extensions. Select `.venv\Scripts\python.exe` with **Python: Select Interpreter**. Pytest is configured from the repository root by `pytest.ini`; do not select `qa_automation` as the test root.

Verify discovery from the repository root:

```powershell
python -m pytest --collect-only -q
```

The current suite should collect the test modules under `qa_automation\tests\ui\step_definitions`.

### 5. Configure local test credentials

Set these variables for the current PowerShell session. Do not commit credentials or put them in source files:

```powershell
$env:envName = "TEST"
$env:WEBTEST_USERNAME = "<test-username>"
$env:WEBTEST_PASSWORD = "<test-password>"
```

`login_setup.py` also accepts the legacy names `webtestUser` and `webtestUserPassword`. `LOGIN_URL` is optional and defaults to `https://analytical-data-access.education.gov.uk/`.

Capture the authenticated browser state before running UI tests:

```powershell
python login_setup.py
```

This creates `auth_state\state.json`, which is local test data and must not be committed.

### 6. Run tests

```powershell
# All tests
python -m pytest

# One test module
python -m pytest qa_automation/tests/ui/step_definitions/test_ada_website.py

# A marker/tag
python -m pytest -m smoke
```

Select the browser with the `BROWSER` environment variable. The supported values are `chrome` (default), `firefox`, `safari` (WebKit), and `edge` (Microsoft Edge channel):

```powershell
$env:BROWSER = "firefox"
python -m pytest
```

To run headed or debug Playwright tests, set `$env:HEADLESS = "false"` or `$env:PWDEBUG = "1"` before running pytest.

### 7. Optional Allure reporting

The pytest configuration writes raw results to `allure-results` automatically. To create and open an HTML report, install Java and the Allure command-line tool, then run:

```powershell
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### 8. Optional parallel execution

`pytest-xdist` is already included in `requirements.txt`:

```powershell
python -m pytest -n auto
```

After the initial setup, a new session only needs to activate `.venv`, refresh dependencies if `requirements.txt` changes, recapture login state when necessary, and run `python -m pytest`.

## **Web/UI Testing:**

This is developed using **Pytest**, **Pytest-Playwright** with **Pytest-BDD**. **Pytest-Playwright** is a **Pytest** plugin for **Playwright** to write end-to-end tests for web apps with Playwright and pytest. **Playwright** supports all modern rendering engines including Chromium, WebKit, and Firefox. Test on Windows, Linux, and macOS, locally or on CI, headless or headed with native mobile emulation. The Playwright library can be used as a general purpose browser automation tool, providing a powerful set of APIs to automate web applications, for both **Sync** and **Async Python**.

## **Python Libraries**:

Here are the primary **Python** libraries utilized in the development of this framework:

- **Pytest:** [Pytest](https://docs.pytest.org/en/8.2.x/) is a Python testing framework that originated from the PyPy project. It can be used to write various types of software tests, including unit tests, integration tests, end-to-end tests, and functional tests. Its features include parametrized testing, fixtures, and assert re-writing.

- **Playwright:** The [Playwright](https://playwright.dev/python/docs/intro) library can be used as a general purpose browser automation tool, providing a powerful set of APIs to automate web applications, for both sync and async Python. Playwright supports all modern rendering engines including Chromium, WebKit, and Firefox. Test on Windows, Linux, and macOS, locally or on CI, headless or headed with native mobile emulation.

- **Pytest-Playwright:** Playwright recommends using the official [Playwright Pytest plugin](https://playwright.dev/python/docs/test-runners) to write end-to-end tests. It provides context isolation, running it on multiple browser configurations out of the box. [pytest-playwright](https://pypi.org/project/pytest-playwright/) is a Pytest plugin for Playwright. It is used to write end-to-end tests for web applications with Playwright and pytest.

- **Pytest-BDD:** [Pytest-BDD](https://pytest-bdd.readthedocs.io/en/8.1.0/) implements a subset of the Gherkin language to enable automating project requirements testing and to facilitate behavioral driven development. Unlike many other BDD tools, it does not require a separate runner and benefits from the power and flexibility of **Pytest**. It enables unifying unit and functional tests, reduces the burden of continuous integration server configuration and allows the reuse of test setups. **Pytest** fixtures written for unit tests can be reused for setup and actions mentioned in feature steps with dependency injection. This allows a true BDD just-enough specification of the requirements without maintaining any context object containing the side effects of Gherkin imperative declarations.

## **Key Features:**

- **Behavior Driven Development (BDD) Support:** The test scenarios are written in plain English text called Gherkin, making it easy for non-technical stakeholders to understand and contribute to the testing process.
- **UI, Mobile Browser and API Operations:** The framework includes a built-in library to operate on UI, Mobile Browser and API (REST API) levels, ensuring comprehensive testing capabilities.
- **Multi-Browser Support:** Supports the execution of tests across different browsers, including Chromium/Chrome, Firefox, and WebKit.
- **Parallel Execution:** Scenarios can be executed in parallel mode by default using the **Pytest-XDIST** Python library. The number of workers is determined by the value specified in the command line or configured in the environment variable at runtime, significantly reducing test execution time.
  The parallel execution is invoked automatically when we use Pytest with `--numprocesses or -n` option as part of **Pytest** CLI:
  - `pytest --numprocesses auto` or `pytest --numprocesses 2` or `pytest -n 2` or `pytest -n auto`
- **Run Specific Feature/Scenario:** Scenarios can be easily run using the specific `markers/tags` which are marked before the feature or scenarios and registered same marker as part of `pytest.ini`.
  - `PWDEBUG=1 pytest -m smoke` or `PWDEBUG=1 pytest -m ada_home`
- **Rerun of Failed Scenarios:** To re-run failure/flaky tests again, `pytest-rerunfailures` package help to re-run failed scenarios.
  - `pytest --reruns <no_of_reruns> -m ada_home`
  - Example, below is a sample re-run command to allow **Pytest** test runner to re-run failed scenarios 2 times.
    - `pytest -m ada_home --reruns 2 --alluredir allure-results`
  - Example, command to execute scenarios parallel and re-run failed:
    - `pytest -n <no_of_workers> --reruns <no_of_reruns> -m "tag_name or tag_name_2"`
- **Scenario Skipping:** Scenarios can be easily skipped by adding a `not` before the marker/tag so that pytest runner is autoamtially unselect those marked as `not ada_home` as part of the test execution.
- **Debugging and Dry Run:** Supports debugging and dry run of scenarios, which helps identify undefined and ambiguous steps or scenarios at the time of test execution. Also, it helps to detect and fix flaky tests. To debug tests, use `PWDEBUG=1` as part of **Pytest** CLI. This debugging is only enabled for UI tests and can be useful to navigate step by step to debug using the Playwright debug window.
  - `PWDEBUG=1 pytest` or `PWDEBUG=1 pytest -m smoke`
- **Capture Test Logs:** **capture_logs** fixture method allows us to capture test logs. The logs can be viewed in the Allure HTML report after execution of test run.
- **Allure HTML Report Generation:** Generates Allure HTML reports, providing a detailed and visually appealing representation of test results.
  - **Enhanced Metadata Support:** Allure reports now include comprehensive environment information, executor details (CI/CD build links), and intelligent test failure categorization.
  - **Automatic Generation:** Metadata (environment.properties, executor.json, categories.json) is automatically generated during test execution via `conftest.py` using the `qa_automation/utils/allure_metadata.py` module.
  - **Local & CI/CD Support:** Works seamlessly in both local development and Azure DevOps pipelines with auto-detection of environment.
  - See [pipelines/README-ALLURE-SETUP.md](pipelines/README-ALLURE-SETUP.md) for detailed Allure configuration and metadata customization. - *Pending*
- **Environment Variable Control:** Please refer to the 3.1 and 3.2 sections for more detail, how to set up and run scenarios on local machine and Azure pipeline.

## **Supported Browsers for UI tests:**

1. **Chromium:** The default browser for testing and can be used to run tests on Edge browser by setting up `BROWSER` environment variable as `Edge`.
2. **Firefox:** Supports testing on the Firefox browser. To run tests in `Firefox` broweser, please set `BROWSER` environment variable as `Firefox`.
3. **WebKit:** The web browser engine used by Safari, ensuring compatibility with Safari. To run tests in `Webkit` broweser, please set `BROWSER` environment variable as `Webkit`.

## **Configure Azure Repos and Git Authentication:**

Follow the below links for step by step guide to Git Authentication or clone the Azure Repos.

- [Azure Repos](https://learn.microsoft.com/en-gb/azure/devops/repos/get-started/what-is-repos?view=azure-devops)
- [Git Authentication](https://learn.microsoft.com/en-gb/azure/devops/repos/git/auth-overview?view=azure-devops&tabs=Windows)

## **Configure IDE:**

The [**Visual Studio Code**](https://code.visualstudio.com/) known as VS Code is used as default IDE for this framework development. Hence, once the VS Code is installed, click **Ctrl + Shift + P** button to select the default **Python Interpreter ** for the workspace or framework. Follow the steps to select or configure appropriate version of Python Interpreter for the workspace.

Also, install the below useful VS Code extensions to work as part of this framwork development.

- Python
- Pylance
- Python Debugger
- Pytest BDD
- pytest-fixtures
- Cucumber (Gherkin) Full Support - It is useful to format Feature files but can not directly navigate to corresponding step definitions
- Playwright - It allows us to use record and playback option from VS Code Testing tab
- Allure Support
- Prettier - Code Formater for JSON and other supporting launguages format
- Black Formater for Python language/script format
- Pytest IntelliSense - Optional
- GitLens - Optional but it helps to keep track of Git changes
- Live Server - Optional but it can be used to view Allure HTML reports locally

## **Pytest Configuration File:**

The **pytest.ini** is a Pytest configuration file and it can be used to pre-configure with some of the **Pytest** configurations to allow pytest test runner to use at runtime. This is an optional file but would give an option for better maintainance to use pre-configured **pytest.ini** file. This file can be used to set options to locate tests, BDD features, define markers, default format of results and results folder path etc.

## **Install Python:**

To use this framework, you’ll need **Python** version 3.8 or higher, along with the package manager **pip**.

To avoid conflicts when installing **Python** packages on your local machine, use a **Python** virtual environment. Configure your IDE to use this `.venv` as the default **Python** development environment. This way, you can install dependencies within your repository and run scenarios smoothly. Follow the link below to configure a virtual environment for **Python** development using **VS Code** or similar IDEs.

- [Python - Virtual Environment Set up](https://docs.python.org/3/library/venv.html) or you can follow below steps to install the **Python** in a custom path and configure your IDE to allow you to install dependencies easily and run the scenarios.

- First, install the Python into the following custom path to allow us to install any packages without throwing user privileges issues. Here `ngella` is my local username so it should be different in your case.

  ```sh
  C:\Users\ngella\AppData\Roaming\Python
  ```

- Second, add below Python, Scripts and site-packages paths to User Environment Variables Path in Windows, save and close it.

  ```sh
  path = C:\Users\ngella\AppData\Roaming\Python\Python310\
  ```

  ```sh
  path = C:\Users\ngella\AppData\Roaming\Python\Python310\Scripts\
  ```

  ```sh
  path = C:\Users\ngella\AppData\Roaming\Python\Python310\Lib\site-packages\
  ```

- Third, open command prompt or terminal to run the below command to check if system is recognised Python installation.

  ```sh
  python --verson
  ```

- Finally, you should see, the installation version of python as an output. That means, python installtion is successful.

# **Install Dependencies and Run Features/Scenarios:**

#### 1. **Install Dependencies:**

To install all necessary dependencies, run the following command in the root directory of the project:

Use below command to install dependencies if you use bash as a terminal:

```sh
pip install -U -r ./requirements.txt
```

Use below command to install dependencies if you use Windows Commandline or Powershall as a terminal:

```sh
pip install -U -r .\requirements.txt
```

Verify the terminal or command line to ensure all dependencies are installed successfully by running below command:

```sh
pip list
```

### General Issues and Solutions:

We may encounter SSLError while installing the packages/libraries by default in `C:/Program Files/` path as a local user you won't have suffienct privellages to write in Program Files, hence below steps address those issues:

#### How to fix SSLError?

Error Message:

```
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1007)'))': /packages/4d/23/d145e541682e1535de873c790e5cf3f00d6c0487dfea226511e6e9b8f6d7/allure_pytest_bdd-2.13.5-py3-none-any.whl
```

Solution:

Below command to install dependencies if you use bash as a terminal:

```sh
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -U -r ./requirements.txt
```

Below command to install dependencies if you use Windows Commandline or Powershall as a terminal:

```sh
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -U -r .\requirements.txt
```

#### Install Playwright Browsers:

Below command to install Playwright browsers for the first time. Need to run the below command whenever we upgrade **Playwright** verison in order to support correct version of the browser engines.

```sh
playwright install --with-deps
```

#### **2. Test Scenarios and Step Definitions:**

- **Test Scenarios Organisation:** Test scenarios are organised into features and placed inside the `qa_automation/tests/ui/features` folder.
- **Step Definitions:** Step definitions connect Gherkin steps in feature files to programming code. These step definitions are placed inside the `qa_automation/tests/ui/step_definitions` folder.
- **Feature File Binding:** The feature file acts as a binding for all step definitions and features to run the tests scenario by scenario using **Pytest** as a test runner.

#### **3. Test Execution:**

To run test scenarios and generate allure reports by default, set up the environment variables in the Windows user environment variables. Below are essential environment variables for UI tests:


##### **3.1 UI Tests:**

Set the following environment variables (locally or via pipeline variables):

- `envName` (or `environmentName`)
- `webtestUser` (or `ada-web-user` in CI/CD)
- `webtestUserPassword` (or `ada-web-pwd` in CI/CD)


Before running the UI tests on local or Azure pipeline - run the below **Python** script to capture the user session to reuse the same session for each scenario execution.

```sh
python login_setup.py
```

##### **3.2 Run Tests Locally:**

To trigger the UI tests, use below command(s). Below commands run only corresponding tests marked with markers/tags: `@ada_home`.

```sh
pytest -m ada_home --alluredir allure-results
```

**Generate and View Allure Report:**

After running tests, generate and view the Allure report with enhanced metadata:

```sh
# Generate report
allure generate allure-results -o allure-report --clean

# View report (opens in browser)
allure open allure-report
```

Or use the combined command:

```sh
# Generate and serve report in one step
allure serve allure-results
```

**Allure Report Features:**
- **Environment Tab:** View detailed environment information (browser, OS, Python/Pytest versions, etc.)
- **Executor Info:** See build information with links to CI/CD builds (when run in Azure DevOps)
- **Categories:** Tests automatically categorized by failure type (infrastructure issues, timeouts, assertions, etc.)

**Manual Metadata Generation (Optional):**

If you need to regenerate or customize metadata files:

```sh
# Generate metadata with auto-detected environment
python -m qa_automation.utils.allure_metadata

# Generate for specific environment
python -m qa_automation.utils.allure_metadata --env-name TEST

# Force overwrite existing categories.json
python -m qa_automation.utils.allure_metadata --force
```

See [pipelines/README-ALLURE-SETUP.md](pipelines/README-ALLURE-SETUP.md) for complete Allure setup and customization details.

##### **3.3 Run Tests in Azure Pipeline:**

To execute test scenarios within the Azure pipeline, the pipeline template is set up to utilize test user credentials by retrieving **ADA-TEST** for the Dev and Test environment and **ADA-Prod** for the Production environment variable group data from the Azure pipeline libraries. Subsequently, the following command is executed. This command specifically targets scenarios that are marked with `@smoke` or `@regression`, allowing for selective test execution during pipeline execution by applying these markers/tags to scenario or feature names in the feature file:

```sh
pytest -m smoke --alluredir allure-results
```

```sh
pytest -m regression --alluredir allure-results
```

To skip some scenarios in any environment, add `not` before the marker (example: `ada_home`). **Pytest** test runner is autoamatically unselect those features/scenarios marked as `@ada_home` as part of the test execution.

```sh
pytest -m 'not ada_home' --alluredir allure-results
```

## **CI/CD Integration:**

This repository includes comprehensive Azure DevOps pipeline configurations for automated UI testing across different environments. The pipelines are designed to integrate seamlessly with web application deployment workflows.

### **Pipeline Architecture:**

The CI/CD pipelines are organized to support:

1. **Standalone Test Execution** - Run tests independently for any environment
2. **Post-Deployment Testing** - Integrate as stages after web app deployment
3. **Environment-Specific Pipelines** - Separate configurations for DEV, TEST, and PROD

### **Available Pipelines:**

#### **Environment-Specific Test Pipelines:**

Located in the `pipelines/` directory:

- **`ui-tests-dev.yml`** - DEV environment UI tests
  - Default tag: `smoke`
  - Parallel workers: 4
  - Trigger: Manual (trigger: none)

- **`ui-tests-test.yml`** - TEST environment UI tests
  - Default tag: `smoke`
  - Parallel workers: 4
  - Trigger: Manual (trigger: none)

- **`ui-tests-prod.yml`** - PROD environment UI tests
  - Default tag: `smoke`
  - Parallel workers: 4
  - Trigger: Manual (trigger: none)

#### **Integration Example:**

- **`webapp-with-ui-tests.yml`** - Complete CI/CD pipeline example showing:
  - Web app deployment to DEV → UI tests in DEV
  - Web app deployment to TEST → UI tests in TEST
  - Web app deployment to PROD → UI tests in PROD
  - Configurable environment deployment via parameters

### **Using the Pipelines:**

#### **Option 1: Standalone Test Execution**

Create a pipeline in Azure DevOps pointing to one of the environment-specific YAML files:

1. Navigate to **Pipelines** → **New Pipeline**
2. Select **Azure Repos Git**
3. Choose this repository
4. Select **Existing Azure Pipelines YAML file**
5. Choose path: `/pipelines/ui-tests-dev.yml` (or test/prod)
6. Run with parameters:
   - **pytest_tag**: `smoke` | `regression` | `ada_home` | etc.
   - **parallel_workers**: Number of parallel test workers (default: 4)

#### **Option 2: Integrate with Web App Deployment**

In your web app repository pipeline, add a reference to this test repository:

```yaml
# In your web app azure-pipelines.yml
resources:
  repositories:
    - repository: ui-tests
      type: git
      name: YourProject/ada_test_repo
      ref: main

stages:
  - stage: Deploy_WebApp_DEV
    jobs:
      - job: DeployApp
        steps:
          # Your web app deployment steps
          - script: echo "Deploying web app..."

  # Add UI tests after deployment
  - stage: UI_Tests_DEV
    dependsOn: Deploy_WebApp_DEV
    condition: succeeded('Deploy_WebApp_DEV')
    variables:
      - template: pipelines/variables/dev-env-variables.yml@ui-tests
    jobs:
      - template: pipelines/templates/ui-test-steps.yml@ui-tests
        parameters:
          jobName: "UI_Tests_After_Deployment"
          jobDisplayName: "Post-Deployment UI Tests"
          envName: "Dev"
          pytest_tag: "smoke"
          parallelWorkers: 4
          pythonVersion: "3.12"
          serviceConnection: $(ServiceConnection)
          keyVaultName: $(KeyVaultName)
```

#### **Option 3: Use Complete Integration Example**

Use `webapp-with-ui-tests.yml` as a reference for a full CI/CD pipeline:

```yaml
# Run with parameters
parameters:
  - deployToDev: true
  - deployToTest: true
  - deployToProd: false
  - pytest_tag: "smoke"
```

### **Pipeline Configuration:**

#### **Azure DevOps Setup Requirements:**

1. **Service Connections** (Project Settings → Service connections):
   - `s101dev_sc` - DEV environment Azure subscription
   - `s101test_sc` - TEST environment Azure subscription
   - `s101prod_sc` - PROD environment Azure subscription

2. **Environments** (Pipelines → Environments):
   - `DEV` - Development environment
   - `Test` - Test environment
   - `PROD` - Production environment
   - Configure approvals and checks as needed

3. **Variable Groups** (Pipelines → Library):
   Create the following variable groups to manage environment-specific configurations:

   **`ADA-DEV`** - DEV environment variables:
   - `ServiceConnection`: `s101dev_sc`
   - `KeyVaultName`: `s101d01-kv-edap-01`
  - `envName`: `Dev`

   **`ADA-TEST`** - TEST environment variables:
   - `ServiceConnection`: `s101test_sc`
   - `KeyVaultName`: `s101t01-kv-edap-01`
  - `envName`: `Test`

   **`ADA-PROD`** - PROD environment variables:
   - `ServiceConnection`: `s101prod_sc`
   - `KeyVaultName`: `s101p01-kv-edap-01`
  - `envName`: `PROD`

   Link the appropriate variable group to each pipeline.

4. **Agent Pools** (Project Settings → Agent pools):
   - `Adapt` - Self-hosted agent pool with:
     - Python 3.12 or higher
     - Playwright browser dependencies
     - Internet access for package installation

5. **Key Vaults** (Azure Portal):
  Each environment needs a Key Vault with these secrets:
  - `ada-web-user` - Test user username
  - `ada-web-pwd` - Test user password

#### **Pipeline Parameters:**

**`pytest_tag`** - Specifies which tests to execute:

- `smoke` - Quick smoke tests (recommended for post-deployment)
- `regression` - Full regression test suite
- `ada_home` - Home page tests
- `analyse_data` - Analyse data feature tests
- `get_support` - Support page tests
- Custom tags from `pytest.ini`

**`parallel_workers`** - Number of parallel pytest-xdist workers:

- Default: 4
- Adjust based on agent capacity and test suite size
- Higher values = faster execution (if agent supports it)

### **Pipeline Execution Flow:**

Each pipeline executes the following steps:

1. **Checkout** - Clone test repository
2. **Key Vault** - Retrieve secrets from Azure Key Vault (including sensitive credentials)
3. **Python Setup** - Install Python 3.12
4. **Dependencies** - Install packages from requirements.txt
5. **Playwright** - Install browser engines (Chromium, Firefox, WebKit)
6. **Authentication** - Run login_setup.py to capture session
7. **Test Execution** - Run pytest with specified tags and workers
8. **Publish Results** - Upload test results and Allure reports
9. **Allure Report** - Generate and publish HTML report

### **Secure Handling of Username and Password in Azure Classic Release Pipeline**

To securely set and use sensitive values like usernames and passwords in an Azure Classic Release Pipeline:

1. **Use Pipeline Variables as Secrets:**

- Go to the pipeline's **Variables** tab.
- Add variables for your username and password.
- For the password, enable the **Keep this value secret** option (padlock icon).
- Reference these variables in scripts or tasks as `$(ada-web-user)` and `$(ada-web-pwd)`.
- Secret variables are masked in logs and not exposed to users or scripts.

2. **(Recommended) Use Azure Key Vault:**

- Store credentials in Azure Key Vault as secrets.
- Link the Key Vault to your pipeline (via Variable Groups or Key Vault task).
- Reference secrets as pipeline variables (e.g., `$(ada-web-user)`, `$(ada-web-pwd)`).
- This approach centralizes secret management and enhances security.

**Never hardcode credentials in scripts or YAML files.**

For more details, see [Azure DevOps secrets documentation](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=classic#secret-variables) and [Azure Key Vault integration](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml#link-secrets-from-an-azure-key-vault-as-variables).

### **Test Reports in Azure DevOps:**

After pipeline execution, view results:

1. **Allure Report**:
   - Navigate to pipeline run → **Extensions** → **Allure Report**
   - Interactive HTML report with test details and logs

2. **Azure Test Results**:
   - Navigate to pipeline run → **Tests** tab
   - View pass/fail statistics and trends

3. **Published Artifacts**:
   - `auth_state_<ENV>` - Authentication session files
   - `allure-results_<ENV>` - Raw test results

### **Best Practices:**

1. **Post-Deployment Testing**:
   - Always run `smoke` tests after deployment
   - Use as a quality gate before promoting to next environment

2. **Scheduled Testing**:
   - Run `regression` tests on a schedule (nightly/weekly)
   - Don't run full regression on every deployment

3. **Environment Promotion**:
   - DEV → TEST → PROD progression
   - Require successful tests before promoting

4. **Parallel Execution**:
   - Use 4 workers for smoke tests
   - Use 6-8 workers for regression (if agent supports)

5. **Test Data Management**:
   - Use environment-specific test users
   - Clean up test data after execution

### **Troubleshooting CI/CD:**

**Issue**: Python/Pip installation fails

- **Solution**: Verify Python 3.12 is available on agent or install via UsePythonVersion task

**Issue**: Playwright browser installation fails

- **Solution**: Ensure agent has internet access or pre-install browsers on self-hosted agents

**Issue**: Key Vault access denied

- **Solution**: Verify service connection has "Get" and "List" permissions on Key Vault secrets

**Issue**: Tests fail to collect

- **Solution**: Check pytest.ini configuration and feature file paths

**Issue**: Authentication failures

- **Solution**: Verify Key Vault secrets are correct and login_setup.py executes successfully

For detailed CI/CD configuration, see `pipelines/README.md`.

#### **4. Report & Logs:**

##### **4.1 HTML Report - Locally:**

In order to generate or view allure HTML report locally, please install below two prerequisites:

- Install [allure](https://allurereport.org/docs/install-for-windows/) package in Windows or download [allure-2.32.2.zip](https://github.com/allure-framework/allure2/releases/tag/2.32.2) file and extract it to custom path and set the custom path in user environment variables to run allure executable to recognise and generate the report when invoke by running the **allure** command.
- **Java** is required in order to execute the **allure** package hence install the correct version of Java by following the [allure](https://allurereport.org/docs/install-for-windows/) installation steps for Windows.

We use [`allure-pytest-bdd`](https://pypi.org/project/allure-pytest-bdd/) plugin to generate allure-report. To invoke the `allure-pytest-bdd` plugin to capture the test results and logs, please pass `--alluredir allure-results`command as part of the test execution as shown above. The test report and logs are generated during the test execution is saved under `allure-results` and folder in the root directory and excecute the below command to generate the HTML report, that will be saved in a temp folder and automatically open in a default browser locally.

```sh
allure serve allure-results
```

##### **4.2 Logs - Locally:**

The logs will be present inside the `allure-results` folder in the root directory. The screenshots and video clips generated during the execution will be present under `test_results` folder in the root directory.

```sh
allure-results
```

##### **4.3 HTML Report - Azure Pipeline:**

The HTML report will be present inside the `allure-report` folder in the root directory. Need to configure your workspace with [Allure Report plugin page](https://allurereport.org/docs/integrations-azure/) to allow generate allure HTML report in azure pipeline and can be viewed in the azure pipeline by clicking on the allure report tab.

##### **4.4 Logs - Azure Pipeline:**

The logs will be present inside the `allure-results` folder in the root directory.
