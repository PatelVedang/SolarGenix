from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re


class SSLYSE:
    result = ""
    service_regex = "\*(?P<service>[\w\s.]+):\n"
    # service_regex = "\*(?P<service>[\w\s.]+):\\r\\n"

    def sslyze_handler(self, target, regenerate):
        """
        It takes the raw result of the tool and then it searches for the regex pattern of the service
        and then it takes the content between the service and the next service and then it escapes the
        content and then it returns the result
        
        :param target: The target object that is being processed
        :param regenerate: If the user wants to regenerate the result, this parameter will be True
        :return: The result of the handler is being returned.
        """
        if regenerate or target.compose_result=="":
            self.result = f'''
                <div class="col-12 border border-1 border-dark">
                        <h2>{target.tool.tool_name.replace("-"," ").capitalize()}</h2>
                </div>'''
            services = list(re.finditer(self.service_regex, target.raw_result))
            for service_obj in services:
                index = services.index(service_obj)
                if index != len(services)-1:
                    regex = f"(?s)\\{service_obj.group()}(?P<content>.*?)\\{services[index+1].group()}"
                    regex.replace("\n","\\n").replace("\r","\\r")
                    self.result+= f'''
                    <div class="col-12">
                        <div class="row">
                            <div class="col-3 border border-1 border-dark">
                                <h5>{service_obj.groupdict().get('service')}</h5>
                            </div>
                            <div class="col-9 border border-1 border-dark d-flex">
                                <pre style="text-decoration:none;">
{escape(re.search(regex, target.raw_result).groupdict().get('content'))}
                                </pre>
                            </div>
                        </div>
                    </div>
                    '''
            if not services:
                self.result += f'''
                <div class="col-12 border border-1 border-dark">
                        <h3>Not Found Any Vulnerability Threat Level</h3>
                </div>'''
            Target.objects.filter(id=target.id).update(compose_result=self.result)
        else:
            self.result = target.compose_result
        return self.result
