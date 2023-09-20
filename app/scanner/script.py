import requests
import json
import os
import argparse

def scan_without_auth(targets_id, origin):
    """
    It takes a list of machine IDs, and sends a POST request to the API endpoint `/scan/add-in-queue/`
    with the list of machine IDs as the payload
    
    :param targets_id: The ID of the machine you want to scan
    """
    try:
        url = f"{origin}/api/scan/addByIds/"
        payload = json.dumps({
        "targets_id": targets_id
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

def scan_with_auth(targets_id, origin, token):
    """
    It takes a list of machine IDs, and sends a POST request to the API endpoint `/scan/add-in-queue/`
    with the list of machine IDs as the payload
    
    :param targets_id: The ID of the machine you want to scan
    """
    try:
        url = f"{origin}/api/scan/addByIds/"
        payload = json.dumps({
        "targets_id": targets_id
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
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
parser.add_argument("--targets_id", '-ids', type=str ,required=True, help="ids of machines or hosts in format something like 1,2,3")
parser.add_argument("--token", '-t', type=str ,required=True, help="Authorization token")
# group = parser.add_mutually_exclusive_group(required=True)
# group.add_argument("--targets_id", type=str ,required=False)
args = parser.parse_args()
origin = args.origin
targets_id = args.targets_id.split(",")
token = args.token
scan_with_auth(targets_id , origin, token)