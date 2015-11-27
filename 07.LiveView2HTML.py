#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
from datetime import datetime
import time
import operator
from LoggingManager import *
from GlobalConfig import *

config_vars_one = GlobalConfig.read_vars('06.LiveViewInput')
config_vars = GlobalConfig.read_vars('07.LiveView2HTML')

page_title = config_vars.get('page_title')
sorted_page_title = config_vars.get('sorted_page_title')
input_file_name = config_vars.get('input_file_name')
output_file_name = config_vars.get('output_file_name')
sorted_output_file_name = config_vars.get('sorted_output_file_name')
column_five_value = config_vars_one.get('column_five_percentage')
timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

app_logger = LoggingManager('07.LiveView2HTML.py')

class HtmlGenerator:
    def __init__(self):
        pass

    def read_next_lines(self,lines,start=0,line_count=2):
        temp_lines = []
        while True:
            temp_lines = lines[start:start+line_count]
            if not temp_lines:
                break
            yield temp_lines

    def generate_html_page(self,page_title='24 Hours View',input_file_name='input.txt',output_file_name='24hoursview.html',is_sorted=False):
        try:
            html = """<!DOCTYPE html>"""
            html += """\n<html>\n    <head>\n    <meta charset="utf-8" />\n    <title>"""+page_title+"""</title>"""
            html += """\n    <link rel="stylesheet" type="text/css" href="css/view.css">\n    </head>\n    <body>"""
            html += """\n    <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
            html += """\n    <script type="text/javascript" src="js/wz_tooltip.js"></script>"""
            html += """\n    <table class="BackupDataTime" align="right">\n        <tbody>\n            <tr>\n            <td> Last Updated:<br>"""+str(timenow)+""" </td>"""
            html += """\n            </tr>\n        </tbody>\n    </table>"""
            html += """\n    <div id='logo'>\n        <header>\n            <div id='header'></div>\n           <div id='headerbar'></div>\n            <div>"""
            html += """\n                    <img src="img/version.png" alt="version logo" id="version"/>\n            </div>"""
            html += """\n        </header>\n                </div>\n                <nav>\n                    <ul id="menubar">"""
            html += """\n                        <li><a href="./index.html">Dashboard</a></li>"""
            html += """\n                        <li><a href="./liveview.html" class="selected">Live View</a></li>"""
            html += """\n                        <li><a href="./historyview.html">History View</a></li>"""
            html += """\n                        <li><a href="./monthlyview.html">Monthly View</a></li>"""
            html += """\n                        <li><a href="./weeklyview.html">Weekly View</a></li>"""
            html += """\n                        <li><a>Sort By</a>"""
            html += """\n                            <ul>"""
            html += """\n                                <li><a href="./liveview.html">Policy Name</a></li>"""
            html += """\n                                <li><a href="./liveviewsortbyclient.html">Client Name</a></li>"""
            html += """\n                            </ul>"""
            html += """\n                        </li>"""
            html += """\n                        <li><a href="./help.html">Help</a></li>"""
            html += """\n                    </ul>"""
            html += """\n                </nav>"""
            html += """\n    <div id='body'></div>"""
            html += """\n    <p>\n    </p>"""

            input_data = []
            with open(input_file_name,'r') as fi:
                input_data = fi.readlines()

            if not input_data:
                app_logger.log_error('No input data is found in file %s' % input_file_name)
                return

            if is_sorted:
                input_data = [line.split(',') for line in input_data]
                input_data = sorted(input_data,key=operator.itemgetter(1),reverse=False)
                input_data = [','.join(line) for line in input_data]

            table = """\n    <table class="BackupData">"""
            table += """\n        <tbody>"""

            tr_row = """"""

            for i,line in enumerate(input_data):
                line_split = line.split(',')
                if i % 7 == 0:
                    tr_row = """\n        <tr>"""
                td_cols = []
                col_three_val = line_split[2]
                if col_three_val == 'NoBackup' or col_three_val == 'Inactive' or col_three_val == 'NoSchedule' or col_three_val == 'FullMissing':
                    td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],line_split[1])
                    td_cols += [td_col]
                elif col_three_val == 'Active' or col_three_val == 'LongRun':
                    running_time = line_split[3]
                    try:
                        running_time = str(float(running_time)/3600.0)
                    except Exception,msg:
                        pass
                    td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s<br><div>%s Hours</div>%s')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],running_time,line_split[4],line_split[1])
                    td_cols += [td_col]
                else:
                    td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s<br>%s<br>%s seconds<br>%s Kbytes<br>%s files')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],line_split[3],line_split[4],line_split[5],line_split[6],line_split[1])
                    td_cols += [td_col]

                td_cols_merged = "\n".join(td_cols)

                tr_row += """\n"""+td_cols_merged
                if i % 7 == 6:
                    tr_row += """\n       </tr>"""
                    table += tr_row

            remaining_line_count = len(input_data) % 7

            remaining_lines = []
            if remaining_line_count > 0:
                remaining_lines = input_data[-remaining_line_count:]

                temp_tr = """\n        <tr>"""
                td_cols = []

                for line in remaining_lines:
                    line_split = line.split(',')
                    col_three_val = line_split[2]
                    if col_three_val == 'NoBackup' or col_three_val == 'Inactive':
                        td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],line_split[1])
                        td_cols += [td_col]
                    elif col_three_val == 'Active' or col_three_val == 'LongRun':
                        running_time = line_split[3]
                        try:
                            running_time = str(float(running_time)/3600.0)
                        except Exception,msg:
                            pass
                        td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s<br><div>%s Hours</div>%s')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],running_time,line_split[4],line_split[1])
                        td_cols += [td_col]
                    else:
                        td_col = """            <td class="%s"> <a href="%s-%s.html" onmouseover="Tip('%s<br>%s<br>%s<br>%s<br>%s seconds<br>%s Kbytes<br>%s files')" onmouseout="UnTip()">%s</a></td>""" % (line_split[2],line_split[0],line_split[1],line_split[0],line_split[1],line_split[2],line_split[3],line_split[4],line_split[5],line_split[6],line_split[1])
                        td_cols += [td_col]

                for j in range(7-len(remaining_lines)):
                    td_cols += ['            <td></td>']

                td_cols_merged = "\n".join(td_cols)

                temp_tr += """\n"""+td_cols_merged
                temp_tr += """\n       </tr>"""

                table += temp_tr

            table += """\n        </tbody>"""
            table += """\n   </table>"""
            html += table

            html += """\n    <p>\n    </p>"""
            html += """\n    <div>\n        <table class="BackupDataFooter">"""
            html += """\n            <tbody>"""
            html += """\n                <tr>\n                    <td class="keytocolors">Key to colours</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="Full">Successful Full Backup</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="Incr">Successful Incremental Backup</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="Active">Currently Running Backup</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="LongRun">Backup is running for more than """ + '%s' % str(column_five_value) + """ percent of previous Full Backup time! - Most probably the job is stuck</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="Inactive">Inactive Backup Policy</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="NoSchedule">No Backup Scheduled for today</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="Misc">Valid Backup but Misconfigured</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="FullMissing">No Full backup exist for this policy - Please run Full backup ASAP</td>\n                </tr>"""
            html += """\n                <tr>\n                    <td class="NoBackup">No Backup Data for the period</td>\n                </tr>"""
            html += """\n            </tbody>\n        </table>\n    </div>"""
            html += """\n"""
            html += """\n    <p>\n    </p>"""
            html += """\n    <p>"""+str(timenow)+"""\n    </p>"""
            html += """\n    </body>\n</html>"""

            dformat = '%Y-%m-%d %H:%M:%S'
            dt = datetime.now()
            print '%s INFO 07.LiveView2HTML.py  File is saving to %s' % (dt.strftime(dformat), output_file_name)
            app_logger.log_info('File is saving to %s' % (output_file_name))
            with open(output_file_name,'w') as f:
                f.write(html)

            dt = datetime.now()
            print '%s INFO 07.LiveView2HTML.py  File Saved.' % dt.strftime(dformat)
            app_logger.log_info('File Saved.')
        except Exception,msg:
            dformat = '%Y-%m-%d %H:%M:%S'
            dt = datetime.now()
            print '%s ERROR 07.LiveView2HTML.py  Exception occured inside generate_html_page() method. Exception message: %s' % (dt.strftime(dformat), msg)
            #print msg
            app_logger.log_error('Exception occured inside generate_html_page() method. Exception message: %s' % msg)

def run_main():
    dformat = '%Y-%m-%d %H:%M:%S'
    dt = datetime.now()

    if not page_title:
        print '%s WARNING 07.LiveView2HTML.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set.')

    if not column_five_value:
        print '%s WARNING 07.LiveView2HTML.py  column_five_value is not set' % dt.strftime(dformat)
        app_logger.log_warning('column_five_value is not set.')

    try:
        int(column_five_value)
    except Exception,msg:
        print '%s WARNING 07.LiveView2HTML.py  Invalid value %s' % (dt.strftime(dformat), column_five_value)
        app_logger.log_warning('Invalid value %s' % column_five_value)

    if not sorted_page_title:
        print '%s WARNING 07.LiveView2HTML.py  Sorted page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Sorted page title is not set.')

    if not os.path.isfile(input_file_name):
        print '%s ERROR 07.LiveView2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), input_file_name)
        app_logger.log_error('%s is not a valid file.' % input_file_name)
        app_logger.log_info('Program is exiting...')
        print '%s INFO 07.LiveView2HTML.py  Program is exiting...' % dt.strftime(dformat)
        return
    try:
        html_generator_obj.generate_html_page(page_title=page_title,input_file_name=input_file_name,output_file_name=output_file_name,is_sorted=False)
        html_generator_obj.generate_html_page(page_title=sorted_page_title,input_file_name=input_file_name,output_file_name=sorted_output_file_name,is_sorted=True)
    except Exception,msg:
        print 'Exception occured. Exception message: %s' % str(msg)
        app_logger.log_error('Exception occured. Exception message: %s' % str(msg))

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

if __name__ == '__main__':
    dformat = '%Y-%m-%d %H:%M:%S'
    dt = datetime.now()
    print '%s INFO 07.LiveView2HTML.py  Started program...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    html_generator_obj = HtmlGenerator()
    start_time = unix_time(dt)
    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 07.LiveView2HTML.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 07.LiveView2HTML.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    dt = datetime.now()
    print '%s INFO 07.LiveView2HTML.py  Ended program...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
