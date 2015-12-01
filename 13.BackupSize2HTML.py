#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
from datetime import datetime
from datetime import timedelta
import time
import csv
import math
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('13.BackupSize2HTML')

default_page_title = config_vars.get('default_page_title')
report_size_count = config_vars.get('report_size_count')
variance_value = config_vars.get('variance_value')
history_file_path = config_vars.get('history_file_path')
output_html_file_default = config_vars.get('output_html_path_default')
output_csv_file_default = config_vars.get('output_csv_path_default')
csv_report_path_default = config_vars.get('csv_report_path_default')

app_logger = LoggingManager('13.BackupSize2HTML.py')
dformat = '%Y-%m-%d %H:%M:%S'

class BackupSize2HTMLGenerator:
    def __init__(self):
        pass

    def get_static_html_upper(self,title,csv_path_download):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """<!DOCTYPE html>"""
        html += """\n<html>\n   <head>\n<meta charset="utf-8" />\n      <title>"""+ title +"""</title>"""
        html += """\n<link rel="stylesheet" type="text/css" href="css/view.css">\n  </head>"""
        html += """\n   <body>"""
        html += """\n       <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
        html += """\n       <script type="text/javascript" src="js/wz_tooltip.js"></script>"""
        html += """\n       <table class="BackupDataTime" align="right">\n      <tbody>\n           <tr>"""
        html += """\n               <td> Last Updated:<br>"""+ str(timenow) +"""\n                </td>\n           </tr>\n     </tbody>"""
        html += """\n       </table>\n      <div id='logo'>\n           <header>\n              <div id='header'></div>\n            <div id='headerbar'></div>"""
        html += """\n               <div>\n                 <img src="img/version.png" alt="version logo" id="version"/>"""
        html += """\n               </div>\n            </header>\n      </div>\n        <nav>\n            <ul id="menubar">"""
        html += """\n               <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n               <li><a href="./reports.html">Reports</a></li>"""
        html += """\n               <li><a href="./policyconfig.html">Policy Config</a></li>"""
        html += """\n               <li><a href="./backupsize.html" class="selected">Backup Size</a></li>"""
        html += """\n               <li><a href="./catalog.html">Catalog</a></li>"""
        html += """\n               <li><a href="./backupwritetime.html">Bck Write Time</a></li>"""
        html += """\n               <li><a href="./billing.html">Billing</a></li>"""
        html += """\n               <li><a href="./help.html">Help</a></li>"""
        html += """\n               </ul>"""
        html += """\n        </nav>"""
        html += """\n        <div id='body'></div>\n        <p>"""
        html += """\n           <a href='""" + csv_path_download + """' style="text-decoration: underline; float: right";>csv download</a></p>"""

        return html

    def get_static_lower_html(self,variance_value):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n        <p></p>"""
        html += """\n        <div>"""
        html += """\n        <table class="BackupDataFooter">"""
        html += """\n           <tbody>"""
        html += """\n               <tr>\n                  <td class="keytocolors">Key to colours</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="keytocolors">Figures in bold = Full Backup Size</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="Tbacksize1sum">More than one Incremental backup exist for this day</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="Tbacksize2sum">More than one backup run in this day with at least one Full backup</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="keytocolors"> - (minus sign) = No Valid Backup Exist or Backup has Expired</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="keytocolors">* Backup Difference between last backup with previous backup same type.</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="keytocolors">** Variance based on """ + variance_value + """% difference between last backup with previous backup same type</td>"""
        html += """\n               </tr>"""
        html += """\n               <tr>\n                  <td class="keytocolors">*** Backup Size in GB based on Live Backup Data Only</td>"""
        html += """\n               </tr>"""
        html += """\n           </tbody>"""
        html += """\n       </table>"""
        html += """\n       </div>"""
        html += """\n       <p></p>"""
        html += """\n       <p>"""+str(timenow)+"""</p>"""
        html += """\n   </body>"""
        html += """\n</html>"""

        return html

    def read_chunks_from_history_data(self,policy_name,server_name,history_data):
        chunk = []
        for line in history_data:
            line = line.replace('\n','')
            line_split = line.split(',')
            if line_split[0].strip() == policy_name and line_split[1].strip() == server_name:
                chunk += [line]
        return chunk

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

    def find_current_date_last_backup_date(self,policy_name,server_name,chunk_lines,all_dates):

        current_backup_line = None
        last_previous_backup_line = None

        current_backup_date_index = -1

        chunk_lines = sorted(chunk_lines,key=lambda x: int(x.split(',')[2]),reverse=True)

        for i,line in enumerate(chunk_lines):
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            cols_datetime = datetime.fromtimestamp(int(line_split[2]))
            cols_date = cols_datetime.date()

            for j, adate in enumerate(all_dates):
                if adate == cols_date:
                    current_backup_date_index = j
                    current_backup_line = line
                    break
            if current_backup_line:
                break

        if not current_backup_line:
            return current_backup_line,last_previous_backup_line

        remaining_backup_dates = []
        if current_backup_date_index != -1:
            if len(all_dates) > current_backup_date_index + 2:
                remaining_backup_dates = all_dates[current_backup_date_index+1:]

        if not remaining_backup_dates:
            return current_backup_line,last_previous_backup_line

        current_backup_type = int(current_backup_line.split(',')[3].strip())

        for i,line in enumerate(chunk_lines):
            line = line.replace('\n','').strip()
            line_split = line.split(',')
            cols_datetime = datetime.fromtimestamp(int(line_split[2]))
            cols_date = cols_datetime.date()

            backup_type = int(line_split[3].strip())

            for j, adate in enumerate(remaining_backup_dates):
                if adate == cols_date and backup_type == current_backup_type:
                    last_previous_backup_line = line
                    break

            if last_previous_backup_line:
                break


        return current_backup_line,last_previous_backup_line


    def calculate_variance(self,policy_name,server_name,chunk_lines):
        tdays_date = datetime.now().date()

        min_date_in_history = tdays_date

        if chunk_lines:
            first_line = chunk_lines[0]
            first_line_split = first_line.split(',')
            min_date_in_history = datetime.fromtimestamp(int(first_line_split[2].strip()))
            min_date_in_history = min_date_in_history.date()

        all_dates = []

        temp_date = tdays_date

        while temp_date >= min_date_in_history:
            all_dates += [temp_date]
            temp_date = temp_date+timedelta(days=-1)

        all_dates.sort(reverse=True)

        current_backup_line,last_valid_backup_line = self.find_current_date_last_backup_date(policy_name,server_name,chunk_lines,all_dates)

        if not current_backup_line and not last_valid_backup_line:
            return 0,0

        if current_backup_line and not last_valid_backup_line:
            return 0,0

        cline_split = current_backup_line.split(',')
        lline_split = last_valid_backup_line.split(',')

        variance_val = int(cline_split[5]) - int(lline_split[5])

        variance_percentage = float(variance_val)/int(lline_split[5])

        variance_percentage = variance_percentage * 100

        fraction,integer = math.modf(variance_percentage)

        if fraction >= 0.5:
            variance_percentage = math.ceil(variance_percentage)
        else:
            variance_percentage = math.floor(variance_percentage)

        return variance_val,variance_percentage


    def generate_dynamic_data_table(self,report_size,history_file_path,output_html_path,variance_value):

        html = """\n          <table class="BackupData2">"""
        csv_contents = []

        report_dates = []

        report_dates_range = [i for i in range(int(report_size))]

        todays_date = datetime.now()

        report_dates = [todays_date+timedelta(days=-i) for i in report_dates_range]

        report_dates = [tdays_date.date() for tdays_date in report_dates]

        report_dates.sort()

        html += """\n               <tr>"""

        header_cols = ["""\n                <td class="backsizehead">Policy</td>"""]
        header_cols += ["""                 <td class="backsizehead">Server</td>"""]
        header_cols += ["""                 <td class="backsizehead">Difference*</td>"""]
        header_cols += ["""                 <td class="backsizehead">Variance**</td>"""]
        header_cols += ["""                 <td class="backsizehead">Backup Size KB***</td>"""]

        csv_header = ['Policy','Server','Variance*','Backup Size GB**']

        for each_date in report_dates:
            formatted_date = each_date.strftime('%d %b<br/>%Y')
            csv_formatter_date = each_date.strftime('%d %b, %Y')
            header_cols += ["""                 <td class="backsizehead">"""+formatted_date+"""</td>"""]
            csv_header += [csv_formatter_date]

        csv_contents += [csv_header]

        html += """\n""".join(header_cols)

        html += """\n               </tr>"""

        large_file = open(history_file_path,'r')
        last_line_read = 0

        def get_backup_size_on_date(bdate,lines):
            backup_size = None
            backup_full = False
            lines_on_date = []
            for line in lines:
                line = line.replace('\n','')
                line_split = line.split(',')

                target_datetime = datetime.fromtimestamp(int(line_split[2]))
                target_date = target_datetime.date()

                if bdate == target_date:
                    #backup_size = float(line_split[5])#/(1024*1024)
                    #backup_full_value = int(line_split[3])
                    #backup_full = True if backup_full_value == 0 else False
                    lines_on_date += [line]
                    #break

            col_four_val_mask = 1
            for l in lines_on_date:
                lsplit = l.split(',')
                if not backup_size:
                    backup_size = float(lsplit[5])
                else:
                    backup_size += float(lsplit[5])

                if int(lsplit[3]) == 0:
                    backup_full = True

                col_four_val_mask = col_four_val_mask & int(lsplit[3])

            multiple_occurance = False
            if len(lines_on_date) >= 2:
                multiple_occurance = True

            return backup_size,backup_full,multiple_occurance,col_four_val_mask

        for i,(last_line_read,lines,seq_name) in enumerate(self.read_sequence_in_chunks(large_file,last_line_read)):
            seq_name_split = seq_name.split('-')
            pname = seq_name_split[0].strip()
            sname = seq_name_split[1].strip()

            lines = [line.replace('\n','') for line in lines]

            lines_sorted = sorted(lines,key=lambda x: int(x.split(',')[2]))

            """Calculate the backup size in GB here."""
            col_six_val_sum = 0.0
            for line in lines:
                line_split = line.split(',')
                col_six_val = line_split[5].strip()
                col_six_val_sum += float(col_six_val)

            backup_size_gb = float(col_six_val_sum)#/(1024*1024)

            class_name = """backsize1"""
            if (i + 1) % 2 == 0:
                class_name = """backsize2"""

            backup_size_gb = '%.2f' % backup_size_gb

            data_cols = ["""\n            <tr>"""]

            difference,variance_percentage = self.calculate_variance(pname,sname,lines_sorted)

            difference_size_gb = '%.2f' % difference

            variance_class_name = class_name

            variance_value = float(variance_value)

            math_variance_absolute = math.fabs(variance_percentage)

            if math_variance_absolute > variance_value:
                variance_class_name = 'VarianceNOK'

            variance_percentage = str(int(variance_percentage))

            csv_data_row = [pname,'-'.join(seq_name_split[1:]),difference_size_gb,backup_size_gb]
            #import ipdb; ipdb.set_trace()

            data_cols += ["""\n                 <td class=\"""" + class_name + """\">""" + pname + """</td>"""]
            data_cols += ["""                   <td Class=\"""" + class_name + """\"><a href = """ + seq_name + """.html> """ + '-'.join(seq_name_split[1:]) + """ </a> </td>"""]
            data_cols += ["""                   <td class=\"""" + class_name + """\">""" + difference_size_gb + """</td>"""]
            data_cols += ["""                   <td class=\"""" + variance_class_name + """\">""" + variance_percentage + """%</td>"""]
            data_cols += ["""                   <td class=\"""" + class_name + """\">""" + backup_size_gb + """</td>"""]

            temp_class_name = class_name

            for each_date in report_dates:
                bsize,backup_full,multiple_occurance,col_four_val_mask = get_backup_size_on_date(each_date, lines_sorted)
                if backup_full:
                    class_name = temp_class_name + 'full'
                else:
                    class_name = temp_class_name

                if multiple_occurance:
                    if col_four_val_mask == 1:
                        class_name = 'backsize1sum'
                    else:
                        class_name = 'backsize2sum'

                if bsize:
                    bsize_gb_str = '%0.2f' % bsize
                    data_cols += ["""                   <td class=\"""" + class_name + """\">""" + bsize_gb_str + """</td>"""]
                    csv_data_row += [bsize_gb_str]
                else:
                    data_cols += ["""                   <td class=\"""" + class_name + """\">-</td>"""]
                    csv_data_row += ['NoData']

            csv_contents += [csv_data_row]

            data_cols += ["""           </tr>"""]

            html += """\n""".join(data_cols)

        html += """         </table>"""

        large_file.close()

        return html,csv_contents


    def generate_html(self):
        html = self.get_static_html_upper(default_page_title,csv_report_path_default)

        history_data = []
        with open(history_file_path,'r') as hf:
            history_data = hf.readlines()

        history_data_sorted = sorted(history_data, key = lambda x : (x[0], x[1]))

        history_data_sorted = [line.replace('\n','') for line in history_data_sorted]

        history_data = '\n'.join(history_data_sorted)

        history_file_sorted = history_file_path.replace('.txt','')+'_sorted.txt'

        with open(history_file_sorted,'w') as hf:
            hf.write(history_data)

        html_table,csv_contents = self.generate_dynamic_data_table(report_size_count,history_file_sorted,output_html_file_default,variance_value)
        html += html_table

        html += self.get_static_lower_html(variance_value)
        dt = datetime.now()

        print '%s INFO 13.BackupSize2HTML.py  Output is saving to: %s' % (dt.strftime(dformat), output_html_file_default)
        app_logger.log_info('Output is saving to: %s' % output_html_file_default)

        with open(output_html_file_default,'w') as output_file:
            output_file.write(html)

        dt = datetime.now()
        print '%s INFO 13.BackupSize2HTML.py  Output is saved.' % dt.strftime(dformat)
        app_logger.log_info('Output is saved.')

        csv_file_path = output_csv_file_default
        if not csv_file_path.endswith('.csv'):
            csv_file_path = csv_file_path+'.csv'

        print '%s INFO 13.BackupSize2HTML.py  Output is saving to: %s' % (dt.strftime(dformat), csv_file_path)
        app_logger.log_info('Output is saving to: %s' % csv_file_path)

        with open(csv_file_path, 'w') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(csv_contents)

        dt = datetime.now()
        print '%s INFO 13.BackupSize2HTML.py  Output is saved.' % dt.strftime(dformat)
        app_logger.log_info('Output is saved.')


def run_main():
    dt = datetime.now()
    if not default_page_title:
        print '%s WARNING 13.BackupSize2HTML.py  Default page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Default page title is not set!')

    if not os.path.isfile(history_file_path):
        print '%s ERROR 13.BackupSize2HTML.py  %s is not a valid file.' % (dt.strftime(dformat), history_file_path)
        app_logger.log_error('%s is not a valid file.' % history_file_path)
        print '%s INFO 13.BackupSize2HTML.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return
    try:
        int(report_size_count)
    except Exception,msg:
        print '%s ERROR 13.BackupSize2HTML.py  Invalid report size count found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Invalid report size count found in the config file.')
        print '%s INFO 13.BackupSize2HTML.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    try:
        int(variance_value)
    except Exception,msg:
        print '%s ERROR 13.BackupSize2HTML.py  Invalid variance value found in the config file.' % dt.strftime(dformat)
        app_logger.log_error('Invalid variance value found in the config file.')
        print '%s INFO 13.BackupSize2HTML.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    backupsize2htmlgenerator = BackupSize2HTMLGenerator()
    backupsize2htmlgenerator.generate_html()


def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

if __name__ == '__main__':
    dt = datetime.now()
    print '%s INFO 13.BackupSize2HTML.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 13.BackupSize2HTML.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 13.BackupSize2HTML.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 13.BackupSize2HTML.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 13.BackupSize2HTML.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
