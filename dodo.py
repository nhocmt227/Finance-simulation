def task_install():
    """Install Python dependencies."""
    return {
        'actions': ['pip install -r requirements.txt'],
        'verbosity': 2,
    }

def task_start():
    """Run the Flask application."""
    return {
        'actions': ['python main.py'],
        'verbosity': 2,
    }

def task_test():
    """Run all unit tests."""
    return {
        'actions': ['python -m unittest discover -s . -p "*_test.py"'],
        'verbosity': 2,
    }

def task_cleanup():
    """Remove __pycache__ and .pyc files."""
    return {
        'actions': [
            'find . -type d -name "__pycache__" -exec rm -r {} +',
            'find . -name "*.pyc" -delete'
        ],
        'verbosity': 2,
    }