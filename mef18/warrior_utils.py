
import os
import json
import subprocess
import sys
import threading
import time
from utils.navigator_util import Navigator
from django.template.loader import render_to_string


class WarriorAdaptor:
    STATUS_IDLE = 'IDLE'
    STATUS_RUNNING_WAKEUP = 'WAKEUP'
    STATUS_RUNNING_NAPTIME = 'NAPTIME'

    def __init__(self):
        self.PYTHON_EXE = sys.executable
        self.WARRIOR_DIR = Navigator().get_warrior_dir()
        self.PLUGINSPACE_DIR = os.path.join(self.WARRIOR_DIR, "plugins", "mef18_plugin", "pluginspace")
        self.PLUGINSPACE_WDF_DIR = os.path.join(self.PLUGINSPACE_DIR, "data")
        self.PLUGINSPACE_TC_DIR = os.path.join(self.PLUGINSPACE_DIR, "testcases")
        self.PLUGINSPACE_TD_VC_DIR = os.path.join(self.PLUGINSPACE_DIR, "config_files")
        self.WARRIOR_EXE = os.path.join(self.WARRIOR_DIR, 'Warrior')
        self.TEMPLATE_WDF = "xml_templates/WDF_mef18_template.xml"
        self.TEMPLATE_WDF_CPE = "xml_templates/WDF_mef18_cpe_template.xml"
        self.TEMPLATE_VC = "xml_templates/VC_mef18_template.xml"
        self.FILENAME_WDF = "WDF_mef18.xml"
        self.FILENAME_WDF_CPE = "WDF_mef18_cpe.xml"
        self.FILENAME_TC_WAKEUP = "TC_mef18_tru_wakeup.xml"
        self.FILENAME_TC_WAKEUP_CPE = "TC_mef18_cpe_wakeup.xml"
        self.FILENAME_TC_NAPTIME = "TC_mef18_tru_naptime.xml"

        self._instance_lock = threading.RLock()
        self.status = self.STATUS_IDLE

    def get_settings_file(self):
        txt = ""
        with open(os.path.join(self.PLUGINSPACE_WDF_DIR, self.FILENAME_WDF)) as fd:
            txt = txt + fd.read() + "\n"
        with open(os.path.join(self.PLUGINSPACE_WDF_DIR, self.FILENAME_WDF_CPE)) as fd:
            txt = txt + fd.read() + "\n"
        return txt

    def generate_system_data(self, target_tru_system, target_cpe_system, via_system):
        """
        Takes host data, device on which microservice is deployed,
        and generates Input Data File from a template
        """
        with self._instance_lock:
            data = {
                "target_system": {},
                "via_system": {}
            }
            data['target_system'].update(target_tru_system)
            data['via_system'].update(via_system)
            data = render_to_string(self.TEMPLATE_WDF, data)
            open(os.path.join(self.PLUGINSPACE_WDF_DIR, self.FILENAME_WDF), "w+").write(data)

            data = {
                "target_system": {},
                "via_system": {}
            }
            data['target_system'].update(target_cpe_system)
            data['via_system'].update(via_system)
            data = render_to_string(self.TEMPLATE_WDF_CPE, data)
            open(os.path.join(self.PLUGINSPACE_WDF_DIR, self.FILENAME_WDF_CPE), "w+").write(data)
        return

    def _run(self, tc_file):
        with self._instance_lock:
            tc_file = os.path.join(self.PLUGINSPACE_TC_DIR, tc_file)
            warrior_cmd = '{0} {1} {2}'.format("python3", self.WARRIOR_EXE, tc_file)
            output = subprocess.Popen(str(warrior_cmd),
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)

            print_cmd = '{0} {1} {2}'.format("python3", self.WARRIOR_EXE, tc_file)

            first_poll = True

            file_li_string = "{0}".format(tc_file)

            file_list_html = "{0}".format(file_li_string)
            cmd_string = "Command: {0}".format(print_cmd)
            logs_heading = "Logs:"
            init_string = "Executing:{0}" \
                       .format(file_list_html) + cmd_string + logs_heading
            result = ""
            while output.poll() is None:
                line = output.stdout.readline()
                if first_poll:
                    line = init_string + line
                    first_poll = False
                    # Yield this line to be used by streaming http response
                print(line)
                result = result + line
                if line.startswith('-I- DONE'):
                    break
            return result

    def run_wakeup(self):
        with self._instance_lock:
            self.status = self.STATUS_RUNNING_WAKEUP
            result = self._run(self.FILENAME_TC_WAKEUP)
            time.sleep(3)
            result = self._run(self.FILENAME_TC_WAKEUP_CPE)
            self.status = self.STATUS_IDLE

    def run_naptime(self):
        with self._instance_lock:
            self.status = self.STATUS_RUNNING_NAPTIME
            result = self._run(self.FILENAME_TC_NAPTIME)
            self.status = self.STATUS_IDLE

    def trigger_wakeup(self):
        if self.status == self.STATUS_IDLE:
            t = threading.Thread(target=self.run_wakeup)
            t.start()

    def trigger_naptime(self):
        if self.status == self.STATUS_IDLE:
            t = threading.Thread(target=self.run_naptime)
            t.start()


if __name__  == "__main__":
    warrior = WarriorAdaptor()
    warrior.generate_system_data('100.0.0.200', 'localhost')