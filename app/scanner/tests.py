import requests
import json
import os
import argparse

def scanner(machines_id, origin):
    """
    It takes a list of machine IDs, and sends a POST request to the API endpoint `/scan/add-in-queue/`
    with the list of machine IDs as the payload
    
    :param machines_id: The ID of the machine you want to scan
    """
    try:
        url = f"{origin}/scan/add-in-queue/"
        payload = json.dumps({
        "machines_id": machines_id
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(">"*30," "*15,"Response start", " "*15,"<"*30)
        print(response.text)
        print(">"*30," "*15,"Response end", " "*15,"<"*30)
    except Exception as e:
        print(">"*30," "*15,"Exception Found with below content", " "*15,"<"*30)
        print(str(e))
        print(">"*30," "*15,"Exception content end", " "*15,"<"*30)



parser = argparse.ArgumentParser()
parser.add_argument('--origin', '-o', type=str, required=True, help="origin to call API")
parser.add_argument("--machines_id", '-ids', type=str ,required=True, help="ids of machines or hosts in format something like 1,2,3")
# group = parser.add_mutually_exclusive_group(required=True)
# group.add_argument("--machines_id", type=str ,required=False)
args = parser.parse_args()
origin = args.origin
machines_id = args.machines_id.split(",")
scanner(machines_id , origin)