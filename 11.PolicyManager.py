#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
import re
import csv
import os
from datetime import datetime
from datetime import timedelta
import time
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('11.PolicyManager')

page_title = config_vars.get('page_title')
csv_report_file_path = config_vars.get('csv_report_file_path')
all_policies_file_path = config_vars.get('all_policies_file_path')
policies_output_html_file_path = config_vars.get('output_html_file')
policies_output_csv_file_path = config_vars.get('output_csv_file')
calendar_policy_file = config_vars.get('calendar_policy_file')
policy_calendar_html_dir = config_vars.get('policy_calendar_html_dir')

app_logger = LoggingManager('11.PolicyManager.py')
timetorun_file = config_vars.get('timetorun_file')
dformat = '%Y-%m-%d %H:%M:%S'

class FileHandler:
    def __init__(self):
        pass

    @staticmethod
    def read_lines(allpolicies_file_path):
        contents = []
        with open(allpolicies_file_path,'r') as f:
            contents = f.readlines()

        return contents

    @staticmethod
    def read_calendar_policies(calendar_policy_file):
        contents = []
        with open(calendar_policy_file,'r') as cf:
            contents = cf.readlines()

        return contents

class PolicyCSVParser:

    @staticmethod
    def parse_policy():
        policies = []
        with open(all_policies_file_path,'r') as f:
            policies = f.readlines()
        return policies

    @staticmethod
    def parse_window_sequence(windows_val):
        windows_val_split = windows_val.split()
        windows = []
        a_window = []
        for i,value in enumerate(windows_val_split):
            a_window += [value]
            if (i + 1) % 5 == 0:
                windows += [a_window]
                a_window = []
        windows = [' '.join(win) for win in windows]
        return windows

    @staticmethod
    def parse_policy_data(policy,output_csv=False):
        policy_split = policy.split(',')

        full_backup_windows = policy_split[4].strip()
        full_windows = PolicyCSVParser.parse_window_sequence(full_backup_windows)

        incr_backup_windows = policy_split[7].strip()
        incr_windows = PolicyCSVParser.parse_window_sequence(incr_backup_windows)
        if output_csv:
            csv_output_data = {
                'policy_name': policy_split[0].strip(),
                'server': policy_split[1].strip(),
                'backup_type': policy_split[2].strip(),
                'full_backup_title':policy_split[3].strip(),
                'full_windows': '<br>'.join(full_windows),
                'full_retention': policy_split[5].strip(),
                'incr_backup_title': policy_split[6].strip(),
                'incr_windows': '<br>'.join(incr_windows),
                'incr_retention': policy_split[8],
                'backup_selection': policy_split[9].strip(),
                'policy_active': policy_split[10].strip()
            }
            return csv_output_data
        else:
            server_names = policy_split[1].strip()
            servers_split = server_names.split()
            servers_split = [server.strip() for server in servers_split]
            server_names = '<br>'.join(servers_split)

            backup_selection = policy_split[9].strip()
            backup_selection_split = backup_selection.split()
            backup_selection_split = [bs.strip() for bs in backup_selection_split]
            backup_selection = '<br>'.join(backup_selection_split)

            html_output_data = {
                'policy_name': policy_split[0].strip(),
                'server' : server_names,
                'backup_type': policy_split[2].strip(),
                'full_backup_title':policy_split[3].strip(),
                'full_windows': '<br>'.join(full_windows),
                'full_retention': policy_split[5].strip(),
                'incr_backup_title': policy_split[6].strip(),
                'incr_windows': '<br>'.join(incr_windows),
                'incr_retention': policy_split[8],
                'backup_selection' : backup_selection,
                'policy_active': policy_split[10].strip()
            }
            return html_output_data

class PolicyManager:
    def __init__(self):
        pass

    def get_static_html_part_upper(self,page_title, csv_report_file_name):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')
        _timetorun = open(timetorun_file, 'r').readlines()[-1]

        html = """<!DOCTYPE html>"""
        html += """\n<html>\n    <head>\n    <meta charset="utf-8" />\n    <title>"""+page_title+"""</title>"""
        html += """\n    <link rel="stylesheet" type="text/css" href="css/view.css">\n    </head>\n    <body>"""
        html += """\n    <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
        html += """\n    <script type="text/javascript" src="js/wz_tooltip.js"></script>"""
        html += """\n    <table class="BackupTimeRun" align="right">"""
        html += """\n      <tbody>"""
        html += """\n        <tr>"""
        html += """\n          <td>Time to Run:<br>""" + _timetorun + """</td>"""
        html += """\n        </tr>"""
        html += """\n      </tbody>"""
        html += """\n    </table>"""
        html += """\n    <table class="BackupDataTime" align="right">"""
        html += """\n      <tbody>"""
        html += """\n        <tr>"""
        html += """\n          <td> Last Updated:<br>"""+str(timenow)+""" </td>"""
        html += """\n        </tr>"""
        html += """\n      </tbody>"""
        html += """\n    </table>"""
        html += """\n    <div id='logo'>\n        <header>\n            <div id='header'></div>\n            <div id='headerbar'></div>\n            <div>"""
        html += """\n                    <img src="img/version.png" alt="version logo" id="version"/>\n            </div>"""
        html += """\n        </header>\n                </div>\n                <nav>\n                    <ul id="menubar">"""
        html += """\n                        <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n                        <li><a href="./reports.html">Reports</a></li>"""
        html += """\n                        <li><a href="./policyconfig.html" class="selected">Policy Config</a></li>"""
        html += """\n                        <li><a href="./backupsize.html">Backup Size</a></li>"""
        html += """\n                        <li><a href="./catalog.html">Catalog</a></li>"""
        html += """\n                        <li><a href="./backupwritetime.html">Bck Write Time</a></li>"""
        html += """\n                        <li><a href="./billing.html">Billing</a></li>"""
        html += """\n                        <li><a href="./help.html">Help</a></li>"""
        html += """\n                    </ul>"""
        html += """\n                </nav>"""
        html += """\n    <div id='body'></div>"""
        html += """\n    <p>\n    <a href='""" + csv_report_file_name + """' style="text-decoration: underline; float: right";>csv download</a>\n    </p>"""

        return html

    def generate_html_data_table(self,policies):
        data_table = """<table class="BackupData2">\n<tbody>"""

        data_table += """<tr>\n<td class="polconfighead">Policy</td>\n<td class="polconfighead">Server</td>"""
        data_table += """\n<td class="polconfighead">Backup Type</td>"""
        data_table += """\n<td class="polconfighead">Full Backup Type</td>\n<td class="polconfighead">Full Backup Windows</td>"""
        data_table += """\n<td class="polconfighead">Full Retention</td>\n<td class="polconfighead">Incr Backup Type</td>"""
        data_table += """\n<td class="polconfighead">Incr Backup Windows</td>\n<td class="polconfighead">Incr Retention</td>"""
        data_table += """\n<td class="polconfighead">Backup Selection</td>\n<td class="polconfighead">Policy Active</td>\n<td class="polconfighead">Calendar</td>\n</tr>"""

        calendar_policies = FileHandler.read_calendar_policies(calendar_policy_file)
        calendar_policy_dict = {}

        for i, line in enumerate(calendar_policies):
            line = line.replace('\n','')
            line_split = line.split(',')
            policy_name = line_split[0].strip()
            policy_calendar_status = line_split[1].strip()
            policy_cal_status = 'no' if policy_calendar_status == 'NotCalendar' else 'yes'
            calendar_policy_dict[policy_name] = policy_cal_status

        for i,a_policy in enumerate(policies):
            policy_data = PolicyCSVParser.parse_policy_data(a_policy)
            class_name = """polconfig1"""
            if (i + 1) % 2 == 0:
                class_name = """polconfig2"""

            calendar_data = """<a><img src="img/notvalid.png"/></a>"""
            plcyname = a_policy.split(',')
            plcyname = plcyname[0].strip()
            policy_cstatus = calendar_policy_dict.get(plcyname)
            if policy_cstatus:
                if policy_cstatus == 'yes':
                    policy_calendar_file_name = plcyname+'-calendar.html'
                    pc_file_path = policy_calendar_html_dir + policy_calendar_file_name
                    calendar_data = """<a href=\"""" + pc_file_path + """\"><img src="img/calendar.png"/></a>"""
                else:
                    calendar_data = """<a><img src="img/calendar_disable.png"/></a>"""

            if policy_data['policy_active'].lower().strip() == 'no':
                class_name = """polconfig3"""

            row = """\n<tr>"""
            row += """\n<td class="%s">""" % class_name + policy_data['policy_name'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['server'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['backup_type'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['full_backup_title'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['full_windows'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['full_retention'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['incr_backup_title'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['incr_windows'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['incr_retention'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['backup_selection'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + policy_data['policy_active'] + """</td>"""
            row += """\n<td class="%s">""" % class_name + calendar_data + """</td>"""
            row += """\n</tr>"""

            data_table += row

        data_table += """\n</tbody>\n</table>"""
        return data_table

    def read_static_html_part_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n    <p>\n    </p>"""
        html += """\n    <p>\n    </p>"""
        html += """\n    <p>"""+str(timenow)+"""\n    </p>"""
        html += """\n    </body>\n</html>"""
        return html

    def generate_html(self,policies):
        html = self.get_static_html_part_upper(page_title,csv_report_file_path)
        html += self.generate_html_data_table(policies)
        html += self.read_static_html_part_lower()

        return html


    def run(self):
        policies = PolicyCSVParser.parse_policy()

        html_page = self.generate_html(policies)
        dt = datetime.now()

        print '%s INFO 11.PolicyManager.py  Output is saving to: %s' % (dt.strftime(dformat), policies_output_html_file_path)
        app_logger.log_info('Output is saving to: %s' % policies_output_html_file_path)

        with open(policies_output_html_file_path,'w') as f:
            f.write(html_page)

        dt = datetime.now()
        print '%s INFO 11.PolicyManager.py  Output is saved.' % dt.strftime(dformat)
        app_logger.log_info('Output is saved.')

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def run_main():
    dt = datetime.now()
    if not page_title:
        print '%s WARNING 11.PolicyManager.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set!')

    if not os.path.isfile(all_policies_file_path):
        print '%s ERROR 11.PolicyManager.py  %s is not a valid file.' % (dt.strftime(dformat), all_policies_file_path)
        app_logger.log_error('%s is not a valid file.' % all_policies_file_path)
        print '%s INFO 11.PolicyManager.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(calendar_policy_file):
        print '%s ERROR 11.PolicyManager.py  %s is not a valid file.' % (dt.strftime(dformat), calendar_policy_file)
        app_logger.log_error('%s is not a valid file.' % calendar_policy_file)
        print '%s INFO 11.PolicyManager.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    policy_manager = PolicyManager()
    policy_manager.run()

if __name__ == "__main__":
    dt = datetime.now()
    print '%s INFO 11.PolicyManager.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 11.PolicyManager.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 11.PolicyManager.py  Script didn\'t complete successfully' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 11.PolicyManager.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 11.PolicyManager.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
