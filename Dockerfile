FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/hid_tests/src

CMD ["pytest", "-v", "hid_tests/tests", "--alluredir=hid_tests/test_reports/allure/allure-results"]

