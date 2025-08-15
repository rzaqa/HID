
Pre condition:
1. Have installed and run Docker Desktop
2. Have Python v.3.12
3. Have installed pre-commit
4. Installed libraries from requirements.txt file


Create local venv 
```bash
python3 -m venv venv 
```

Install dependencies
```bash
pip install -r requirements.txt
```

Run test in docker container:
```bash
./run_in_docker.sh 
```

Generate an allure report:
```bash
allure serve hid_tests/test_reports/allure/allure-results
```

Run pre-commit checks:
```bash
pre-commit run --all-files
```

Get MD5 sum for a test file (a, or b)
```bash
md5sum hid_tests/data/samples/positive/a.txt
```
```bash
md5sum hid_tests/data/samples/positive/b.txt
```