from scanner.models import *
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import *
import asyncio

class OpenVAS:
    result = {}
    issue_regex = r"Issue\n-----\n(.*?)(?=\n\n\n|\Z)"
    title_regex = r"NVT: (?P<title>.*?)\n"
    cvvs_regex = r"Threat: (?P<complexity>\w+) \(CVSS: (?P<cvvs>(\d+\.\d+))\)"
    description_regex = r"Summary:\s*(?P<description>.*?)\n\n"
    solution_regex = r"Solution:\s*(?P<solution>.*?)\n\n"
    evidence_regex = r"Vulnerability Detection Result:\s*(?P<evidence>.*?)\n\n"
    reference_regex = r"References:\n(?P<reference>.*?)$"

    async def handlers(self, tool_cmd, handlers, target, regenerate):
        """
        The function "handlers" takes in a tool command, a dictionary of handlers, a target, and a
        boolean flag, and creates a list of jobs to be executed concurrently using asyncio.
        
        :param tool_cmd: The `tool_cmd` parameter is a string that represents the command or tool being
        used. It is used to determine which handlers to execute for that specific command or tool
        :param handlers: The `handlers` parameter is a dictionary that contains the handlers for
        different tool commands. Each key in the dictionary represents a tool command, and the
        corresponding value is a list of handler functions for that command
        :param target: The "target" parameter is the target object or entity that the handlers will be
        applied to. It could be a website, a network, a file, or any other entity that the handlers are
        designed to work on
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether the
        target should be regenerated or not. It is used to determine whether the vulnerability handlers
        should regenerate any necessary files or data related to the target before executing their tasks
        """
        jobs = []
        for vul_handler in handlers[tool_cmd]:
            jobs.append(vul_handler(target, regenerate))
        await asyncio.gather(*jobs)

    def main(self, target, regenerate):
        """
        The main function handles different tool commands and either generates a new result or retrieves
        a previously stored result.
        
        :param target: The "target" parameter is an object that represents a target for a specific tool.
        It likely contains information such as the target's ID, name, and other relevant details
        :param regenerate: The `regenerate` parameter is a boolean flag that indicates whether the
        result should be regenerated or not. If `regenerate` is `True`, it means that the result needs
        to be regenerated. If `regenerate` is `False`, it means that the existing result can be used
        without regeneration
        :return: The code is returning the `self.result` variable.
        """
        handlers = {
            'openvas': [
                self.openvas_handler,
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or not target.compose_result:
                self.result = {}
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.handlers(tool_cmd, handlers, target, regenerate))
                loop.close()
                
                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    async def set_vul_data(self, issue_regex_obj, target):
        """
        The function `set_vul_data` extracts various fields from a given `issue_regex_obj` and uses them
        to create a `vul_data` dictionary, which is then merged with the existing `self.result`
        dictionary.
        
        :param issue_regex_obj: The `issue_regex_obj` parameter is a string that represents the issue or
        vulnerability that needs to be processed. It is expected to match a specific regex pattern
        :param target: The `target` parameter is an object that contains information about the target
        being scanned. It likely has properties such as `tool_name` which represents the name of the
        scanning tool being used
        """
        title_search = re.search(self.title_regex, issue_regex_obj)
        cvvs_search = re.search(self.cvvs_regex, issue_regex_obj)
        description_search = re.search(self.description_regex, issue_regex_obj, flags=re.DOTALL)
        solution_search = re.search(self.solution_regex, issue_regex_obj, flags=re.DOTALL)
        evidence_search = re.search(self.evidence_regex, issue_regex_obj, flags=re.DOTALL)
        reference_search = re.search(self.reference_regex, issue_regex_obj,flags=re.DOTALL)

        title=title_search.groupdict().get('title', '') if title_search else ''
        complexity=cvvs_search.groupdict().get('complexity', '') if cvvs_search else ''
        cvvs3_0=cvvs_search.groupdict().get('cvvs', '') if cvvs_search else ''
        description=description_search.groupdict().get('description', '') if description_search else ''
        solution=solution_search.groupdict().get('solution', '') if solution_search else ''
        evidence=evidence_search.groupdict().get('evidence', '') if evidence_search else ''
        reference=reference_search.groupdict().get('reference', '') if reference_search else ''

        vul_data = await alert_response(
            complexity=complexity.strip(),
            error=title.strip(),
            description=description.strip(),
            solution=solution.strip(),
            tool=target.tool.tool_name,
            alert_type=4,
            evidence=evidence.replace('<br/>', '\n').strip(),
            cvvs3={
                'base_score': cvvs3_0.strip(),
                'error_type': complexity.strip()
            },
            reference = reference.strip()
        )
        self.result = {**self.result, **vul_data}

    async def openvas_handler(self, target, regenerate):
        """
        The `openvas_handler` function extracts issues from a target's raw result and sets vulnerability
        data for each issue asynchronously.
        
        :param target: The "target" parameter is an object that represents the target for the OpenVAS
        scan. It likely contains information such as the IP address or hostname of the target, as well
        as any additional configuration or settings for the scan
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether the
        OpenVAS scan should be regenerated or not. If `regenerate` is `True`, it means that the scan
        should be regenerated before processing the results. If `regenerate` is `False`, it means that
        the existing scan
        """

        issues = re.findall(self.issue_regex, target.get_raw_result(), flags=re.DOTALL)
        if issues:
            jobs = []
            for match in issues:
                jobs.append(self.set_vul_data(match, target))
            await asyncio.gather(*jobs)
    