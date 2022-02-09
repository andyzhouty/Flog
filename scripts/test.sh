set -e
pytest -s -n auto --ignore=tests/test_images.py --no-cov
pytest tests/test_images.py --no-cov