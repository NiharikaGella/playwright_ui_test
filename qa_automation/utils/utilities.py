import inspect
import subprocess
import os
import sys
import json
import logging
import utils.filepaths as fp


def get_os_type():
    """Detect the operating system type."""
    if sys.platform.startswith("freebsd"):
        return "freebsd"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform.startswith("win32"):  # windows
        return "win32"
    elif sys.platform.startswith("darwin"):  # mac
        return "darwin"
    elif sys.platform.startswith("cygwin"):  # Windows/Cygwin
        return "cygwin"


def get_logged_in_user_name():
    """Get the currently logged in username."""
    if get_os_type() == "linux":
        username = os.environ.get("USER")
    elif get_os_type() == "win32":
        username = os.environ.get("USERNAME")
    else:
        # Handle other platforms (e.g., macOS)
        username = "Unknown"
    return username


logger = logging.getLogger("qa_automation")


def log_and_display(log_type=None, log_message=None):
    """
    Log messages with different log levels.

    Please provide log_type from below list:
        debug
        info
        warning
        critical
        error
        exception
    """
    calling_function_frame = inspect.getouterframes(inspect.currentframe(), 2)
    calling_function_name = calling_function_frame[1][3]
    match (str(log_type).lower()):
        case "debug":
            logger.debug(f"{calling_function_name} : {str(log_message)}")
        case "info":
            logger.info(f"{calling_function_name} : {str(log_message)}")
        case "warning":
            logger.warning(f"{calling_function_name} : {str(log_message)}")
        case "critical":
            logger.critical(f"{calling_function_name} : {str(log_message)}")
        case "error":
            logger.error(f"{calling_function_name} : {str(log_message)}")
        case "exception":
            logger.exception(f"{calling_function_name} : {str(log_message)}")
        case _:
            logger.info(f"{calling_function_name} : {str(log_message)}")


def get_config_file_json_object(config_file_path) -> dict:
    """Read and parse JSON configuration file."""
    with open(config_file_path, "r") as json_file:
        json_object_data = json_file.read()
        if not json_object_data:
            log_and_display(
                log_type="error",
                log_message=f"ERROR! File '{config_file_path}' is empty or null",
            )
            return None
        else:
            json_object = json.loads(json_object_data)
            return json_object


is_local = False


def get_environment_variable(env_variable):
    """Get environment variable from system or user environment.

    Works on both Windows and Linux platforms:
    - CI/CD environments: Uses os.environ (Azure DevOps pipeline variables)
    - Windows local: Falls back to PowerShell if os.environ doesn't have it
    - Linux local: Uses os.environ only
    """
    # First, try to get from os.environ (works on all platforms, CI/CD and local)
    system_env_variable = os.environ.get(env_variable)

    if system_env_variable and system_env_variable != "":
        return system_env_variable

    # If not found in os.environ and we're on Windows, try PowerShell as fallback
    if get_os_type() == "win32":
        # Check if powershell is available (won't be on Linux)
        try:
            raw_path = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"[Environment]::GetEnvironmentVariable('{env_variable}', 'User')",
                ],
                capture_output=True,
                timeout=5,
                check=False,
            )
            user_path = raw_path.stdout.decode("ascii").split(";")
            user_variable = [str(i).rstrip("\r\n") for i in user_path][0]
            if user_variable and user_variable != "":
                return user_variable
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # PowerShell not available or timed out, continue to error handling
            pass

    # Environment variable not found in either location
    log_and_display(
        log_type="critical",
        log_message=f"Issue Caught >>> Environment variable '{env_variable}' is empty or null. Checked os.environ and Windows registry (if applicable).",
    )


def update_json_key(
    json_file_path=None,
    key=None,
    value=None,
):
    """
    Update a JSON file with the specified key-value pair.
    If the key already exists, it updates its value; otherwise, it adds a new key-value pair.
    """
    if json_file_path is None or key is None:
        log_and_display(
            log_type="error",
            log_message="JSON file path and key are required.",
        )
        return

    # Check if the file exists
    if not check_file_exists(json_file_path):
        log_and_display(
            log_type="error",
            log_message=f"JSON file '{json_file_path}' does not exist.",
        )
        return

    try:
        with open(json_file_path, "r") as json_file:
            json_data = json.load(json_file)
            json_data[key] = value

        # Write the updated JSON object back to the file
        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=2)
            log_and_display(
                log_type="info",
                log_message=f"Successfully updated '{key}' in JSON file '{json_file_path}'",
            )
    except json.JSONDecodeError as e:
        log_and_display(
            log_type="exception",
            log_message=f"Error decoding JSON file: {e}",
        )
    except FileNotFoundError as e:
        log_and_display(
            log_type="exception",
            log_message=f"Error reading or writing JSON file: {e}",
        )
    except Exception as e:
        log_and_display(
            log_type="exception",
            log_message=f"An unexpected error occurred: {e}",
        )


def get_file_path(file_name):
    """Get the full file path for a file in the current working directory."""
    return os.path.join(os.getcwd(), file_name)


def get_file_path_from_folder(folder_path: str, file_name: str) -> str:
    """Get the full file path for a file in a specific folder."""
    return os.path.join(folder_path, file_name)


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists at the given path."""
    return os.path.exists(file_path)


def create_file_in_specific_folder_if_not_exists(
    folder_path: str, file_name: str
) -> str:
    """Create a file in a specific folder if it doesn't exist."""
    file_path = get_file_path_from_folder(folder_path, file_name)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not check_file_exists(file_path):
        with open(file_path, "w") as file:
            file.write("")
    return file_path


def get_file_row_lines_count(file_path: str) -> int:
    """
    Returns the number of lines (rows) in the specified file (excluding header).

    Args:
      file_path (str): Path to the file.

    Returns:
      int: Number of lines in the file, or -1 if file does not exist.
    """
    if not check_file_exists(file_path):
        log_and_display(
            log_type="error", log_message=f"File '{file_path}' does not exist."
        )
        return -1
    try:
        row_count = 0
        with open(file_path, "r", encoding="utf-8") as file:
            next(file, None)  # Skip header
            for line in file:
                row_count += 1
            return row_count
    except Exception as e:
        log_and_display(
            log_type="exception", log_message=f"Error reading file '{file_path}': {e}"
        )
        return -1
