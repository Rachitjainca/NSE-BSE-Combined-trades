import requests
import socket
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Testing network connectivity...")
print("=" * 50)

# Test DNS resolution
try:
    ip = socket.gethostbyname('groww.in')
    print(f"✓ DNS resolution successful: groww.in -> {ip}")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    exit(1)

# Test HTTP request
try:
    print("\nTesting HTTP request to https://groww.in/investor-relations...")
    response = requests.get('https://groww.in/investor-relations', timeout=10, verify=False, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"✓ HTTP request successful. Status Code: {response.status_code}")
    print(f"Page title: {'<title>' in response.text}")
except Exception as e:
    print(f"❌ HTTP request failed: {type(e).__name__}: {e}")
    exit(1)

print("\nNetwork connectivity is fine. Issue might be specific to Selenium.")
