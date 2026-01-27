import requests

url = "http://127.0.0.1:8000/parse"
headers = {"X-API-KEY": "1234567890"}
files = {'file': open('test_statement.pdf', 'rb')}
data = {'bank_name': 'UNION BANK OF INDIA'}

try:
    response = requests.post(url, headers=headers, files=files, data=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
