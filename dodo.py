import os
import subprocess


def task_install():
    """Install Python dependencies."""
    return {
        "actions": ["pip install -r requirements.txt"],
        "verbosity": 2,
    }


def task_start():
    """Run the Flask application."""
    return {
        "actions": ["python main.py"],
        "verbosity": 2,
    }


def task_test():
    """Run all unit tests."""
    return {
        "actions": ['python -m unittest discover -s . -p "*_test.py"'],
        "verbosity": 2,
    }


def task_cleanup():
    """Remove __pycache__ and .pyc files."""
    return {
        "actions": [
            'find . -type d -name "__pycache__" -exec rm -r {} +',
            'find . -name "*.pyc" -delete',
        ],
        "verbosity": 2,
    }


def task_format():
    """Format Python code using black and Jinja2 templates using djlint."""
    return {
        "actions": ["black ."],
        "verbosity": 2,
    }


def task_format_templates():
    """Format Jinja2/HTML templates using djlint (quietly)."""
    return {
        "actions": [format_templates],
        "verbosity": 2,
    }


def task_lint_templates():
    """Lint Jinja2/HTML templates using djlint (no changes)."""
    return {
        "actions": ["djlint frontend/templates/"],
        "verbosity": 2,
    }


def task_clear_logs():
    """Clear log files."""
    return {
        "actions": ["rm -f logs/*.log"],
        "verbosity": 2,
    }


# --- Helper functions ---


def format_templates():
    """Run djlint quietly and print success message."""
    null_out = subprocess.DEVNULL  # cross-platform

    result = subprocess.run(
        ["djlint", "frontend/templates/", "--reformat"],
        stdout=null_out,
        stderr=null_out,
    )

    if result.returncode in (0, 1):
        print("✅ Format successful.")
    else:
        raise subprocess.CalledProcessError(result.returncode, result.args)
