import requests
from bs4 import BeautifulSoup
import re
import argparse

def get_cve_details(cve):
    url = 'https://www.cvedetails.com/cve-details.php?cve_id=' + cve
    print('\nScrape URL =>\t',url, "\n\n")
    response = requests.get(url)
    cve_details = {}
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('td', id="cvedetails").find_all('h1')[0].find('a'):
            cve_details['cve_id'] = soup.find('td', id="cvedetails").find_all('h1')[0].find('a').text
            cve_details['description'] = re.sub('\t', '', soup.find('div', {'class': 'cvedetailssummary'}).find('br').previousSibling)
            cve_details['cvss_score'] = soup.find('th', string='CVSS Score').find_next_sibling().find('div').text
            cve_details['access_complexity'] = soup.find('th', string='Access Complexity').find_next_sibling().find_all('span')[0].text
    return cve_details

def get_ms_details(ms_id):
    url = f'https://www.cvedetails.com/search-by-microsoft-refid.php?msid={ms_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cve_details = {}
    cve_table = soup.find('table',id='vulnslisttable')
    if cve_table:
        cve = cve_table.find_all('tr')[1].find_all('td')[1].find('a').text
        cve_details = get_cve_details(cve)
        return cve_details
    return cve_details

# cve = 'CVE-2010-0018'
# cve_details = get_cve_details(cve)
# print('Output: ', cve_details')

# ms_id = 'ms10-001'
# cve_details = get_ms_details(ms_id)
# print('Output: ', cve_details)
parser = argparse.ArgumentParser()

# Add argument group
group = parser.add_argument_group('vulnerability')
group.add_argument('--cve', type=str, help='cve id')
group.add_argument('--ms', type=str, help='ms id')
args = parser.parse_args()
output = {}
if args.cve:
    cves = args.cve.split(",")
    for cve in cves:
        output = get_cve_details(cve)
        print('Output: ',output)
elif args.ms:
    output = get_ms_details(args.ms)
    print('Output: ',output)




# https://www.cvedetails.com/search-by-microsoft-refid.php?msid=ms10-001
# https://www.cvedetails.com/cve-details.php?cve_id=CVE-2010-0018
# https://www.cvedetails.com/cve-details.php?cve_id=CVE-2011-1002
# https://nvd.nist.gov/vuln/detail/CVE-2010-0018