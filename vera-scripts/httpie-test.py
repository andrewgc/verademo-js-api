import sys
import os
import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

# below is for Veracode US Commercial region. For logins in other region uncomment one of the other lines
api_base = "https://api.veracode.com/was/configservice/v1" # for logins in the Veracode US Commercial Region
#api_base = "https://api.veracode.eu" # for logins in the Veracode European Region
#api_base = "https://api.veracode.us" # for logins in the Veracode US Federal Region


#Setup variables according to environment
base_url = "http://verademoapi.aszaryk.vuln.sa.veracode.io:8000"
spec_name = "Verademo API Specification " + os.getenv("JOB_ID")

#GitLab:
#analysis_name = os.getenv("CI_PROJECT_NAME") #Dynamic Job name will be same as GitLab project name

#GitHub:
analysis_name = "Project: " + os.environ.get("REPO_NAME") + " - Workflow Number: " + os.environ.get("JOB_ID") #Dynamic Job name will inherit name from GitHub repository values

headers = {"User-Agent": "Python HMAC Example"}
query_params = "custom_base_url=" + base_url + "&spec_name=" + spec_name
spec_file = {'file': open('../public/postman_collection.json','rb')}

if __name__ == "__main__":

    try:
        response = requests.post(api_base + "/api_specifications", auth=RequestsAuthPluginVeracodeHMAC(), headers=headers, files=spec_file, params=query_params)
    except requests.RequestException as e:
        print("Whoops!")
        print(e)
        sys.exit(1)

    if response.ok:
        data = response.json()
        print (data)
        #for app in data["_embedded"]["applications"]:
        #    print(app["profile"]["name"])
    else:
        print(response.status_code)
        print(response.text)