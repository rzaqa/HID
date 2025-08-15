import json



with open("hid_tests/data/cases.json", "r") as test_data:
    test_data = json.load(test_data)
    positive_data_set = test_data["positive_cases"]
    negative_data_set = test_data["negative_cases"]
    print(test_data)
    print(positive_data_set)
    print(negative_data_set)

