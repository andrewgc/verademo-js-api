import requests
import os
import base64
import json
import nacl.secret
import nacl.utils
from nacl.public import PublicKey, Box, PrivateKey, SealedBox, encoding
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
from veracode_api_py import Users, APICredentials


#thecreds = APICredentials().renew()

#api_id = thecreds['api_id']
#api_key = thecreds['api_secret']

api_id = os.getenv("VERACODE_API_KEY_ID")
api_key = os.getenv("VERACODE_API_KEY_SECRET")


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
def encrypt(public_key: str, secret_value: str) -> str:
    public_key = base64.b64decode(public_key['key'])
    public_key = PublicKey(public_key)
    sealed_box = SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    encrypted_base64 = base64.b64encode(encrypted).decode("utf-8")
    return encrypted_base64


# Step 3: Update the secret in the GitHub repository
def update_secret(public_key):
    # Update the API ID First
    encrypted_id = encrypt(public_key, NEW_SECRET_VALUE_ID)


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
    encrypted_key = encrypt(public_key, NEW_SECRET_VALUE_KEY)


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
