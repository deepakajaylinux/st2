import subprocess

from st2common import log as logging
from st2common.models.api.actionrunner import ActionTypeAPI
from st2common.persistence.actionrunner import ActionType


LOG = logging.getLogger(__name__)


class RunnerContainer():

#    _actiontypes = {}

    def __init__(self):
        LOG.info('Action RunnerContainer instantiated.')
#        LOG.info('Populating Action RunnerContainer with ActionTypes.')
#        actiontype_apis = [ActionTypeAPI.from_model(actiontype_db)
#                           for actiontype_db in ActionType.get_all()]
#
#        for at_api in actiontype_apis:
#            if at_api.enabled:
#                self._actiontypes[at_api.name] = at_api
        

    def dispatch(self, runner_type, runner_parameters, action_parameters, result_data):
        LOG.debug('runner_type: %s', runner_type)
        LOG.debug('runner_parameters: %s', runner_parameters)
        LOG.debug('action_parameters: %s', action_parameters)
        LOG.debug('result_data: %s', result_data)

        if runner_type == 'internaldummy':
            self._handle_internaldummy_runner(runner_parameters, action_parameters, result_data)
        else:
            raise NotImplementedError('RunnerType "%s" not currently supported.' % runner_type)


    def _handle_internaldummy_runner(self, runner_parameters, action_parameters, result_data):
        """
            ActionRunner for "internaldummy" ActionType.

            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            !!!!!!!    This is for internal scaffolding use only.    !!!!!!!
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        """
        LOG.info('Entering Internal Dummy Runner')

        command_list = runner_parameters['command']
        LOG.debug('    [Internal Dummy Runner] command list is: %s', command_list)
        
        LOG.debug('    [Internal Dummy Runner] Launching command as blocking operation.')
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)

        command_stdout, command_stderr = process.communicate()
        command_exitcode = process.returncode

        LOG.debug('    [Internal Dummy Runner] command_stdout: %s', command_stdout)
        LOG.debug('    [Internal Dummy Runner] command_stderr: %s', command_stderr)
        LOG.debug('    [Internal Dummy Runner] command_exit: %s', command_exitcode)
        LOG.debug('    [Internal Dummy Runner] TODO: Save output to DB')
        
def get_runner_container():
    return RunnerContainer()