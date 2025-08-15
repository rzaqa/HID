#!/bin/bash

docker build -t hid-tests .

docker run --rm -it \
  -v "$(pwd)/hid_tests/test_reports:/app/hid_tests/test_reports" \
  -v "$(pwd)/lib:/app/lib" \
  hid-tests \
  pytest -v \
    --timeout=10 \
    --timeout-method=thread \
    --capture=sys \
    --cov=hid_tests/src \
    --cov-report=term-missing \
    --cov-report=html:hid_tests/test_reports/coverage \
    --alluredir=hid_tests/test_reports/allure/allure-results