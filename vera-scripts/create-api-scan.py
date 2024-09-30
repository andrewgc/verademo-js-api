#!/usr/bin/env python3
import os
import json  
import sys
import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
from veracode_api_py.dynamic import Analyses, Scans, ScanCapacitySummary, ScanOccurrences, ScannerVariables, DynUtils, Occurrences

#Setup variables according to environment

#GitLab:
#analysis_name = os.getenv("CI_PROJECT_NAME") #Dynamic Job name will be same as GitLab project name

#GitHub:
analysis_name = "Project: " + os.environ.get("REPO_NAME") + " - Workflow Number: " + os.environ.get("JOB_ID") #Dynamic Job name will inherit name from GitHub repository values

#Payload for creating and scheduling new DA job

def main():

    #Build out the payload for creating and scheduling new DA job
   
    #Set the TargetURL and scope
    url = DynUtils().setup_url('http://my.verademo.site','DIRECTORY_AND_SUBDIRECTORY',False)
   
    #add TargetURL to allowed host
    allowed_hosts = [url]
   
    #add Authentication information
    auth = DynUtils().setup_auth('AUTO','admin','smithy')
    auth_config = DynUtils().setup_auth_config(auth)

    #Configure Crawl Script
    crawl_config = DynUtils().setup_crawl_configuration([],False)

    #Add any blocklist, custom hosts or change default user agent
    scan_setting = DynUtils().setup_scan_setting(blocklist_configs=[],custom_hosts=[],user_agent=None)

    #Build the config JSON
    scan_config_request = DynUtils().setup_scan_config_request(url, allowed_hosts,auth_config, crawl_config, scan_setting)

    #Create the full scan payload
    scan = DynUtils().setup_scan(scan_config_request)

    #Add scan duration (Setting this will automatically kick off the scan when it is created)
    start_scan = DynUtils().start_scan(12, "HOUR")

    #Combine the scan payload, analysis name and schedule and submit to Veracode platform
    analysis = Analyses().create(analysis_name,scans=[scan],owner='Andrzej',email='andrzej@example.com', start_scan=start_scan)


if __name__ == "__main__":
    main()
