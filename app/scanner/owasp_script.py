from zapv2 import ZAPv2
import time
from datetime import datetime
import json
from tldextract import extract
import time
import pandas as pd
import argparse
import os
import platform
from zapv2 import ZAPv2
zap = ZAPv2()

class Common:
    def clear_scr(self):
        if platform.uname().system == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

    def set_html_report(self, url, risk_levels, alerts, scan_type="spider"):
        alerts_html = ""
        # for key,value in risk_levels.items():
        alert_details_html = ""
        for key,value in alerts.items():
            alerts_html += f'''
                <tr>
                    <td><a href="">{key}</a></td>
                    <td align="center" class="{risk_levels[value['risk']]['class']}">{value['risk']}</td>
                    <td align="center">{value['instances']}</td>
                </tr>
            '''

            alert_details_html += f'''
                <table class="results">
                    <tr height="24">
                        <th width="20%" class="{risk_levels[value['risk']]['class']}"><a
                            id="10202"></a>
                            <div>{value['risk']}</div></th>
                        <th class="{risk_levels[value['risk']]['class']}">{key}</th>
                    </tr>
                    <tr>
                        <td width="20%">Description</td>
                        <td width="80%">
                                <div>{value['description']}</div>
                    </tr>'''
            if value.get('urls'):
                alert_details_html += '''<TR vAlign="top">
                    <TD colspan="2"></TD>
                </TR>'''
                    
                for url_obj in value.get('urls'):
                    alert_details_html += f'''<tr>
                            <td width="20%"
                                class="indent1">URL</td>
                            <td width="80%">{url_obj['url']}</td>
                        </tr>
                        <tr>
                            <td width="20%"
                                class="indent2">Method</td>
                            <td width="80%">{url_obj['method']}</td>
                        </tr>
                        <tr>
                            <td width="20%"
                                class="indent2">Parameter</td>
                            <td width="80%">{url_obj['parameter']}</td>
                        </tr>
                        <tr>
                            <td width="20%"
                                class="indent2">Attack</td>
                            <td width="80%">{url_obj['attack']}</td>
                        </tr>
                        <tr>
                            <td width="20%"
                                class="indent2">Evidence</td>
                            <td width="80%">{url_obj['evidence']}</td>
                        </tr>'''
                    
            alert_details_html += f'''<tr>
                        <td width="20%">Instances</td>
                        <td width="80%">{value['instances']}</td>
                    </tr>
                    <tr>
                        <td width="20%">Solution</td>
                        <td width="80%">
                                <div>{value['solution']}</div>
                            </td>
                    </tr>
                    <tr>
                        <td width="20%">Reference</td>
                        <td width="80%">
                            {value['reference']}
                        </td>
                    </tr>
                    <tr>
                        <td width="20%">CWE Id</td>
                        <td width="80%"><a
                            href="https://cwe.mitre.org/data/definitions/{value['cweid']}.html">{value['cweid']}</a></td>
                    </tr>
                    <tr>
                        <td width="20%">WASC Id</td>
                        <td width="80%">{value['wascid']}</td>
                    </tr>
                    <tr>
                        <td width="20%">Plugin Id</td>
                        <td width="80%"><a
                            href="https://www.zaproxy.org/docs/alerts/{value['plugin_id']}/">{value['plugin_id']}</a></td>
                    </tr>
                </table>
                <div class="spacer"></div>
            '''

        
        html_str = '''
            <!DOCTYPE html>
            <html>
            <head>
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>ZAP Scanning Report</title>
            <style type="text/css">
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                color: #000;
                font-size: 13px;
            }

            h1 {
                text-align: center;
                font-weight: bold;
                font-size: 32px
            }

            h3 {
                font-size: 16px;
            }

            table {
                border: none;
                font-size: 13px;
            }

            td, th {
                padding: 3px 4px;
                word-break: break-word;
            }

            th {
                font-weight: bold;
                background-color: #666666;
            }

            td {
                background-color: #e8e8e8;
            }

            .spacer {
                margin: 10px;
            }

            .spacer-lg {
                margin: 40px;
            }

            .indent1 {
                padding: 4px 20px;
            }

            .indent2 {
                padding: 4px 40px;
            }

            .risk-3 {
                background-color: red;
                color: #FFF;
            }

            .risk-2 {
                background-color: orange;
                color: #FFF;
            }

            .risk-1 {
                background-color: yellow;
                color: #000;
            }

            .risk-0 {
                background-color: blue;
                color: #FFF;
            }

            .risk--1 {
                background-color: green;
                color: #FFF;
            }

            .summary {
                width: 45%;
            }

            .summary th {
                color: #FFF;
            }

            .alerts {
                width: 75%;
            }

            .alerts th {
                color: #FFF;
            }

            .results {
                width: 100%;
            }

            .results th {
                text-align: left;
            }

            .left-header {
                display: inline-block;
            }
            </style>
            </head>
        '''
        html_str +=f'''
            <body>
                <h1>
                    <!-- The ZAP Logo -->
                    <img
                        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAABqbAAAamwHdbkbTAAAAB3RJTUUH4QsKDDQPKy6k8AAABxpJREFUWMO9l31sVWcdxz+/55xzbwt9QddJExClvIzNxTKJDZi22oJSbFZpmRb4g8sfhpEIwXQNTKh0NYgiMKIwo5AsdIxdQldGNBN5W2OTFRVcIZE1YwExcXOdc1DK+nLvOc/PP87tC9CWsj98bp6ck3Ofc57v7+37/T3wYGMucBR4F/gK/8exAugAdPXq1bpx40YFekZdHYuP+8PuGP+lAc8CmzIyMtLq6uqora3FcRwAzp49m/7Wv5O95tsNEfyEKvwH9B1V2hT7GnB+PABkhGePAvVA9dy5c6mvr2fp0qX3LOru7iYrK4toSQ1OXhGKohpOiyVQe0NVn9PGFb8iFofGFSMCMMPulwEXgbdXrlxZ3dHRQXt7+4ibA2RmZtLc3Ex/y/O4fg8RMUSMS8RxiRiPqPE+4xrnl07syA3Q+aN5wADlwO1oNPpqQ0NDfl9fH4cPH2bOnDn3dV9VVRWVlVV88vsteNF0XCO4xuA6Bs9xiBgPz/EmueKcIxavHyk/BPjnli1bpm3btu1TZ2hmxkTk8aeYMK8aay1WFVWwqgSqBDYgqQFJGxygccWa4e86IhJpbW39Zk5ODgUFBZ8KwOLFZeyr/wHZs0vw0jMxIqFpAuFt+EOYZ/OrAi41t96dhF8HThcWFnpnzpwhGo0+MIhnamvZs+8AM55uIhn4+Cnrkza8Wqv4NiBhfXwNCgxy3jauuKMKPOCPrpHSU2fOUlJS8sAg8qZP50bGY0xeuIFk4JO0SnIYiMAqSRuQDPyPgsbqh++ugqSsPXGC+WsoLS1lzZqnHxhA40svcfPvfyDNjRARwTOCJ+E0IjgiOGIwRnIkFl97NwBMX9dPvEfLSC+t5cCB/eTk5Ix78ylTplBcXMxDjy3EweIZISKSqoxwcyOCYwRXHETkuSEAsTjE4kVGTLrjpdP7p33U1NTQ2dk5bgCbN28Ow7BoA8YmcVOWR1KWuyKIgEEwYjBiJhN75Ushr15qRp747g9dcRZ4RtCuf3HhdBMlpQuZNm3auAAUFBRw+fJlWl/dy9SCaqwGIBIyJGBTUwemWqzy/mAIRPmaEUGsJeNbz+IVfJ+ioiI2bNgwbi80NTUxJWciV47/GM9Lwwg4CA6CSblbBqYYRPjqEACRR8JaVcRPkPHlJ5m66kX27W8kL2/6uMPR3t7Ox+++yQcXjmLEIEYQA8YIkuIHSYVDkBnDk3DSEDwAi5c5mUfWNtGVPovc3FwOHTp0XwDZ2dm0nTvH9Td+zSedVxDVkIQAEQ1BoIgKCpnmflqpQcAXyjYxo6KeVatWUVZWRiKRGPO1+fPns2vXLjoOr7uvFA8HcHMoQ8IHmkqOINnH1d81kJeXR0VFRcqKkUcQBLS0tHD79u2QXHq7UmkIqgKqoIKKAnQPNiSqXFG0QFVCXbcGK4pVIdnTBcDOnTupqqoa06q2tjZKS0uZ8LmZzKiox5nwWXzfx9qBfmGgCkDRa4MeUNE3repg2QSEiwMFk5nDF8vrWLZsGTNnzqS9vX1UAEVFRezYsYOeD68y8fNPEFifAL2rDAfBnJdhGv0NzzgtoYYbHGOICkSMIWKEqBE8x+X91v18cKGJyspKDh48SFZW1ohAlixZQstfLzM99iK9iQQJqySsxVfFDyz9Nolv/fw7gumsPtIbMZE0zxhcR3DFEDVCZIDTjeA5Drb3Jv84sYOu639j69atNDQ0jAgiN3cyPQ/NJXvhM/QnEwRW8dWSDAL6bbLTHlyee0cVWNWfBhpgVbEWfFUSqiSGqVoyCCCaxayndjKn+nm2736BzIyJHDt27B4AFy9eovvtU3R3nA5DkFJEXwNUtWHEptSsPtIXNW7UMy4mJSLeMA+4IrhCKC6A46XR+VYz772xj/z8fJqampg1a9bg906ePElZWRlZy3+DZuSGPUGQ/G/QuDznHjVMeaEyaS2+WqxVbMryxMDVKv0W+qzSr0pPoo/Mx8uZs/51rgdTmD17NrFYbJArFi9ezKZNm7h1dD1B4JO0PgG23KR6QxnlYLHXM846z7i4oX4P6vmA9Q6ENMsQZyiGxK1OPjr5M5Kd77B7925qamoAWLBgAX+59jFU7tmivy3fPvq5INXDSyx+3DXOd1xx8YzBiGBMKCIDwmKMDLEWEnoMUDdK37U2bp/6BQ9PSueV+BEWLVpEdnYW3be6f67wo7EOJoMgiMX3uuKs84zBEQcjghjBMCAmhF1niskGCMaiqFWs8ehrj+Off5nCwkK2b99OcXExwFTgvdEB3AmizIi85oqTNgDCSKrPFWV4DFRD/beqWLX4YUXdst0ffk+b168CVqZWpwN9YwO4Wzhi8c1GpM6ISTcYREJPMOSAQYZLHc1upY5meyjfBq/XAUwGbgL9Y4dgrBGLFwtSITAPkekCk1L73wS9qsoFxR6nceWfx/O5/wGLCSMJ+zJrfwAAAABJRU5ErkJggg=="
                        alt="" />
                    ZAP Scanning Report
                </h1>
                <p />
                

                <h2>
                    
                    
                    Sites: {url}
                </h2>

                <h3>
                    Generated on {datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")} UTC
                </h3>

                
                    <h3 class="left-header">Summary of Alerts</h3>
                    <table class="summary">
                        <tr>
                            <th width="45%"
                                height="24">Risk Level</th>
                            <th width="55%"
                                align="center">Number of Alerts</th>
                        </tr>
                        <tr>
                            <td class="risk-3">
                                <div>High</div>
                            </td>
                            <td align="center">
                                <div>{risk_levels['High']['count']}</div>
                            </td>
                        </tr>
                        <tr>
                            <td class="risk-2">
                                <div>Medium</div>
                            </td>
                            <td align="center">
                                <div>{risk_levels['Medium']['count']}</div>
                            </td>
                        </tr>
                        <tr>
                            <td class="risk-1">
                                <div>Low</div>
                            </td>
                            <td align="center">
                                <div>{risk_levels['Low']['count']}</div>
                            </td>
                        </tr>
                        <tr>
                            <td class="risk-0">
                                <div>Informational</div>
                            </td>
                            <td align="center">
                                <div>{risk_levels['Informational']['count']}</div>
                            </td>
                        </tr>
                        <tr>
                            <td class="risk--1">
                                <div>				False Positives:</div>
                            </td>
                            <td align="center">
                                <div>{risk_levels['False Positives:']['count']}</div>
                            </td>
                        </tr>
                    </table>
                    <div class="spacer-lg"></div>
                

                
                    <h3>Alerts</h3>
                    <table class="alerts">
                        <tr>
                            <th width="60%" height="24">Name</th>
                            <th width="20%"
                                align="center">Risk Level</th>
                            <th width="20%"
                                align="center">Number of Instances</th>
                        </tr>
                        {alerts_html}
                        
                    </table>
                    <div class="spacer-lg"></div>
                

                    <h3>Alert Detail</h3>
                    {alert_details_html}
            </body>
            </html>

        '''
        with open(f'{scan_type}.html', 'w') as f:
            f.write(html_str)

class OWASP(Common):
    risk_levels = {
        'High': {'class':'risk-3', 'count':0},
        'Medium': {'class':'risk-2', 'count':0},
        'Low': {'class':'risk-1', 'count':0},
        'Informational': {'class':'risk-0', 'count':0},
        'False Positives:': {'class':'risk--1', 'count':0},
    }

    def set_domain(self, url):
        domain = ".".join(list(extract(url))).strip(".")
        self.http_url = f"http://{domain}"
        self.https_url = f"https://{domain}"
        self.url = url
        
        if not ('http://' in url or 'https://' in url):
            self.url = self.http_url
    
    def create_custom_alert_obj(**alert_obj):
        custom_alert_obj = {
            "name": alert_obj.get("name"),
            "description": alert_obj.get("description"),
            "urls": [
                {
                    "url": alert_obj.get("url"),
                    "method": alert_obj.get("method"),
                    "parameter": alert_obj.get("param"),
                    "attack": alert_obj.get("attack"),
                    "evidence": alert_obj.get("evidence"),
                }
            ],
            "instances": 1,
            "wascid": (
                alert_obj.get("wascid") if alert_obj.get("wascid") != "-1" else ""
            ),
            "cweid": alert_obj.get("cweid") if alert_obj.get("cweid") != "-1" else "",
            "plugin_id": alert_obj.get("pluginId"),
            "reference": "<br>".join(alert_obj.get("reference").split("\n")),
            "solution": alert_obj.get("solution"),
            "risk": alert_obj.get("risk"),
        }
        return custom_alert_obj
        

    def create_alerts_response(self, alerts_ids):
        """
        The function `create_alerts_response` takes a list of alert IDs, retrieves information about each
        alert, and returns a dictionary containing custom alert objects grouped by alert title.
        
        :param alerts_ids: The `alerts_ids` parameter is a list of alert IDs. These IDs are used to retrieve
        information about specific alerts from the ZAP (Zed Attack Proxy) core
        :return: The function `create_alerts_response` returns a dictionary object `alerts_objs` which
        contains information about the alerts.
        """
        alerts_objs = {}
        for alert_id in alerts_ids:
            alert_obj = zap.core.alert(id=alert_id)
            if isinstance(alert_obj,dict):
                alert_title = alert_obj.get('name')
                custom_alert_obj = self.create_custom_alert_obj(**alert_obj)

                if alert_title and alerts_objs.get(alert_title):
                    custom_alert_obj['urls'] = [*alerts_objs[alert_title]['urls'], *custom_alert_obj['urls']]
                    custom_alert_obj['instances'] = alerts_objs[alert_title]['instances']+1
                else:
                    self.risk_levels[custom_alert_obj['risk']]['count'] += 1
                
                alerts_objs[alert_title] = custom_alert_obj
            zap.alert.delete_alert(alert_id)
        return alerts_objs


    def spider_scan(self, url, html_report=False):
        
        self.set_domain(url)

        # scan url with spider tool of OWASP ZAP fro quick scan
        spider_scan_id = zap.spider.scan(url=url)
        
        # Here we are checking if spider scan still in progress then current process is sleep for 1s until 100% is compelete
        while int(zap.spider.status(spider_scan_id)) < 100:
            super().clear_scr()
            print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
            time.sleep(1)

        super().clear_scr()
        print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
        
        #Get full result of spider scan 
        full_results = pd.DataFrame(data=zap.spider.full_results(scanid=spider_scan_id))

        # Getting all the objects of urlsInScope and urlsIoError of spider scan
        spider_requests = pd.DataFrame(data=[*full_results.loc[full_results.index[0]]['urlsInScope'], *full_results.loc[full_results.index[2]]['urlsIoError']])

        # Getting message ids from urlsInScope and urlsIoError of spider scan
        spider_msg_ids = spider_requests['messageId'].to_list()
        
        # Make main thread to 10 seconds sleep to owasp update it's cache
        time.sleep(10)

        # Getting all the alerts of url with http and https
        alerts = pd.DataFrame(data=[*zap.alert.alerts(baseurl=self.http_url), *zap.alert.alerts(baseurl=self.https_url)])

        # Spider scan alerts ids
        print(alerts,"=>>>Alerts")
        print(spider_msg_ids,"=>>>Spider Msg IDS")
        if not alerts.empty:
            spider_alerts_ids = alerts[alerts['messageId'].isin(spider_msg_ids)]['id'].tolist()
        else:
            spider_alerts_ids = []

        alerts_objs = {}
        if len(spider_requests) and len(spider_alerts_ids):
            # Getting all the alert based on alerts ids
            alerts_objs = self.create_alerts_response(spider_alerts_ids)
        
        # Remove spider scan
        zap.spider.remove_scan(scanid=spider_scan_id)

        if html_report:
            super().set_html_report(url=self.url, risk_levels=self.risk_levels, alerts=alerts_objs, scan_type="spider")
            print("Html report is created with name spider.html")
        else:
            return json.dumps({'alerts': alerts_objs})

    def active_scan(self, url, html_report=False):
        self.set_domain(url)

        scan_id = zap.ascan.scan(url)

        # Start Spider scan
        spider_scan_id = zap.spider.scan(url)

        # Waiting to complete spider scan
        while int(zap.spider.status(spider_scan_id)) < 100:
            super().clear_scr()
            print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
            time.sleep(1)
        
        super().clear_scr()
        print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))

        #Get full result of spider scan 
        full_results = pd.DataFrame(data=zap.spider.full_results(scanid=spider_scan_id))

        # Getting all the objects of urlsInScope and urlsIoError of spider scan
        spider_requests = pd.DataFrame(data=[*full_results.loc[full_results.index[0]]['urlsInScope'], *full_results.loc[full_results.index[2]]['urlsIoError']])

        # Getting message ids from urlsInScope and urlsIoError of spider scan
        spider_msg_ids = spider_requests['messageId'].to_list()
        
        # Start Active scan
        active_scan_id = zap.ascan.scan(url)

        # Waiting to complete active scan
        while int(zap.ascan.status(scanid=scan_id)) < 100:
            super().clear_scr()
            print('Active scan progress %: {} for scan id {} with url {}'.format(zap.ascan.status(scanid=active_scan_id), active_scan_id, url))
            time.sleep(1)
        
        super().clear_scr()
        print('Active scan progress %: {} for scan id {} with url {}'.format(zap.ascan.status(scanid=active_scan_id), active_scan_id, url))

        # Getting all the alerts of url with http and https
        alerts = pd.DataFrame(data=[*zap.alert.alerts(baseurl=self.http_url), *zap.alert.alerts(baseurl=self.https_url)])

        # Spider scan alerts ids
        print(alerts,"=>>>Alerts")
        print(spider_msg_ids,"=>>>Spider Msg IDS")
        if not alerts.empty:
            spider_alerts_ids = alerts[alerts['messageId'].isin(spider_msg_ids)]['id'].tolist()
        else:
            spider_alerts_ids = []

        # Active scan's alerts ids 
        active_alerts_ids = zap.ascan.alerts_ids(scanid=active_scan_id)


        # Getting all the alert based on alerts ids
        alerts_objs = {}
        alerts_objs = self.create_alerts_response([*spider_alerts_ids, *active_alerts_ids])

        # Remove scan cache  
        zap.spider.remove_scan(scanid=spider_scan_id)
        zap.ascan.remove_scan(scanid=active_scan_id)

        if html_report:
            super().set_html_report(url=self.url, risk_levels=self.risk_levels, alerts=alerts_objs, scan_type="active")
            print("Html report is created with name active.html")
        else:
            return json.dumps({'alerts': alerts_objs})


def main():
    parser = argparse.ArgumentParser(description="OWASP Scan Argument Parser")
    parser.add_argument('--scan_type', type=str, choices=['active', 'spider'], help='Specify the scan type (active or spider)')
    parser.add_argument('--html_report', type=str, choices=['true', 'false'], help='Specify whether to generate an HTML report (true or false)')
    parser.add_argument('--url', type=str, help='Specify the URL to scan')
    args = parser.parse_args()
    scan_type = args.scan_type
    generate_html_report = args.html_report
    url = args.url

    owasp  = OWASP()
    if scan_type == 'active':
        if generate_html_report == 'false':
            print(owasp.active_scan(url=url))
        else:
            owasp.active_scan(url=url, html_report=True)
    elif scan_type == 'spider':
        if generate_html_report == 'false':
            print(owasp.spider_scan(url=url))
        else:
            owasp.spider_scan(url=url, html_report=True)

if __name__ == "__main__":
    main()