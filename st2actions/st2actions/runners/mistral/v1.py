# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

from oslo.config import cfg
from mistralclient.api import client as mistral

from st2common.constants.action import ACTIONEXEC_STATUS_RUNNING
from st2actions.runners import ActionRunner
from st2common import log as logging


LOG = logging.getLogger(__name__)


def get_runner():
    return MistralRunner(str(uuid.uuid4()))


class MistralRunner(ActionRunner):

    url = cfg.CONF.workflow.url

    def __init__(self, runner_id):
        super(MistralRunner, self).__init__(runner_id=runner_id)
        self._on_behalf_user = cfg.CONF.system_user.user

    def pre_run(self):
        pass

    def run(self, action_parameters):
        client = mistral.client(mistral_url='%s/v1' % self.url)

        # Update workbook definition.
        workbook_name = self.action.pack + '.' + self.action.name
        workbook = next((w for w in client.workbooks.list() if w.name == workbook_name), None)
        if not workbook:
            client.workbooks.create(workbook_name, description=self.action.description)
        workbook_file = self.entry_point
        with open(workbook_file, 'r') as workbook_spec:
            definition = workbook_spec.read()
            try:
                old_definition = client.workbooks.get_definition(workbook_name)
            except:
                old_definition = None
            if definition != old_definition:
                client.workbooks.upload_definition(workbook_name, definition)

        # Setup context for the workflow execution.
        context = self.runner_parameters.get('context', dict())
        endpoint = 'http://%s:%s/v1/actionexecutions' % (cfg.CONF.api.host, cfg.CONF.api.port)
        context['st2_api_url'] = endpoint
        context['st2_parent'] = self.action_execution_id
        context.update(action_parameters)

        # Execute the workflow.
        execution = client.executions.create(self.runner_parameters.get('workbook'),
                                             self.runner_parameters.get('task'),
                                             context=context)

        # Return status and output.
        output = {
            'id': str(execution.id),
            'state': str(execution.state)
        }

        self.container_service.report_status(ACTIONEXEC_STATUS_RUNNING)
        self.container_service.report_result(output)

        return (str(execution.state) == 'RUNNING')
