import requests
import os
import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
from veracode_api_py import Users, APICredentials


thecreds = APICredentials().renew()

api_id = thecreds['api_id']
api_key = thecreds['api_secret']

#*** Update CI/CD Key store ****

# Constants
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # Replace with your GitHub token
REPO_OWNER = "aszaryk"  #  repository owner's username
REPO_NAME = "verademo-js-api"  #  repository name
SECRET_NAME_ID = "VERACODE_API_ID"  # API ID
NEW_SECRET_VALUE_ID = api_id  #  new secret value
SECRET_NAME_KEY = "VERACODE_API_KEY"  # API KEY
NEW_SECRET_VALUE_KEY = api_key  # new secret value

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
    print(f"Secret value: {encoded_value}")
    return encoded_value



# Step 3: Update the secret in the GitHub repository
def update_secret(public_key):
    # Update the API ID First
    encrypted_id = encrypt_secret(public_key, NEW_SECRET_VALUE_ID)


    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{SECRET_NAME_ID}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "encrypted_value": encrypted_id,
        "key_id": public_key['key_id']
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 204:
        print(f"Successfully updated the API ID: {SECRET_NAME_ID}")
    else:
        print(f"Failed to update API ID: {response.status_code}, {response.text}")

    # Now Update the API KEY
    encrypted_key = encrypt_secret(public_key, NEW_SECRET_VALUE_KEY)


    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{SECRET_NAME_KEY}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "encrypted_value": encrypted_key,
        "key_id": public_key['key_id']
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 204:
        print(f"Successfully updated the API KEY: {SECRET_NAME_KEY}")
    else:
        print(f"Failed to update API KEY: {response.status_code}, {response.text}")

def main():
    public_key = get_public_key()
    if public_key:
        update_secret(public_key)

if __name__ == "__main__":
    main()
