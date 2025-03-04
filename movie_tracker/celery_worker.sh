#!/bin/bash

# Navigate to the directory containing manage.py
cd /path/to/your/movie_tracker  # Replace with the actual path

# Activate the virtual environment (if you're using one)
source venv/bin/activate  # Replace 'venv' with your virtual environment name, if applicable

# Start the Celery worker
celery -A movie_tracker worker -l info

# You can also start the Celery beat scheduler in a separate terminal or background it:
# celery -A movie_tracker beat -l info