import io
import logging
import os
import sys
import time
import traceback
import allure
import pytest
import xdist
from pathlib import Path
from playwright.sync_api import sync_playwright

# Conditional import for Windows-only packages
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# This file is used to configure pytest fixtures and hooks for the test suite.


pytest.plugin = ["pytest_bdd"]


# ============================================ Allure Metadata Generation ============================================
def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before performing collection.
    Generate Allure metadata at the start of the test session.
    """
    # Get allure-results directory from pytest config
    allure_dir = session.config.option.allure_report_dir
    if allure_dir:
        print(f"\n{'='*70}")
        print("Generating Allure Report Metadata...")
        print(f"{'='*70}")
        generate_allure_metadata(allure_dir)
        print(f"{'='*70}\n")


# ============================================ Pytest-BDD Tag to Marker Conversion ============================================
def pytest_bdd_apply_tag(tag, function):
    """
    Automatically convert BDD tags from feature files to pytest markers.
    This allows using -m flag with BDD scenario tags like @sparsity_gias, @smoke, etc.

    This hook is called by pytest-bdd for each tag found in feature files.
    """
    if hasattr(pytest.mark, tag):
        marker = getattr(pytest.mark, tag)
        marker(function)
    return True


def pytest_collection_modifyitems(session, config, items):
    """
    Modify test items after collection to apply BDD feature tags as pytest markers.
    This ensures that feature file tags can be used with pytest -m flag.
    """


def pytest_collection_modifyitems(session, config, items):
    """
    Modify test items after collection to apply BDD feature tags as pytest markers.
    This ensures that feature file tags can be used with pytest -m flag.
    """
    for item in items:
        # Check if this is a BDD test with a feature file
        if hasattr(item, "obj") and hasattr(item.obj, "__scenario__"):
            scenario = item.obj.__scenario__
            # Apply feature tags
            if hasattr(scenario.feature, "tags") and scenario.feature.tags:
                for tag in scenario.feature.tags:
                    item.add_marker(getattr(pytest.mark, tag))
            # Apply scenario tags
            if hasattr(scenario, "tags") and scenario.tags:
                for tag in scenario.tags:
                    item.add_marker(getattr(pytest.mark, tag))


# Configure root folder path. This is necessary for relative path references to work.
sys.path.append(str(os.path.join(str(Path().absolute()), "qa_automation")))
from tests.ui.pages.BasePage import BasePage
import utils.utilities as ut
import utils.filepaths as ft
from utils.allure_metadata import generate_allure_metadata

# Directory to save the user state, videos and screenshots
TEST_RESULTS_DIR = "test_results"
VIDEOS_DIR = "videos"
SCREENSHOTS_DIR = "screenshots"
SCREENSHOTS_DIR_PATH = f"{TEST_RESULTS_DIR}/{SCREENSHOTS_DIR}"
VIDEOS_DIR_PATH = f"{TEST_RESULTS_DIR}/{VIDEOS_DIR}"


def get_viewport():
    """Get desktop screen width & height"""
    if PYAUTOGUI_AVAILABLE:
        screen_width, screen_height = pyautogui.size()
    else:
        # Default viewport for headless/Linux environments
        screen_width, screen_height = 1920, 1080
    viewport = {"width": screen_width, "height": screen_height}
    return viewport


@pytest.fixture(scope="session")
def browser():
    """Fixture to create a new browser instance"""
    with sync_playwright() as pw:
        browser_info: dict = BasePage.get_browser()
        print(f"browser selected: {browser_info['browser']}")
        headless = os.getenv("HEADLESS", "true").lower() != "false"
        browser = getattr(pw, browser_info["browser"]).launch(
            headless=headless, slow_mo=50
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, clean_test_result_directories, request):
    # clean test results directories if exist, if not create those
    clean_test_result_directories
    """Create a browser context."""
    print(
        f"VIDEO_PATH: {VIDEOS_DIR_PATH if not 'data' in request.node.keywords else None}"
    )
    context_options = {
        "viewport": get_viewport(),
        "record_video_dir": VIDEOS_DIR_PATH,
        "record_video_size": get_viewport(),
    }
    storage_state_path = ft.get_ui_storage_state_file_path()
    if os.path.exists(storage_state_path):
        context_options["storage_state"] = storage_state_path
    context = browser.new_context(**context_options)
    # Create a new page from browser context
    page = context.new_page()
    yield page
    # Capture video after closing page & context to ensure Playwright finalises file
    video = getattr(page, "video", None)
    page.close()
    context.close()
    if video and not "data" in request.node.keywords:
        try:
            video_path = video.path()
            # Wait briefly for file to be fully written
            for _ in range(10):
                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    break
                time.sleep(0.5)
            if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                # Handle Allure versions that may not have WEBM type
                attachment_type = (
                    allure.attachment_type.WEBM
                    if hasattr(allure.attachment_type, "WEBM")
                    else allure.attachment_type.MP4
                )
                allure.attach.file(
                    video_path,
                    name=f"Video - {request.node.name}",
                    attachment_type=attachment_type,
                )
            else:
                print(
                    f"Video file {video_path} not ready or empty after wait; skipping attach."
                )
        except Exception as e:
            print(f"Error attaching video: {e}")


@pytest.fixture(scope="session")
def clean_test_result_directories():
    # Create test_results directory if it doesn't exist
    os.makedirs(TEST_RESULTS_DIR, exist_ok=True)
    screenshots_dir = os.path.join(TEST_RESULTS_DIR, SCREENSHOTS_DIR)
    videos_dir = os.path.join(TEST_RESULTS_DIR, VIDEOS_DIR)

    # Create directories if they don't exist
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    # Clean files in screenshots directory
    for filename in os.listdir(screenshots_dir):
        filepath = os.path.join(screenshots_dir, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")

    # Clean files in videos directory
    for filename in os.listdir(videos_dir):
        filepath = os.path.join(videos_dir, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")


@pytest.fixture(scope="function", autouse=True)
def capture_logs(request):
    """Fixture to capture and attach log messages to Allure reports."""
    log_stream = io.StringIO()
    log_handler = logging.StreamHandler(log_stream)
    log_handler.setLevel(logging.INFO)  # Set the desired log level

    logger = logging.getLogger()
    logger.addHandler(log_handler)

    original_stdout = sys.stdout
    sys.stdout = log_stream  # Redirect stdout to the StringIO stream

    yield

    sys.stdout = original_stdout  # Restore stdout
    log_handler.flush()  # Ensure all logs are flushed to the stream
    logger.removeHandler(log_handler)  # Remove the handler after the test
    log_contents = log_stream.getvalue().strip()  # Get the log contents

    if log_contents:
        allure.attach(
            log_contents, name="Test Logs", attachment_type=allure.attachment_type.TEXT
        )
        log_stream.close()
        log_handler.close()  # Close the StringIO stream to free up resources


# ------------------------------------------------------------------------------------


@pytest.hookimpl()
def pytest_bdd_before_scenario(request, feature, scenario):
    # This will be printed before each scenario
    log_scenario_info(feature, scenario, "Started")


@pytest.hookimpl()
def pytest_bdd_after_scenario(request, feature, scenario):
    log_scenario_info(feature, scenario, "Completed")
    ut.log_and_display(
        log_type="info", log_message=f"Completed scenario: '{scenario.name}'"
    )


@pytest.hookimpl()
def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    ut.log_and_display(
        log_type="info",
        log_message=f"Started test step: '{step.name[:300]}' {' ...' if len(step.name)>300 else ''}",
    )


@pytest.hookimpl()
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    # - Called after step function is successfully executed
    ut.log_and_display(
        log_type="info",
        log_message=f"Completed test step: '{step.name[:300]}' {' ...' if len(step.name)>300 else ''}",
    )
    ut.log_and_display(
        log_type="info",
        log_message=(
            "Test Step - 'PASS'" if step.failed == False else "Test Step - 'FAIL'"
        ),
    )
    ut.log_and_display(
        log_type="info",
        log_message="============================================================================",
    )


@pytest.hookimpl()
def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    ut.log_and_display(
        log_type="error",
        log_message=f"ERROR! Test Step FAILURE: \n{step.name}'\n[{step_func}]",
    )
    ut.log_and_display(
        log_type="error", log_message=f"[{exception}]\n {traceback.format_exc()}"
    )
    print(
        f"====================================================================================="
    )
    if not "data" in request.node.keywords:
        # Capture screenshot and attach to report when a step fails
        page = request.getfixturevalue("page")
        base_page = BasePage(page)
        base_page.capture_and_attach_screenshot(step.name)
        page.close()


@pytest.hookimpl()
def pytest_bdd_step_func_lookup_error(request, feature, scenario, step, exception):
    # - Called when step lookup failed
    ut.log_and_display(
        log_type="error",
        log_message=f"Completed test step: '{step.name[:300]}' {' ...' if len(step.name)>300 else ''}",
    )
    ut.log_and_display(log_type="error", log_message="Test Step - 'FAIL'")


def log_scenario_info(feature, scenario, test_status):
    log_msgs = {
        ut.log_and_display(
            log_type="info",
            log_message="-------------------------------------------------------------------------",
        ),
        ut.log_and_display(
            log_type="info",
            log_message=f"Test {test_status}. Feature: '{feature.name}' | Scenario: '{scenario.name}' | Feature tags: '{', '.join([i for i in feature.tags])}'",
        ),
        ut.log_and_display(
            log_type="info",
            log_message="-------------------------------------------------------------------------",
        ),
    }
    for msg in log_msgs:
        print(msg)
