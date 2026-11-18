"""
Allure Report Metadata Utilities

This module provides utilities for generating Allure report metadata files:
- environment.properties: Test environment information
- executor.json: CI/CD executor information
- categories.json: Test failure categorization

Usage as a Module:
    from utils.allure_metadata import generate_allure_metadata
    
    # Generate metadata for default location
    generate_allure_metadata()
    
    # Generate metadata for custom location
    generate_allure_metadata("custom-results-dir")

Usage as a Standalone Script:
    # From project root directory
    python -m qa_automation.utils.allure_metadata
    
    # With custom options
    python -m qa_automation.utils.allure_metadata --env-name TEST --results-dir ./custom-results
    
    # Force overwrite categories.json
    python -m qa_automation.utils.allure_metadata --force

Note: When running pytest, metadata is automatically generated via conftest.py.
Use this script for manual metadata generation or when pytest is not available.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def generate_allure_metadata(results_dir="allure-results", force_categories=False):
    """
    Generate Allure metadata files:
    - environment.properties: Test environment information
    - executor.json: CI/CD executor information
    - categories.json: Test failure categorization
    
    Args:
        results_dir (str): Path to allure-results directory (default: "allure-results")
        force_categories (bool): Force overwrite of existing categories.json (default: False)
    
    Returns:
        None
    
    Raises:
        None - Errors are caught and logged as warnings
    """
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    # Helper function to get command version
    def get_version(command):
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or result.stderr.strip() or "N/A"
        except Exception:
            return "N/A"

    # Helper function to get Python package version
    def get_python_package_version(package_name):
        try:
            import importlib

            module = importlib.import_module(package_name)
            return getattr(module, "__version__", "N/A")
        except Exception:
            return "N/A"

    # 1. Generate environment.properties
    try:
        env_name = (
            os.environ.get("envName") 
            or os.environ.get("RELEASE_ENVIRONMENTNAME")
            or os.environ.get("BUILD_ENVIRONMENT") 
            or "Local"
        )
        browser = os.environ.get("BROWSER") or os.environ.get("browser") or "Chromium"
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Get pytest version from Python package (more reliable than CLI)
        pytest_version = get_python_package_version("pytest")

        # Get playwright version from Python package (more reliable than CLI)
        playwright_version = get_python_package_version("playwright")

        env_properties = [
            "# Test Environment Information",
            f"Environment={env_name}",
            f"Browser={browser}",
            f"OS={platform.system()} {platform.release()}",
            f"Architecture={platform.machine()}",
            f"Python.Version={python_version}",
            f"Pytest.Version={pytest_version}",
            f"Playwright.Version={playwright_version}",
            f"Agent.Name={os.environ.get('AGENT_NAME', platform.node())}",
            f"Build.Date={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Timezone={datetime.now().astimezone().tzname()}",
        ]

        # Add Azure DevOps specific variables if available
        if os.environ.get("RELEASE_RELEASEID"):
            # Azure Classic Release Pipeline
            env_properties.extend(
                [
                    f"Azure.ReleaseId={os.environ.get('RELEASE_RELEASEID')}",
                    f"Azure.ReleaseName={os.environ.get('RELEASE_RELEASENAME', 'N/A')}",
                    f"Azure.ReleaseDefinition={os.environ.get('RELEASE_DEFINITIONNAME', 'N/A')}",
                    f"Azure.Environment={os.environ.get('RELEASE_ENVIRONMENTNAME', 'N/A')}",
                ]
            )
        elif os.environ.get("BUILD_BUILDID"):
            # Azure Build Pipeline (YAML)
            env_properties.extend(
                [
                    f"Azure.BuildId={os.environ.get('BUILD_BUILDID')}",
                    f"Azure.BuildNumber={os.environ.get('BUILD_BUILDNUMBER', 'N/A')}",
                    f"Azure.BuildDefinition={os.environ.get('BUILD_DEFINITIONNAME', 'N/A')}",
                    f"Azure.Branch={os.environ.get('BUILD_SOURCEBRANCHNAME', 'N/A')}",
                ]
            )

        env_file = results_path / "environment.properties"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(env_properties))
        print(f"Generated Allure metadata: {env_file.name}")
    except Exception as e:
        print(f"Warning: Failed to generate environment.properties: {e}")

    # 2. Generate executor.json
    try:
        if os.environ.get("RELEASE_RELEASEID"):
            # Azure Classic Release Pipeline
            collection_uri = os.environ.get("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", "")
            team_project = os.environ.get("SYSTEM_TEAMPROJECT", "")
            release_id = os.environ.get("RELEASE_RELEASEID", "0")

            # Use direct release URL if available, otherwise construct it
            release_url = os.environ.get("RELEASE_RELEASEWEBURL")
            if not release_url:
                release_url = f"{collection_uri}{team_project}/_release?releaseId={release_id}&_a=release-summary"

            env_name = os.environ.get("RELEASE_ENVIRONMENTNAME", "Unknown")

            executor_data = {
                "name": "Azure Classic Release Pipeline",
                "type": "azure-release",
                "url": release_url,
                "buildOrder": int(release_id),
                "buildName": f"{os.environ.get('RELEASE_DEFINITIONNAME', 'Release Pipeline')} - {env_name}",
                "buildUrl": release_url,
                "reportUrl": "",
                "reportName": "Allure Report",
            }
        elif os.environ.get("BUILD_BUILDID"):
            # Azure Build Pipeline (YAML)
            collection_uri = os.environ.get("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", "")
            team_project = os.environ.get("SYSTEM_TEAMPROJECT", "")
            build_id = os.environ.get("BUILD_BUILDID", "0")
            build_url = (
                f"{collection_uri}{team_project}/_build/results?buildId={build_id}"
            )

            executor_data = {
                "name": "Azure DevOps Build Pipeline",
                "type": "azure-build",
                "url": build_url,
                "buildOrder": int(build_id),
                "buildName": os.environ.get("BUILD_DEFINITIONNAME", "Build Pipeline"),
                "buildUrl": build_url,
                "reportUrl": "",
                "reportName": "Allure Report",
            }
        else:
            # Local execution
            executor_data = {
                "name": "Local Execution",
                "type": "local",
                "url": "http://localhost",
                "buildOrder": int(datetime.now().timestamp()),
                "buildName": "Local Test Run",
                "buildUrl": "http://localhost",
                "reportUrl": "",
                "reportName": "Allure Report",
            }

        executor_file = results_path / "executor.json"
        with open(executor_file, "w", encoding="utf-8") as f:
            json.dump(executor_data, f, indent=2)
        print(f"Generated Allure metadata: {executor_file.name}")
    except Exception as e:
        print(f"Warning: Failed to generate executor.json: {e}")

    # 3. Generate categories.json (only if it doesn't exist)
    try:
        categories_file = results_path / "categories.json"
        if not categories_file.exists() or force_categories:
            if force_categories and categories_file.exists():
                print(f"Overwriting existing {categories_file.name}...")

            categories = [
                {"name": "Ignored tests", "matchedStatuses": ["skipped"]},
                {
                    "name": "Infrastructure problems",
                    "matchedStatuses": ["broken", "failed"],
                    "messageRegex": ".*([Tt]imeout|[Cc]onnection|[Nn]etwork|DNS|502|503|504|gateway|ERR_CONNECTION).*",
                },
                {
                    "name": "Outdated tests",
                    "matchedStatuses": ["broken"],
                    "traceRegex": ".*(NoSuchElementException|ElementNotFound|ElementNotVisibleException|element.*not.*found).*",
                },
                {
                    "name": "Authentication failures",
                    "matchedStatuses": ["failed", "broken"],
                    "messageRegex": ".*(authentication|login|unauthorized|401|403|credential|session.*expired).*",
                },
                {
                    "name": "Assertion failures",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*(AssertionError|assert.*failed|[Ee]xpected.*but.*got).*",
                },
                {
                    "name": "Browser/Driver issues",
                    "matchedStatuses": ["broken"],
                    "messageRegex": ".*(ChromeDriver|GeckoDriver|WebDriver|browser.*closed|Target.*closed|Session.*closed|Browser.*context.*was.*closed).*",
                },
                {
                    "name": "Timeout failures",
                    "matchedStatuses": ["broken", "failed"],
                    "messageRegex": ".*(TimeoutError|Timeout.*exceeded|Waiting.*for.*element.*timed.*out|Page.*navigation.*timed.*out).*",
                },
                {
                    "name": "Page load failures",
                    "matchedStatuses": ["broken", "failed"],
                    "messageRegex": ".*(page.*load|navigation.*failed|ERR_|net::).*",
                },
                {"name": "Product defects", "matchedStatuses": ["failed"]},
                {"name": "Test defects", "matchedStatuses": ["broken"]},
            ]

            with open(categories_file, "w", encoding="utf-8") as f:
                json.dump(categories, f, indent=2)
            print(f"Generated Allure metadata: {categories_file.name}")
        else:
            print(f"Allure metadata exists: {categories_file.name} (skipping)")
    except Exception as e:
        print(f"Warning: Failed to generate categories.json: {e}")


def main():
    """
    Main function for CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Generate Allure Report metadata files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate metadata for local execution
  python -m qa_automation.utils.allure_metadata

  # Generate metadata for specific environment
  python -m qa_automation.utils.allure_metadata --env-name TEST

  # Generate metadata for custom results directory
  python -m qa_automation.utils.allure_metadata --results-dir ./custom-results

  # Force overwrite existing categories.json
  python -m qa_automation.utils.allure_metadata --force
        """
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="./allure-results",
        help="Path to allure-results directory (default: ./allure-results)"
    )
    parser.add_argument(
        "--env-name",
        type=str,
        default=None,
        help="Environment name (e.g., DEV, TEST, PROD). Auto-detected from 'envName' or environment variables if not specified"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite of existing categories.json"
    )
    
    args = parser.parse_args()
    
    # Resolve results directory
    results_dir = Path(args.results_dir).resolve()
    
    # Check if results directory exists
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print(f"   Creating directory: {results_dir}")
        results_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment name if provided
    if args.env_name:
        os.environ["envName"] = args.env_name
    
    # Determine environment name for display
    env_name = (
        args.env_name or
        os.environ.get("envName") or
        os.environ.get("RELEASE_ENVIRONMENTNAME") or
        os.environ.get("BUILD_ENVIRONMENT") or
        "Local"
    )
    
    print("=" * 60)
    print("Allure Report Metadata Generator")
    print("=" * 60)
    print(f"Results Directory: {results_dir}")
    print(f"Environment: {env_name}")
    print("=" * 60)
    print()
    
    # Generate metadata files
    try:
        generate_allure_metadata(str(results_dir), force_categories=args.force)
        
        print()
        print("=" * 60)
        print("Metadata generation completed successfully!")
        print("=" * 60)
        print()
        print("Generated files:")
        print(f"  1. {results_dir / 'environment.properties'}")
        print(f"  2. {results_dir / 'executor.json'}")
        print(f"  3. {results_dir / 'categories.json'}")
        print()
        print("Next steps:")
        print("  - Run: allure generate allure-results -o allure-report --clean")
        print("  - Or: allure serve allure-results")
        print()
        
        return 0
    
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
