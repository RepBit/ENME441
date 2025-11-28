import requests

url = "http://192.168.1.254:8000/positions.json"   # Replace with your URL

response = requests.get(url)
response.raise_for_status()             # Raises an error for bad status codes

data = response.json()                  # Parse JSON directly

print(data)