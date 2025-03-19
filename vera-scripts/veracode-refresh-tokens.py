import requests
import os
import base64
import json
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
from veracode_api_py import Users, APICredentials


thecreds = APICredentials().renew()

api_id = thecreds['api_id']
api_key = thecreds['api_secret']

print('')
print('veracode_api_key_id={}'.format(api_id))
print('veracode_api_key_secret={}'.format(api_key))
print('')
print('Please clear your terminal and scrollback buffer once you have copied the credentials!')

#*** Update CI/CD Key store ****

# Constants
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # Replace with your GitHub token
REPO_OWNER = "aszaryk"  # Replace with the repository owner's username
REPO_NAME = "verademo-js-api"  # Replace with the repository name
SECRET_NAME = "VERACODE_UPDATE_TEST"  # Replace with the name of the secret you want to update
NEW_SECRET_VALUE = "12345"  # Replace with the new secret value

# Step 1: Get the public key for the repository
def get_public_key():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get public key: {response.status_code}, {response.text}")
        return None

# Step 2: Encrypt the secret using the public key
def encrypt_secret(public_key, secret_value):
    public_key_str = public_key['key']
    key_id = public_key['key_id']

    # Convert secret value to base64 encoding
    encoded_value = base64.b64encode(secret_value.encode('utf-8')).decode('utf-8')

    # For the purpose of this example, just base64 encode the value. 
    # In a real implementation, you'd use RSA encryption with a library like PyCryptodome
    return encoded_value

# Step 3: Update the secret in the GitHub repository
def update_secret(public_key):
    encrypted_value = encrypt_secret(public_key, NEW_SECRET_VALUE)

    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{SECRET_NAME}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "encrypted_value": encrypted_value,
        "key_id": public_key['key_id']
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 204:
        print(f"Successfully updated the secret: {SECRET_NAME}")
    else:
        print(f"Failed to update secret: {response.status_code}, {response.text}")

def main():
    public_key = get_public_key()
    if public_key:
        update_secret(public_key)

if __name__ == "__main__":
    main()
