import requests

url = "http://127.0.0.1:8000/upload"
filepath = "datasets/sample_dataset.csv"

with open(filepath, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response:", response.text)
