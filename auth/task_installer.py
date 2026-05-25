"""
Installs or removes the FitTrack reminder service
as a Windows Task Scheduler task that runs at login.
"""
import subprocess
import sys
import os


TASK_NAME = "FitTrackReminderService"


def get_service_path():
    """Returns the full path to reminder_service.py"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "auth", "reminder_service.py"
    )


def get_python_path():
    """Returns the path to the current Python executable (inside venv)."""
    return sys.executable


def install_task():
    """
    Registers the reminder service with Windows Task Scheduler.
    Returns (True, "message") or (False, "error").
    """
    python = get_python_path()
    script = get_service_path()

    # schtasks command to create a task that runs at every login
    cmd = [
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", f'"{python}" "{script}"',
        "/sc", "ONLOGON",
        "/rl", "HIGHEST",
        "/f"   # force overwrite if exists
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=True
        )
        if result.returncode == 0:
            return True, "Reminder service installed. It will start automatically at next login."
        else:
            return False, f"Failed to install: {result.stderr.strip()}"
    except Exception as e:
        return False, str(e)


def remove_task():
    """Removes the scheduled task."""
    cmd = ["schtasks", "/delete", "/tn", TASK_NAME, "/f"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=True
        )
        if result.returncode == 0:
            return True, "Reminder service removed."
        else:
            return False, f"Failed to remove: {result.stderr.strip()}"
    except Exception as e:
        return False, str(e)


def task_exists():
    """Returns True if the scheduled task is already installed."""
    cmd = ["schtasks", "/query", "/tn", TASK_NAME]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=True
        )
        return result.returncode == 0
    except Exception:
        return False


