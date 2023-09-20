import requests
import json
import os
import argparse
from django.conf import settings

def get_cve(cve_id):
    api_key = "57fa417a-91f6-4898-b6d8-6a3f820f4948"
    # cve_id = "CVE-2019-19089"
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apiKey": api_key
    }
    params = {"cveId": cve_id}
    cve_details={}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data.get('vulnerabilities'):
            if data['vulnerabilities'][0].get('cve'):
                if data['vulnerabilities'][0]['cve'].get('descriptions'):
                    desc_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['descriptions']) if i["lang"] == "en"), 0)
                    cve_details = {
                            **cve_details,
                            **{
                                'cve_id':data['vulnerabilities'][0]['cve']['id'],
                                'description':data['vulnerabilities'][0]['cve']['descriptions'][desc_index]['value']
                            }
                        }
                if data['vulnerabilities'][0]['cve'].get('metrics'):
                    if data['vulnerabilities'][0]['cve']['metrics'].get('cvssMetricV31'):
                        cvss3_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31']) if i["source"] == "nvd@nist.gov"), 0)
                        cve_details = {
                            **cve_details,
                            **{
                                'cvvs3':{
                                    'base_score': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31'][cvss3_index]['cvssData']['baseScore'],
                                    'error_type': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31'][cvss3_index]['cvssData']['baseSeverity'],
                                }
                            }
                        }
                    else:
                        cve_details = {
                            **cve_details,
                            **{
                                'cvvs3':{
                                    'base_score': 'N/A',
                                    'error_type': 'N/A',
                                }
                            }
                        }
                    if data['vulnerabilities'][0]['cve']['metrics'].get('cvssMetricV2'):
                        cvss2_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2']) if i["source"] == "nvd@nist.gov"), 0)
                        cve_details = {
                            **cve_details,
                            **{
                                'cvvs2':{
                                    'base_score': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2'][cvss2_index]['cvssData']['baseScore'],
                                    'error_type': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2'][cvss2_index]['cvssData']['accessComplexity'],
                                }
                            }
                        }
                    else:
                        cve_details = {
                            **cve_details,
                            **{
                                'cvvs2':{
                                    'base_score': 'N/A',
                                    'error_type': 'N/A',
                                }
                            }
                        }
                if data['vulnerabilities'][0]['cve'].get('references'):
                    refences = [reference['url'] for reference in data['vulnerabilities'][0]['cve']['references']]
                    cve_details = {
                        **cve_details,
                        **{
                            'sources': refences
                        }
                    }

                if data['vulnerabilities'][0]['cve'].get('weaknesses'):
                    weaknesses = [cwe['value'] for weakness in data['vulnerabilities'][0]['cve']['weaknesses'] for cwe in weakness['description']]
                    cve_details = {
                        **cve_details,
                        **{
                            'cwe_ids': weaknesses
                        }
                    }

        print("#"*30,"CVE Details", "#"*30)
        print("\n\n",cve_details, "\n\n")
        print("#"*73)
    else:
        print("#"*73)
        print("CVE NOT FOUND")
        print("#"*73)


parser = argparse.ArgumentParser()
parser.add_argument('--cve', type=str, required=True, help="ex. CVE-2020-11022")
args = parser.parse_args()
cve_id = args.cve
get_cve(cve_id)