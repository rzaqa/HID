#!/bin/bash
set -e  # Exit on error

# Build Docker image
docker build -t hid-tests .

# Run tests in container
docker run --rm \
    -v "$(pwd)/hid_tests/test_reports:/app/hid_tests/test_reports" \
    hid-tests \
    pytest -v -s \
        --alluredir=hid_tests/test_reports/allure/allure-results
