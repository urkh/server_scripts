#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
from datetime import datetime
from datetime import timedelta
import time
import csv
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('10.HistoryView2HTML')

default_page_title = config_vars.get('default_page_title')
monthview_page_title = config_vars.get('monthview_page_title')
weekview_page_title = config_vars.get('weekview_page_title')
history_all_file_path = config_vars.get('history_all_file_path')
earliest_date_file_path = config_vars.get('earliest_date_file_path')
default_output_file_path = config_vars.get('default_output_file_path')
monthview_output_file_path = config_vars.get('monthview_output_path')
weekview_output_file_path = config_vars.get('weekview_output_path')
csv_default_file_path = config_vars.get('csv_default_file_path')
csv_monthview_file_path = config_vars.get('csv_monthview_file_path')
csv_weekview_file_path = config_vars.get('csv_weekview_file_path')
csv_report_path_default = config_vars.get('csv_report_path_default')
csv_report_path_monthly = config_vars.get('csv_report_path_monthly')
csv_report_path_weekly = config_vars.get('csv_report_path_weekly')
noschedules_data_file_path = config_vars.get('noschedules_data_file')
nopolicy_data_file_path = config_vars.get('nopolicy_data_file')
inactive_policies_data_file_path = config_vars.get('inactive_policies_data_file')
kpi_threshold = config_vars.get('kpi_threshold')
month_view_days_count = config_vars.get('month_view_days_count')
week_view_days_count = config_vars.get('week_view_days_count')
timetorun_file = config_vars.get('timetorun_file')
app_logger = LoggingManager('10.HistoryView2HTML.py')
dformat = '%Y-%m-%d %H:%M:%S'

class HtmlGeneratorHistoryAll:
    def __init__(self):
        pass

    def unix_time(self,dt):
        return int(time.mktime(dt.timetuple()))

    def get_static_html_part_upper(self,page_title,csv_report_file_name,html_file_name):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        output_file_name = None
        try:
            output_file_name = html_file_name[html_file_name.rindex("/")+1:]
        except Exception,msg:
            pass
        
        _timetorun = open(timetorun_file, 'r').readlines()[-1]

        html = """<!DOCTYPE html>"""
        html += """\n<html>\n    <head>\n    <meta charset="utf-8" />\n    <title>"""+page_title+"""</title>"""
        html += """\n    <link rel="stylesheet" type="text/css" href="css/view.css">\n    </head>\n    <body>"""
        html += """\n    <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
        html += """\n    <script type="text/javascript" src="js/jquery.min.js"></script>"""
        html += """\n    <script type="text/javascript" src="js/wz_tooltip.js"></script>"""
        html += """\n<script>"""
        html += """\n$(document).ready(function()"""
        html += """\n{"""
        html += """\n   $("#menubar a").each(function(i)"""
        html += """\n   {"""
        html += """\n       var href = $(this).attr("href");"""
        html += """\n       $(this).removeClass("selected");"""
        html += """\n       if (href.indexOf(\"""" +output_file_name+ """\") >= 0)"""
        html += """\n       {"""
        html += """\n           $(this).addClass("selected");"""
        html += """\n		}"""
        html += """\n	});"""
        html += """\n});"""
        html += """\n</script>"""
        html += """\n  <header>"""
        html += """\n    <table class="BackupTimeRun" align="right">"""
        html += """\n      <tbody>"""
        html += """\n        <tr>"""
        html += """\n          <td>Time to Run: <br>""" + _timetorun + """</td>"""
        html += """\n        </tr>"""
        html += """\n      </tbody>"""
        html += """\n    </table>"""
        html += """\n    <table class="BackupDataTime" align="right">"""
        html += """\n      <tbody>"""
        html += """\n        <tr>"""
        html += """\n          <td> Last Updated:<br>""" + str(timenow) + """</td>"""
        html += """\n        </tr>"""
        html += """\n      </tbody>"""
        html += """\n    </table>"""
        html += """\n    <div id='logo'>"""
        html += """\n      <header>"""
        html += """\n        <div id='header'></div>"""
        html += """\n        <div id='headerbar'></div>"""
        html += """\n        <div>"""
        html += """\n          <img src="img/version.png" alt="version logo" id="version"/>"""
        html += """\n        </div>"""
        html += """\n      </header>"""
        html += """\n    </div>"""
        html += """\n    <nav>"""
        html += """\n      <ul id="menubar">"""
        html += """\n        <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n        <li><a href="./liveview.html">Live View</a></li>"""
        html += """\n        <li><a href="./historyview.html" class="selected">History View</a></li>"""
        html += """\n        <li><a href="./monthlyview.html">Monthly View</a></li>"""
        html += """\n        <li><a href="./weeklyview.html">Weekly View</a></li>"""
        html += """\n        <li><a href="./help.html">Help</a></li>"""
        html += """\n      </ul>"""
        html += """\n    </nav>"""
        html += """\n    <div id='body'></div>"""
        html += """\n    <p>"""
        html += """\n      <a href='""" + csv_report_file_name + """' style="text-decoration: underline; float: right">csv download</a>"""
        html += """\n    </p>"""

        return html

    def read_static_html_part_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n    <p>\n    </p>"""
        html += """\n    <div>\n        <table class="BackupDataFooter">"""
        html += """\n            <tbody>"""
        html += """\n                <tr>\n                    <td class="keytocolors">Key to colours</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THFull">Successful Full Backup</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="ExpTHFull"> Expired Successful Full Backup</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THIncr">Successful Incremental Backup</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="ExpTHIncr">Expired Successful Incremental Backup</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THNoBackup">No Backup Data for the period</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="TNoData">No Data prior to policy creation</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THNoNewBackup">No Backup done today</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THNoSchedule">No Backup scheduled today</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="THInactive">Inactive Policy</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="keytocolors">* KPI Based on """ + str(kpi_threshold) + """% of Successful Backup</td>\n                </tr>"""
        html += """\n                <tr>\n                    <td class="keytocolors">** Backup Size in GB based on Live Backup Data Only</td>\n                </tr>"""
        html += """\n            </tbody>\n        </table>\n    </div>"""
        html += """\n"""
        html += """\n    <p>\n    </p>"""
        html += """\n    <p>"""+str(timenow)+"""\n    </p>"""
        html += """\n    </body>\n</html>"""
        return html

    def read_sequence_in_chunks(self,file_object, last_line_read =0):
        """Lazy function (generator) to read a file piece by piece."""
        while True:
            sequence_name = None

            same_sequence_found = True

            data_sequence = []

            file_object.seek(last_line_read)
            data = file_object.readline()

            while data == '\n':
                last_line_read = last_line_read + len(data)
                file_object.seek(last_line_read)
                data = file_object.readline()

            last_line_read = last_line_read + len(data)
            if not data:
                same_sequence_found = False
                break

            data_sequence += [data]

            data_split = data.split(',')

            if data_split:
                sequence_name = data_split[0].strip()+'-'+data_split[1].strip()

            while same_sequence_found:
                file_object.seek(last_line_read)
                data = file_object.readline()

                if data == '\n':
                    last_line_read = last_line_read + len(data)
                    continue

                if not data:
                    break

                temp_data_split = data.split(',')

                if temp_data_split and temp_data_split[0] == data_split[0] and temp_data_split[1] == data_split[1]:
                    data_sequence += [data]
                    last_line_read = last_line_read + len(data)
                else:
                    same_sequence_found = False

            yield last_line_read,data_sequence,sequence_name

    def generate_html_page(self,page_title,input_file_name,earliest_date_file_name,output_file_name,view_type,output_csv_file_name,csv_report_file_name,noschedule_file_path):

        """ First read the lowest date from earliest_date.txt file which contains the date as 2014-06-20 03:01:01 format. """

        csv_contents = []
        
        #import ipdb; ipdb.set_trace()

        earliest_date = None
        #if view_type == 'default':
        dt = datetime.now()

        with open(earliest_date_file_name,'r') as f:
            data = f.read()
            if data:
                earliest_date = data.replace('\n','').strip()

        if not earliest_date:
            print '%s ERROR 10.HistoryView2HTML.py  Earliest date not found. Program exiting...' % dt.strftime(dformat)
            app_logger.log_error('Earliest date not found in %s.' % earliest_date_file_name)
            print 'Program exiting...'
            return

        try:
            earliest_date = datetime.strptime(earliest_date,'%Y-%m-%d %H:%M:%S')
        except Exception,msg:
            print '%s ERROR 10.HistoryView2HTML.py  Invalid earliest date %s given.' % (dt.strftime(dformat), earliest_date)
            app_logger.log_error('Invalid earliest date %s given.' % earliest_date)
            print 'Program exiting...'
            return

        if view_type == 'month':
            #int(month_view_days_count)
            _dt = datetime.now()
            todays_date = datetime.strptime(str(_dt)[:-7],'%Y-%m-%d %H:%M:%S')
            month_earliest_date = todays_date+timedelta(days=-int(month_view_days_count))
            if earliest_date < month_earliest_date:
                earliest_date = month_earliest_date
        elif view_type == 'week':
            _dt = datetime.now()
            todays_date = datetime.strptime(str(_dt)[:-7],'%Y-%m-%d %H:%M:%S')
            week_earliest_date = todays_date+timedelta(days=-int(week_view_days_count))
            if earliest_date < week_earliest_date:
                earliest_date = week_earliest_date

        """ Now we have got the earliest date. We need to generate total columns from the earliest date till yesterday. """
        start_date = datetime.strptime(str(earliest_date),'%Y-%m-%d %H:%M:%S')
        dt = datetime.now()
        end_date = dt
        end_date = datetime.strptime(str(end_date)[:-7],'%Y-%m-%d %H:%M:%S')

        dates = []

        while end_date >= start_date:
            dates += [start_date]
            start_date = start_date+timedelta(days=1)

        dates.sort(reverse=False)

        large_file = open(input_file_name,'r')
        last_line_read = 0

        ###Read noschedules file here.
        noschedules = []
        with open(noschedule_file_path,'r') as nsf:
            noschedules = nsf.readlines()

        #noschedules = [line.replace('\n','').strip() for line in noschedules]

        noschedules_dict = {}

        for k,entry in enumerate(noschedules):
            #policy20, master, 1405685426, NoSchedule
            entry = entry.replace('\n','').strip()
            entry_split = entry.split(',')
            policy_name = entry_split[0].strip()
            server_name = entry_split[1].strip()
            entry_timestamp = entry_split[2].strip()
            entry_status = entry_split[3].strip()
            entry_datetime = datetime.fromtimestamp(int(entry_timestamp))
            entry_date = entry_datetime.date()
            if entry_status == 'NoSchedule':
                data_row = [policy_name,server_name]
                if not noschedules_dict.get(entry_date):
                    noschedules_dict[entry_date] = [data_row]
                else:
                    policy_server_exist = False
                    for drow in noschedules_dict.get(entry_date):
                        if drow[0] == policy_name and drow[1] == server_name:
                            policy_server_exist = True
                            break
                    if not policy_server_exist:
                        noschedules_dict[entry_date] += [data_row]

        ###Read inactive_policies file here.
        inactive_policies = []
        with open(inactive_policies_data_file_path,'r') as ipf:
            inactive_policies = ipf.readlines()

        inactive_policies_dict = {}
        for k,entry in enumerate(inactive_policies):
            #policy20, master, 1405685426, NoSchedule
            entry = entry.replace('\n','').strip()
            entry_split = entry.split(',')
            policy_name = entry_split[0].strip()
            server_name = entry_split[1].strip()
            entry_timestamp = entry_split[2].strip()
            entry_status = entry_split[3].strip()
            entry_datetime = datetime.fromtimestamp(int(entry_timestamp))
            entry_date = entry_datetime.date()
            if entry_status == 'Inactive':
                data_row = [policy_name,server_name]
                if not inactive_policies_dict.get(entry_date):
                    inactive_policies_dict[entry_date] = [data_row]
                else:
                    policy_server_exist = False
                    for drow in inactive_policies_dict.get(entry_date):
                        if drow[0] == policy_name and drow[1] == server_name:
                            policy_server_exist = True
                            break
                    if not policy_server_exist:
                        inactive_policies_dict[entry_date] += [data_row]

        # read nopolicy datafile
        temp_nopolicy_data = {}
        nopolicy_data = open(nopolicy_data_file_path, 'r').readlines()
        for nop in nopolicy_data:
            entry_date = datetime.fromtimestamp(int(nop.split(',')[2])).date()
            policy_name = nop.split(',')[0].strip()
            server_name = nop.split(',')[1].strip()
            data_row = [policy_name, server_name]
            if not temp_nopolicy_data.get(entry_date):
                temp_nopolicy_data[entry_date] = [data_row]
            else:
                tmp_np = temp_nopolicy_data[entry_date]
                tmp_np.append(data_row)


        html = self.get_static_html_part_upper(page_title,csv_report_file_name,output_file_name)

        html += """\n<table class="BackupData2">"""

        header_row = """\n<tr>"""
        header_row += """<td class="HdrCell">Policy</td>"""
        header_row += """<td class="HdrCell">Server</td>"""
        header_row += """<td class="HdrCell">KPI*</td>"""
        header_row += """<td class="HdrCell">Backup Size KB**</td>"""

        csv_header_row = ['Policy','Server','KPI*','Backup Size GB**']

        for each_date in dates:
            formatted_date = each_date.strftime('%d %b<br/>%Y')
            csv_formatter_date = each_date.strftime('%d %b, %Y')
            header_row += """<td class="HdrCell">"""+formatted_date+"""</td>"""
            csv_header_row += [csv_formatter_date]

        header_row += """</tr>"""

        html += header_row

        csv_contents += [csv_header_row]

        pol_status = ''

        def get_value_for_date(policy_name,server_name,lines,target_date):
            value = 'NoExist'
            line = ''
            target_date_only = target_date.date()
            nowdate = datetime.now()
            try:
                todays_date = datetime.strptime(str(nowdate)[:-7],'%Y-%m-%d %H:%M:%S')
            except Exception,msg:
                todays_date = datetime.strptime(str(nowdate),'%Y-%m-%d %H:%M:%S')

            todays_date_only = todays_date.date()
            for aline in lines:
                if aline:
                    lsplit_temp = aline.split(',')
                    datetime_val = datetime.strptime(lsplit_temp[2],'%Y-%m-%d %H:%M:%S')
                    date_val = datetime_val.date()
                    if date_val == target_date_only:
                        if lsplit_temp[8].strip() == 'ExpiredData':
                            if lsplit_temp[3].strip() == '0':
                                value = 'ExpHFull'
                            elif lsplit_temp[3].strip() == '1' or lsplit_temp[3].strip() == '4':
                                value = 'ExpHIncr'
                        else:
                            if lsplit_temp[3].strip() == '0':
                                value = 'HFull'
                            elif lsplit_temp[3].strip() == '1' or lsplit_temp[3].strip() == '4':
                                value = 'HIncr'
                        line = aline
                        break
                    elif target_date_only > date_val:
                        if target_date_only == todays_date_only:
                            value = 'HNoNewBackup'
                        else:
                            value = 'HNoBackup'
                            nop_server_rows = temp_nopolicy_data.get(target_date_only)
                            if nop_server_rows:
                                for nop_server_row in nop_server_rows:
                                    if nop_server_row[0] == policy_name and nop_server_row[1] == server_name:
                                        value = 'HNoPolicy'

                            p_server_rows = noschedules_dict.get(target_date_only)
                            if p_server_rows:
                                for p_server_row in p_server_rows:
                                    if p_server_row[0] == policy_name and p_server_row[1] == server_name:
                                        value = 'HNoSchedule'

                            pcy_server_rows = inactive_policies_dict.get(target_date_only)
                            if pcy_server_rows:
                                for pcy_server_row in pcy_server_rows:
                                    if pcy_server_row[0] == policy_name and pcy_server_row[1] == server_name:
                                        value = 'HInactive'
                                        pol_status = value

                        line = aline
            return value,line

        def check_for_livedata(lines):
            for line in lines:
                line_split = line.split(',')
                if line_split[8].replace('\n','').strip() == 'LiveData':
                    return True
            return False


        rows = []

        for i,(last_line_read,lines,seq_name) in enumerate(self.read_sequence_in_chunks(large_file,last_line_read)):
            dt = datetime.now()
            print '%s INFO 10.HistoryView2HTML.py  Entered sequence %s' % (dt.strftime(dformat), seq_name)
            app_logger.log_info('Entered sequence %s' % seq_name)

            live_data_exist = check_for_livedata(lines)
            if not live_data_exist:
                continue

            """ Here generate each row. """
            row = []
            value_lines = {}
            #seq_name_split = seq_name.split('-')
            #row += [seq_name_split[0].strip()]
            #row += [seq_name_split[1].strip()]


            line_group = {}
            for line in lines:
                lsplit = line.split(',')
                ddatetime = datetime.strptime(lsplit[2],'%Y-%m-%d %H:%M:%S')
                ddate = ddatetime.date()
                if not str(ddate) in line_group.keys():
                    line_group[str(ddate)] = [line]
                else:
                    line_group[str(ddate)] += [line]

            unique_items = []
            for group, group_lines in line_group.items():

                seq_zero_lines = []
                live_data_lines = []
                for each_gline in group_lines:
                    gline_split = each_gline.split(',')
                    col_nine_val = gline_split[8].strip()
                    if col_nine_val == 'LiveData':
                        live_data_lines += [each_gline]

                if live_data_lines:
                    for each_gline in live_data_lines:
                        gline_split = each_gline.split(',')
                        col_four_val = gline_split[3].strip()

                        if col_four_val == '0':
                            seq_zero_lines += [each_gline]
                            break

                    if seq_zero_lines:
                        unique_items += [seq_zero_lines[0]]
                    else:
                        unique_items += [live_data_lines[0]]

                else:
                    for each_gline in group_lines:
                        gline_split = each_gline.split(',')
                        col_four_val = gline_split[3].strip()
                        if col_four_val == '0':
                            seq_zero_lines += [each_gline]
                            break

                    if seq_zero_lines:
                        unique_items += [seq_zero_lines[0]]
                    else:
                        unique_items += [group_lines[0]]

            policy_name = seq_name.split('-')[0]
            server_name = seq_name.split('-')[1]

            """ Now we have unique lines in sequence lines. """
            for i,each_col_date in enumerate(dates):
                calc_value = get_value_for_date(policy_name, server_name, unique_items, each_col_date)
                row += [calc_value[0]]
                value_lines[i] = calc_value

            total_count = row.count('HFull') + row.count('ExpHFull') + row.count('HIncr') + row.count('ExpHIncr') + row.count('HNoBackup')
            fresh_count = row.count('HFull') + row.count('ExpHFull') + row.count('HIncr') + row.count('ExpHIncr')

            # calculate the kpi
            kpi_val = 100
            try:
                kpi_val = int((float(fresh_count)/total_count) * 100)
            except Exception:
                pass
            

            kpi_value = """%s%%""" % (str(kpi_val))
            kpi_class = """KPINOK"""
            if kpi_val >= int(kpi_threshold):
                kpi_class = """KPIOK"""

            row_str = """\n<tr>"""

            """Calculate the backup size in GB here."""
            col_six_val_sum = 0.0
            for line in lines:
                line_split = line.split(',')
                if line_split[8].replace('\n','').strip() == 'LiveData':
                    col_six_val = line_split[5].strip()
                    col_six_val_sum += float(col_six_val)

            backup_size_gb = float(col_six_val_sum)
#             backup_size_gb = float(col_six_val_sum)/(1024*1024)  Rahim Commented for testting

            backup_size_gb = '%.2f' % backup_size_gb

            seq_name_split = seq_name.split('-')

            row_str += """\n<td class="HdrCell">%s</td>""" % (seq_name_split[0].strip())
            #row_str += """\n<td Class="HdrCell"><a href = %s-%s.html> %s </a> </td>""" % (seq_name_split[0].strip(),seq_name_split[1].strip(),seq_name_split[1].strip())
            row_str += """\n<td Class="HdrCell"><a href = %s.html> %s </a> </td>""" % (seq_name.strip(),'-'.join(seq_name_split[1:]))
            #import ipdb; ipdb.set_trace()
            row_str += """\n<td class="%s">%s</td>""" % (kpi_class,kpi_value)
            row_str += """\n<td class="HdrCell">%s</td>""" % backup_size_gb

            csv_data_row = [seq_name_split[0].strip(),'-'.join(seq_name_split[1:]),kpi_value,backup_size_gb]

            for i,value in enumerate(row):
                data_line_val = value_lines.get(i)
                data_line = data_line_val[1]

                if value == 'NoExist':
                    row_str += """\n<td class="NoData">-</td>"""
                    csv_data_row += ['NoData']
                elif value == 'HNoBackup':
                    row_str += """\n<td class="HNoBackup">-</td>"""
                    csv_data_row += ['NoBackup']
 
                elif value == 'HNoPolicy':
                    row_str += """\n<td class="HNoPolicy">-</td>"""
                    csv_data_row += ['NoPolicy']
                elif value == 'HNoSchedule':
                    row_str += """\n<td class="HNoSchedule">-</td>"""
                    csv_data_row += ['NoSchedule']
                elif value == 'HNoNewBackup':
                    row_str += """\n<td class="HNoNewBackup">-</td>"""
                    csv_data_row += ['NoNewBackup']
                elif value == 'HInactive':
                    row_str += """\n<td class="HInactive">-</td>"""
                    csv_data_row += ['HInactive']
                else:
                    data_line = data_line.replace('\n','')
                    data_line_split = data_line.split(',')
                    incr_full = ''
                    if data_line_split[3].strip() == '1' or data_line_split[3].strip() == '4':
                        incr_full = 'Incr'
                    elif data_line_split[3].strip() == '0':
                        incr_full = 'Full'

                    csv_data_row += [value.replace('H','')]

                    row_str += """\n<td class="%s"> <a onmouseover="Tip('%s<br>%s<br>%s<br>%s seconds<br>%s Kbytes<br>%s files<br>Bck:%s<br> Exp:%s')" onmouseout="UnTip()">-</a></td>""" \
                               % (value,data_line_split[0].strip(),data_line_split[1].strip(),incr_full,data_line_split[4].strip(),
                                  data_line_split[5].strip(),data_line_split[6].strip(),data_line_split[2].strip(),
                                  data_line_split[7].strip())
            csv_contents += [csv_data_row]

            row_str += """\n</tr>"""
            html += row_str


        html += """\n</table>"""
        html += self.read_static_html_part_lower()
        dt = datetime.now()
        print '%s INFO 10.HistoryView2HTML.py  Output is saving to: %s' % (dt.strftime(dformat), output_file_name)
        app_logger.log_info('Output is saving to: %s' % output_file_name)

        with open(output_file_name,'w') as output_file:
            output_file.write(html)

        dt = datetime.now()
        print '%s INFO 10.HistoryView2HTML.py  Output saved.' % dt.strftime(dformat)
        app_logger.log_info('Output saved.')

        if not output_csv_file_name.endswith('.csv'):
            output_csv_file_name = output_csv_file_name+'.csv'

        print '%s INFO 10.HistoryView2HTML.py  Output is saving to: %s' % (dt.strftime(dformat), output_csv_file_name)
        app_logger.log_info('Output is saving to: %s' % output_csv_file_name)

        with open(output_csv_file_name, 'w') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(csv_contents)

        dt = datetime.now()
        print '%s INFO 10.HistoryView2HTML.py  Output saved.' % dt.strftime(dformat)
        app_logger.log_info('Output saved.')

        large_file.close()

def run_main():
    """


    :return:
    """
    dt = datetime.now()
    if not default_page_title:
        print '%s WARNING 10.HistoryView2HTML.py  Default page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Default page title is not set!')

    if not monthview_page_title:
        print '%s WARNING 10.HistoryView2HTML.py  Month view page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Month view page title is not set!')

    if not weekview_page_title:
        print '%s WARNING 10.HistoryView2HTML.py  Week view page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Week view page title is not set!')

    if not os.path.isfile(history_all_file_path):
        print '%s ERROR 10.HistoryView2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), history_all_file_path)
        app_logger.log_error('%s is not a valid file.' % history_all_file_path)
        print 'Exiting program...'
        return

    if not os.path.isfile(earliest_date_file_path):
        print '%s ERROR 10.HistoryView2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), earliest_date_file_path)
        app_logger.log_error('%s is not a valid file.' % earliest_date_file_path)
        print 'Exiting program...'
        return
    if not os.path.isfile(noschedules_data_file_path):
        print '%s ERROR 10.HistoryView2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), noschedules_data_file_path)
        app_logger.log_error('%s is not a valid file.' % noschedules_data_file_path)
        print 'Exiting program...'
        return

    if not os.path.isfile(inactive_policies_data_file_path):
        print '%s ERROR 10.HistoryView2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), inactive_policies_data_file_path)
        app_logger.log_error('%s is not a valid file.' % inactive_policies_data_file_path)
        print 'Exiting program...'
        return

    if not kpi_threshold:
        print '%s ERROR 10.HistoryView2HTML.py  No KPI value found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('No KPI value found in the config file.')
        print 'Exiting program...'
        return
    if not month_view_days_count:
        print '%s ERROR 10.HistoryView2HTML.py  Month view days count not found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Month view days count not found in the config file.')
        print 'Exiting program...'
        return
    if not week_view_days_count:
        print '%s ERROR 10.HistoryView2HTML.py  Week view days count not found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Week view days count not found in the config file.')
        print 'Exiting program...'
        return
    try:
        int(month_view_days_count)
    except Exception,msg:
        print '%s ERROR 10.HistoryView2HTML.py  Invalid month view days count found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Invalid month view days count found in the config file.')
        print 'Exiting program...'
        return
    try:
        int(week_view_days_count)
    except Exception,msg:
        print '%s ERROR 10.HistoryView2HTML.py  Invalid week view days count found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Invalid week view days count found in the config file.')
        print 'Exiting program...'
        return
    else:
        try:
            int(kpi_threshold)
        except Exception,msg:
            print '%s ERROR 10.HistoryView2HTML.py  Invalid KPI value found in the config file.' % dt.strftime(dformat)
            app_logger.log_error('Invalid KPI value found in the config file.')
            print 'Exiting program...'
            return

    html_generator_historyall_obj = HtmlGeneratorHistoryAll()

    try:
        html_generator_historyall_obj.generate_html_page(default_page_title,history_all_file_path,earliest_date_file_path,default_output_file_path,view_type='default',output_csv_file_name=csv_default_file_path,csv_report_file_name=csv_report_path_default,noschedule_file_path=noschedules_data_file_path)
        html_generator_historyall_obj.generate_html_page(monthview_page_title,history_all_file_path,earliest_date_file_path,monthview_output_file_path,view_type='month',output_csv_file_name=csv_monthview_file_path,csv_report_file_name=csv_report_path_monthly,noschedule_file_path=noschedules_data_file_path)
        html_generator_historyall_obj.generate_html_page(weekview_page_title,history_all_file_path,earliest_date_file_path,weekview_output_file_path,view_type='week',output_csv_file_name=csv_weekview_file_path,csv_report_file_name=csv_report_path_weekly,noschedule_file_path=noschedules_data_file_path)
    except Exception,msg:
        dt = datetime.now()
        print '%s ERROR 10.HistoryView2HTML.py  Exception occured inside generate_html_page() method. Exception message: %s' % (dt.strftime(dformat), str(msg))
        app_logger.log_error('Exception occured inside generate_html_page() method. Exception message: %s' % str(msg))
        print 'Exiting program...'

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

if __name__ == '__main__':
    dt = datetime.now()
    print '%s INFO 10.HistoryView2HTML.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 10.HistoryView2HTML.py  Started running...' %dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)
    
    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 10.HistoryView2HTML.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 10.HistoryView2HTML.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 10.HistoryView2HTML.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
