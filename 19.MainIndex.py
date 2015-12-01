#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import time
from datetime import datetime
import os
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('19.MainIndex')

default_page_title = config_vars.get('default_page_title')
dashboard_files_dir = config_vars.get('dashboard_files_dir')
default_html_output_file_path = config_vars.get('default_html_output_file_path')

app_logger = LoggingManager('19.MainIndex.py')

# Policy Type
dashboard_policy_type = 'dashboard-policy-type.txt'

# Billing
dashboard_billing_file = 'dashboard-billing.txt'

# Open Actions
dashboard_liveview_file = 'dashboard-liveview.txt'
dashboard_historyview_file = 'dashboard-historyview.txt'
dashboard_monthly_view_file = 'dashboard-monthlyview.txt'
dashboard_weeklyview_file = 'dashboard-weeklyview.txt'
dashboard_backup_variance_file = 'dashboard-backupvariance.txt'
dashboard_notdefined_file = 'dashboard-notdefined.txt'

# Infrastructure Details
dashboard_policy_file = 'dashboard-policy.txt'
dashboard_uniqclient_file = 'dashboard-uniqclient.txt'
dashboard_backup_client_file = 'dashboard-backupclient.txt'
dashboard_backup_size_file = 'dashboard-backupsize.txt'
dashboard_catalog_file = 'dashboard-catalog.txt'
dashboard_backuptime_file = 'dashboard-backuptime.txt'

# Backup Issues
dashboard_backup_issue = 'dashboard-backupissue.txt'

# Backup Usage
dashboard_backup_usage = 'dashboard-backupusage.txt'
dformat = '%Y-%m-%d %H:%M:%S'

class MainIndex:
    def __init__(self):
        pass

    def get_static_html_page_upper(self,page_title):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

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
        html += """\n                   </tr>"""
        html += """\n               </tbody>"""
        html += """\n           </table>"""
        html += """\n           <nav>"""
        html += """\n               <div id='header'></div>\n           <div id='headerbar'></div>"""
        html += """\n               <div>"""
        html += """\n                   <img src="img/version.png" alt="version logo" id="version"/>"""
        html += """\n               </div>"""
        html += """\n               <ul id="menubar">"""
        html += """\n                   <li><a href="../index.html" class="selected">Main Index</a></li>"""
        html += """\n                   <li><a href="./liveview.html">Views</a></li>"""
        html += """\n                   <li><a href="./reports.html">Reports</a></li>"""
        html += """\n                   <li><a href="./help.html">Help</a></li>"""
        html += """\n               </ul>"""
        html += """\n           </nav>"""
        html += """\n        </header>"""
        html += """\n       <div id='body'></div>"""
        html += """\n       <table class="BackupDataDashboard">"""
        html += """\n            <tbody>"""
        html += """\n                <tr>"""
        html += """\n                    <td>DASHBOARD</td>"""
        html += """\n                </tr>"""
        html += """\n            </tbody>"""
        html += """\n        </table>"""
        return html

    def generate_data_table_tr(self,file_name,class_name,title,csv_report_file_name,graph_file_name):

        table_tr = """"""

        contents = []
        file_path = os.path.join(dashboard_files_dir,file_name)
        with open(file_path,'r') as f:
            contents = f.readlines()

        contents = [line.replace('\n','').strip() for line in contents]

        temp= []

        for c in contents:
            if c:
                temp += [c]

        contents = temp

        _datetime = None
        open_action_count = None
        if contents:
            last_line = contents[len(contents) - 1]
            last_line_split = last_line.split(',')

            try:
                _datetime = datetime.strptime(last_line_split[0].strip(),'%Y-%m-%d %H:%M:%S')
                open_action_count = int(last_line_split[1].replace('GB','').strip())
            except Exception,msg:
                _datetime = None
                open_action_count = None

        if _datetime and open_action_count is not None:

            formatted_date_str = _datetime.strftime('%a %Y-%m-%d %H:%M:%S')

            excel_img = "img/excel.png"
            chart_img = "img/linechart.png"

            if csv_report_file_name == "#":
                excel_img = "img/exceldisable.png"
            else:
                csv_report_file_name = "reports/"+csv_report_file_name

            if graph_file_name == "#":
                chart_img = "img/linechartdisable.png"
            else:
                graph_file_name = "graphs/"+graph_file_name

            table_tr += """\n              <tr>"""
            table_tr += """\n                    <td class=\"""" + class_name + """\">""" + formatted_date_str + """</td>"""
            table_tr += """\n                    <td class=\"""" + class_name + """\">""" + title + """</td>"""
            table_tr += """\n                    <td class=\"""" + class_name + """\">""" + str(open_action_count) + """</td>"""
            table_tr += """\n                    <td class=\"""" + class_name + """\"><a class href=\"""" + csv_report_file_name + """\"><img src=\"""" + excel_img + """\" alt="csv" /></a></td>"""
            #table_tr += """\n                    <td class=\"""" + class_name + """\"><a class href=\"""" + graph_file_name + """\"><img src=\"""" + chart_img + """\" alt="Graphs" /></a></td>"""
            table_tr += """\n               </tr>"""

        return table_tr

    def generate_data_table_one(self):


        html_data_table  = """\n       <table class="BackupDataOpenAction1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Open Actions</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n       <table class="BackupDataOpenAction2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Date / Time</td>"""
        html_data_table += """\n                    <td class="polconfighead">Description</td>"""
        html_data_table += """\n                    <td class="polconfighead">Open Actions</td>"""
        html_data_table += """\n                    <td class="polconfighead">Files Download</td>"""
        #html_data_table += """\n                    <td class="polconfighead">Graphs</td>"""
        html_data_table += """\n                 </tr>"""

        ###Liveview txt file.
        html_data_table += self.generate_data_table_tr(dashboard_liveview_file,'polconfig1','Issues to check in LiveView <a class href="./liveview.html"><img src="img/link.png" alt="link"></a>','dashboard-liveview.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_historyview_file,'polconfig2','Issues to check in HistoryView <a class href="./historyview.html"><img src="img/link.png" alt="link"></a>','dashboard-historyview.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_monthly_view_file,'polconfig1','Issues to check in MonthlyView <a class href="./monthlyview.html"><img src="img/link.png" alt="link"></a>','dashboard-monthlyview.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_weeklyview_file,'polconfig2','Issues to check in WeeklyView <a class href="./weeklyview.html"><img src="img/link.png" alt="link"></a>','dashboard-weeklyview.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_backup_variance_file,'polconfig1','Issues to check in Backup Variance <a class href="./backupsize.html"><img src="img/link.png" alt="link"></a>','dashboard-backupvariance.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_notdefined_file,'polconfig2','Customer Information Needed for Billing <a class href="./billing.html"><img src="img/link.png" alt="link"></a>','dashboard-notdefined.csv','#')
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""

        return html_data_table

    def generate_data_table_two(self):
        html_data_table = """"""
        html_data_table += """\n       <table class="BackupDataInfraDetails1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Infrastructure Details</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n        <table class="BackupDataInfraDetails2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Date / Time</td>"""
        html_data_table += """\n                    <td class="polconfighead">Description</td>"""
        html_data_table += """\n                    <td class="polconfighead">Numbers</td>"""
        html_data_table += """\n                    <td class="polconfighead">Files Download</td>"""
        #html_data_table += """\n                    <td class="polconfighead">Graphs</td>"""
        html_data_table += """\n                </tr>"""

        html_data_table += self.generate_data_table_tr(dashboard_policy_file,'polconfig1','Number of Policies <a class href="./policyconfig.html"><img src="img/link.png" alt="link"></a>','dashboard-policy.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_uniqclient_file,'polconfig2','Number of unique Clients <a class href="./policyconfig.html"><img src="img/link.png" alt="link"></a>','dashboard-uniqclient.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_backup_client_file,'polconfig1','Number of Backup Clients <a class href="./policyconfig.html"><img src="img/link.png" alt="link"></a>','dashboard-backupclient.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_backup_size_file,'polconfig2','Total Backup Size in KB <a class href="./backupsize.html"><img src="img/link.png" alt="link"></a>','dashboard-backupsize.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_catalog_file,'polconfig1','Total Catalog Entries Live <a class href="./catalog.html"><img src="img/link.png" alt="link"></a>','dashboard-catalog.csv','#')
        html_data_table += self.generate_data_table_tr(dashboard_backuptime_file,'polconfig2','Backup Write Time <a class href="./backupwritetime.html"><img src="img/link.png" alt="link"></a>','dashboard-backuptime.csv','#')
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""

        return html_data_table

    def generate_data_table_seven(self):


        html_data_table  = """\n       <table class="BackupDataBilling1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Billing</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n       <table class="BackupDataBilling2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Date / Time</td>"""
        html_data_table += """\n                    <td class="polconfighead">Description</td>"""
        html_data_table += """\n                    <td class="polconfighead">Open Actions</td>"""
        html_data_table += """\n                    <td class="polconfighead">Files Download</td>"""
        #html_data_table += """\n                    <td class="polconfighead">Graphs</td>"""
        html_data_table += """\n                </tr>"""

        ###dashboard txt file.
        html_data_table += self.generate_data_table_tr(dashboard_billing_file,'polconfig1','Backup Extra Usage to Bill <a class href="./billing.html"><img src="img/link.png" alt="link"></a>','dashboard-billing.csv','#')
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""

        return html_data_table


    def generate_data_table_three(self):
        html_data_table = """"""
        html_data_table += """\n       <table class="BackupDataTopIssue1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Top 20 Backup Issues (Monthly View)</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n        <table class="BackupDataTopIssue2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Policy</td>"""
        html_data_table += """\n                    <td class="polconfighead">Client</td>"""
        html_data_table += """\n                    <td class="polconfighead">KPI*</td>"""
        html_data_table += """\n                </tr>"""

        backup_issue_lines = []
        file_path = os.path.join(dashboard_files_dir,dashboard_backup_issue)
        with open(file_path,'r') as f:
            backup_issue_lines = f.readlines()

        class_name = "polconfig1"
        for line in backup_issue_lines:
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            html_table_row = """\n              <tr>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[0].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[1].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[2].strip() + """</td>"""
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


    def generate_data_table_four(self):
        html_data_table = """"""
        html_data_table += """\n       <table class="BackupDataTopUsage1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Top 20 Backup Usage (All Not Expired Backup)</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n        <table class="BackupDataTopUsage2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Policy</td>"""
        html_data_table += """\n                    <td class="polconfighead">Client</td>"""
        html_data_table += """\n                    <td class="polconfighead">Backup Size</td>"""
        html_data_table += """\n                </tr>"""

        backup_usage_lines = []
        file_path = os.path.join(dashboard_files_dir,dashboard_backup_usage)
        with open(file_path,'r') as f:
            backup_usage_lines = f.readlines()

        class_name = "polconfig1"
        for line in backup_usage_lines:
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            html_table_row = """\n              <tr>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[0].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[1].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[2].strip() + """</td>"""
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


    def generate_data_table_five(self):
        html_data_table = """"""
        html_data_table += """\n       <table class="BackupDataPolType1">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td>Policy Type</td>"""
        html_data_table += """\n                </tr>"""
        html_data_table += """\n            </tbody>"""
        html_data_table += """\n        </table>"""
        html_data_table += """\n        <table class="BackupDataPolType2">"""
        html_data_table += """\n            <tbody>"""
        html_data_table += """\n                <tr>"""
        html_data_table += """\n                    <td class="polconfighead">Policy Type</td>"""
        html_data_table += """\n                    <td class="polconfighead">Policy Count</td>"""
        html_data_table += """\n                </tr>"""

        policy_type_lines = []
        file_path = os.path.join(dashboard_files_dir,dashboard_policy_type)
        with open(file_path,'r') as f:
            policy_type_lines = f.readlines()

        class_name = "polconfig1"
        for line in policy_type_lines:
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            html_table_row = """\n              <tr>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[0].strip() + """</td>"""
            html_table_row += """\n                 <td class=\"""" + class_name + """\">""" + line_split[1].strip() + """</td>"""
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

        tables += self.generate_data_table_five()
        tables += self.generate_data_table_one()
        tables += self.generate_data_table_two()
        tables += self.generate_data_table_three()
        tables += self.generate_data_table_four()
        tables += self.generate_data_table_seven()


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
        print '%s WARNING 19.MainIndex.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set!')

# Policy Type
    dashboard_policy_type_file_path = os.path.join(dashboard_files_dir,dashboard_policy_type)
    if not os.path.isfile(dashboard_policy_type_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_policy_type_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_policy_type_file_path)

        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

# Billing
    dashboard_billing_file_path = os.path.join(dashboard_files_dir,dashboard_billing_file)
    if not os.path.isfile(dashboard_billing_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_billing_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_billing_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

# Open Actions
    dashboard_liveview_file_path = os.path.join(dashboard_files_dir,dashboard_liveview_file)
    if not os.path.isfile(dashboard_liveview_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_liveview_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_liveview_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_historyview_file_path = os.path.join(dashboard_files_dir,dashboard_historyview_file)
    if not os.path.isfile(dashboard_historyview_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_historyview_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_historyview_file_path)

        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_monthly_view_file_path = os.path.join(dashboard_files_dir,dashboard_monthly_view_file)
    if not os.path.isfile(dashboard_monthly_view_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_monthly_view_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_monthly_view_file_path)

        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_weeklyview_file_path = os.path.join(dashboard_files_dir,dashboard_weeklyview_file)
    if not os.path.isfile(dashboard_weeklyview_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_weeklyview_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_weeklyview_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_backup_variance_file_path = os.path.join(dashboard_files_dir,dashboard_backup_variance_file)
    if not os.path.isfile(dashboard_backup_variance_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backup_variance_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backup_variance_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_notdefined_file_path = os.path.join(dashboard_files_dir,dashboard_notdefined_file)
    if not os.path.isfile(dashboard_notdefined_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_notdefined_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_notdefined_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

# Infrastructure Details
    dashboard_policy_file_path = os.path.join(dashboard_files_dir,dashboard_policy_file)
    if not os.path.isfile(dashboard_policy_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_policy_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_policy_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_uniqclient_file_path = os.path.join(dashboard_files_dir,dashboard_uniqclient_file)
    if not os.path.isfile(dashboard_uniqclient_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_uniqclient_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_uniqclient_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_backup_client_file_path = os.path.join(dashboard_files_dir,dashboard_backup_client_file)
    if not os.path.isfile(dashboard_backup_client_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backup_client_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backup_client_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_backup_size_file_path = os.path.join(dashboard_files_dir,dashboard_backup_size_file)
    if not os.path.isfile(dashboard_backup_size_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backup_size_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backup_size_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_catalog_file_path = os.path.join(dashboard_files_dir,dashboard_catalog_file)
    if not os.path.isfile(dashboard_catalog_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_catalog_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_catalog_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    dashboard_backuptime_file_path = os.path.join(dashboard_files_dir,dashboard_backuptime_file)
    if not os.path.isfile(dashboard_backuptime_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backuptime_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backuptime_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

# Backup Issues
    dashboard_backup_issue_file_path = os.path.join(dashboard_files_dir,dashboard_backup_issue)
    if not os.path.isfile(dashboard_backup_issue_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backup_issue_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backup_issue_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

# Backup Usage
    dashboard_backup_usage_file_path = os.path.join(dashboard_files_dir,dashboard_backup_usage)
    if not os.path.isfile(dashboard_backup_usage_file_path):
        print '%s ERROR 19.MainIndex.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_backup_usage_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_backup_usage_file_path)
        print '%s INFO 19.MainIndex.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    main_index_obj = MainIndex()
    html = main_index_obj.generate_html_page()
    dt = datetime.now()
    print '%s INFO 19.MainIndex.py  Output is saving to: %s' % (dt.strftime(dformat), default_html_output_file_path)
    app_logger.log_info('Output is saving to: %s' % default_html_output_file_path)

    with open(default_html_output_file_path,'w') as f:
        f.write(html)

    dt = datetime.now()
    print '%s INFO 19.MainIndex.py  Output Saved!' % dt.strftime(dformat)
    app_logger.log_info('Output Saved!')

if __name__ == "__main__":
    dt = datetime.now()
    print '%s INFO 19.MainIndex.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 19.MainIndex.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 19.MainIndex.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')


    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 19.MainIndex.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 19.MainIndex.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
