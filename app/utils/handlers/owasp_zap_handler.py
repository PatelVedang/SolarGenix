from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import *
import json
import asyncio

class OWASP:
    result = {}
    
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
        This function contains a dictionary of handlers for different tool commands and executes the
        appropriate handler based on the input.
        """
        handlers = {
            'owasp_zap': [
                self.zap_handler,
            ],
            'active_owasp': [
                self.zap_handler,
            ],
            'isaix_owasp': [
                self.zap_handler,
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

    async def zap_handler(self, target, regenerate):
        """
        The function `zap_handler` is an asynchronous function that handles alerts from OWASP ZAP tool
        and updates the `self.result` dictionary with the alert information.
        
        :param target: The `target` parameter is the target object that contains information about the
        target being scanned. It likely includes details such as the URL or IP address of the target
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether the
        target should be regenerated or not. It is used to determine if the target needs to be refreshed
        or if the existing target can be used
        """
        try:
            vul_data = await alert_response(**{**json.loads(target.raw_result),**{'tool': target.tool.tool_name, 'alert_type':5}})
            self.result = {**self.result, **vul_data}
        except Exception as e:
            import traceback
            traceback.print_exc()
            pass
    