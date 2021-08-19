pytest -s -n auto --ignore=tests/test_images.py
pytest tests/test_images.py --cov-append
coverage xml