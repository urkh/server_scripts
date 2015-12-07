#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import time
from datetime import datetime
import os
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('17.BackupWriteTime2HTML')

default_page_title = config_vars.get('default_page_title')
#dashboard_files_dir = config_vars.get('dashboard_files_dir')
timetorun_file = config_vars.get('timetorun_file')
default_html_output_file_path = config_vars.get('default_html_output_file_path')

app_logger = LoggingManager('17.BackupWriteTime2HTML.py')

backupwrite_file = config_vars.get('backupwritetime_file')
dformat = '%Y-%m-%d %H:%M:%S'

class MainIndex:
    def __init__(self):
        pass

    def get_static_html_page_upper(self,page_title):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')
        _timetorun = open(timetorun_file, 'r').readlines()[-1]

        html = """<!DOCTYPE html>\n<html>"""
        html += """\n   <head>"""
        html += """\n       <meta charset="utf-8" />"""
        html += """\n           <title>""" + page_title + """</title>"""
        html += """\n           <link rel="stylesheet" type="text/css" href="css/view.css">"""
        html += """\n   </head>"""
        html += """\n   <body>"""
        html += """\n       <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
        html += """\n       <header>"""
        html += """\n           <table class="BackupDataTime" align="right">"""
        html += """\n               <tbody>"""
        html += """\n                   <tr>"""
        html += """\n                       <td> Last Updated:<br>""" + str(timenow) + """</td>"""
        html += """\n                       <td> Last Updated:<br>""" + _timetorun + """</td>"""
        html += """\n                   </tr>"""
        html += """\n               </tbody>"""
        html += """\n           </table>"""
        html += """\n           <nav>"""
        html += """\n               <div id='header'></div>\n           <div id='headerbar'></div>"""
        html += """\n               <div>"""
        html += """\n                   <img src="img/version.png" alt="version logo" id="version"/>"""
        html += """\n               </div>"""
        html += """\n               <ul id="menubar">"""
        html += """\n                   <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n                   <li><a href="./reports.html">Reports</a></li>"""
        html += """\n                   <li><a href="./policyconfig.html">Policy Config</a></li>"""
        html += """\n                   <li><a href="./backupsize.html">Backup Size</a></li>"""
        html += """\n                   <li><a href="./catalog.html">Catalog</a></li>"""
        html += """\n                   <li><a href="./backupwritetime.html" class="selected">Bck Write Time</a></li>"""
        html += """\n                   <li><a href="./billing.html">Billing</a></li>"""
        html += """\n                   <li><a href="./help.html">Help</a></li>"""
        html += """\n               </ul>"""
        html += """\n           </nav>"""
        html += """\n        </header>"""
        html += """\n       <div id='body'></div>"""
        html += """\n           <a href='reports/backupwritetime.csv' style="text-decoration: underline; float: right";>csv download</a></p>"""
        return html

    def generate_data_table_one(self):
        html_data_table = """"""
        html_data_table += """\n       <table class="BackupDataWriteTime1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Backup Write Time last 24 Hours</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Recommended to move the following backup to Disks</td>"""        
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n        <table class="BackupDataWriteTime2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Policy</td>"""
        html_data_table += """\n                    <td class="polconfighead">Client</td>"""
        html_data_table += """\n                    <td class="polconfighead">Media ID</td>"""
        html_data_table += """\n                    <td class="polconfighead">Image Write Start Time</td>"""
        html_data_table += """\n                    <td class="polconfighead">Elapse Time in Second</td>"""
        html_data_table += """\n                    <td class="polconfighead">Image Write End Time</td>"""
        html_data_table += """\n                    <td class="polconfighead">Media Type</td>"""
        html_data_table += """\n                </tr>"""

        backupwrite_file_lines = open(backupwrite_file, 'r').readlines()
        #    backupwrite_file_lines = f.readlines()

        class_name = "polconfig1"
        for line in backupwrite_file_lines:
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            html_table_row = """\n              <tr>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[0].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[1].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[2].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[3].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[4].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[5].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[6].strip() + """</td>"""
            html_table_row += """\n              </tr>"""

            html_data_table += html_table_row

            if class_name == "polconfig1":
                class_name = "polconfig2"
            else:
                class_name = "polconfig1"

        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""

        return html_data_table

    def generate_data_tables(self):
        tables = """"""

        tables += self.generate_data_table_one()

        return tables

    def read_static_html_part_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n    <p>\n    </p>"""
        html += """\n    <p>\n    </p>"""
        html += """\n    <p>"""+str(timenow)+"""\n    </p>"""
        html += """\n    </body>\n</html>"""
        return html

    def generate_html_page(self):
        html = """"""
        html += self.get_static_html_page_upper(default_page_title)
        html += self.generate_data_tables()
        html += self.read_static_html_part_lower()
        return html

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def run_main():
    dt = datetime.now()
    if not default_page_title:
        print '%s WARNING 17.BackupWriteTime2HTML.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set!')

    #dashboard_backup_client_file_path = os.path.join(dashboard_files_dir,backupwrite_file)
    if not os.path.isfile(backupwrite_file):
        print '%s ERROR 17.BackupWriteTime2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), backupwrite_file)
        app_logger.log_error('%s is not a valid file.' % backupwrite_file)
        print '%s INFO 17.BackupWriteTime2HTML.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return
        

    main_index_obj = MainIndex()
    html = main_index_obj.generate_html_page()

    print '%s INFO 17.BackupWriteTime2HTML.py  Output is saving to: %s' % (dt.strftime(dformat), default_html_output_file_path)
    app_logger.log_info('Output is saving to: %s' % default_html_output_file_path)

    with open(default_html_output_file_path,'w') as f:
        f.write(html)

    dt = datetime.now()
    print '%s INFO 17.BackupWriteTime2HTML.py  Output Saved!' % dt.strftime(dformat)
    app_logger.log_info('Output Saved!')


if __name__ == "__main__":
    dt = datetime.now()
    print '%s INFO 17.BackupWriteTime2HTML.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 17.BackupWriteTime2HTML.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 17.BackupWriteTime2HTML.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 17.BackupWriteTime2HTML.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 17.BackupWriteTime2HTML.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
