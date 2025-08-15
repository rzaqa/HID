FROM python:3.12-slim

# Install minimal runtime dependencies that native .so may rely on
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#       ca-certificates \
#       libstdc++6 \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make wrapper importable as top-level module `hash_wrapper`
ENV PYTHONPATH=/app/hid_tests/src

# Default command: simple smoke run to verify the native library loads on Linux
# Override this with: docker run --rm -it <image> python -c "..." or pytest
#CMD ["python", "-c", "import hash_wrapper as hw; hw.init_library(); print('Hash library initialized OK'); hw.terminate_library(); print('Hash library terminated OK')"]

# Set default command to run tests
CMD ["pytest", "-q", "hid_tests/tests", "--alluredir=hid_tests/test_reports/allure/allure-results"]


