import requests

url = "https://www.optimumnutrition.co.in/products/gold-standard-100-whey-protein-powder-double-rich-chocolate-1118949.json"

response = requests.get(url)

print(response.status_code)
print(response.headers["Content-Type"])
print(response.text[:500])