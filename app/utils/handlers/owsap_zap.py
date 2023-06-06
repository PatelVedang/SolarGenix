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

class OWSAP:
    result = ""
    
    def main(self, target, regenerate):
        """
        This function contains a dictionary of handlers for different tool commands and executes the
        appropriate handler based on the input.
        """
        handlers = {
            'owsap_zap': [
                self.zap_handler,
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or target.compose_result=="":
                self.result = ""
                for vul_handler in handlers[tool_cmd]:
                    vul_handler(target, regenerate)
                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    def zap_handler(self, target, regenerate):
        try:
            self.result += set_zap_template(**{**json.loads(target.raw_result),**{'tool': 'OWSAP ZAP'}})
        except:
            import traceback
            traceback.print_exc()
            pass
    