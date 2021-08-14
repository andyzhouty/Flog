coverage run -m pytest -s -n auto --ignore=tests/test_images.py
coverage run -a -m pytest tests/test_images.py
coverage xml