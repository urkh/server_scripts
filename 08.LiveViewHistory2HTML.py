#! /usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
from datetime import datetime
import time
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('08.LiveViewHistory2HTML')

all_seq_file = config_vars.get('all_seq_file')
input_file_name = config_vars.get('input_file_name')
output_directory = config_vars.get('output_directory')

app_logger = LoggingManager('08.LiveViewHistory2HTML.py')

class HtmlGeneratorHistory:
    def __init__(self):
        pass

    def unix_time(self,dt):
        return int(time.mktime(dt.timetuple()))

    def get_static_html_part_upper(self,page_title):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

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
        html += """\n                        <li><a href="./liveview.html" class="selected">Live Views</a></li>"""
        html += """\n                        <li><a href="./historyview.html">History View</a></li>"""
        html += """\n                        <li><a href="./monthlyview.html">Monthly View</a></li>"""
        html += """\n                        <li><a href="./weeklyview.html">Weekly View</a></li>"""
        html += """\n                        <li><a href="./help.html">Help</a></li>"""
        html += """\n                    </ul>"""
        html += """\n                </nav>"""
        html += """\n    <div id='body'></div>"""
        html += """\n    <p>\n    </p>"""
        html += """<h4><td> <a class="2"href="javascript:history.go(-1);" STYLE="text-decoration: underline" >Back</a></h4>"""

        return html

    def read_static_html_part_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n    <p>\n    </p>"""
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

    def generate_html_page(self,input_file_name,output_directory,all_seq_file):
        def prepare_html_table_row(line):
            #policy01, bengreen,2014-06-17 03:02:33, 1, 2, 32, 0,LiveData
            line_split = line.split(',')
            col_three_value = line_split[2]

            time_stamp = col_three_value
            timestamp_error = False
            try:
                float(time_stamp)
            except Exception,msg:
                timestamp_error = True
            datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

            temp_datetime = datetime.strptime(datetime_str,'%Y-%m-%d %H:%M:%S')
            datetime_str = temp_datetime.strftime('%a %Y-%m-%d %H:%M:%S')

            col_four_val = line_split[3].strip()
            col_four_val_str = 'Misc'
            if col_four_val == '0':
                col_four_val_str = 'Full'
            elif col_four_val == '1' or col_four_val == '4':
                col_four_val_str = 'Incr'

            col_five_val = float(line_split[4])/3600
            col_five_val = '%.1f' % col_five_val

            col_six_val = float(line_split[5])/(1024*1024)
            col_six_val = '%.1f' % col_six_val

            col_seven_val = line_split[6]

            col_eight_value = line_split[7]
            time_stamp2 = col_eight_value
            timestamp2_error = False
            try:
                float(time_stamp2)
            except Exception,msg:
                timestamp2_error = True
            datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

            temp_datetime2 = datetime.strptime(datetime2_str,'%Y-%m-%d %H:%M:%S')
            datetime2_str = temp_datetime2.strftime('%a %Y-%m-%d %H:%M:%S')


            table_row = """\n<tr class="%s"><td> %s </td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s hours</td><td>%s GB</td><td>%s files</td></tr>""" % (col_four_val_str,line_split[0],line_split[1],datetime_str,datetime2_str,col_four_val_str,col_five_val,col_six_val,col_seven_val)
            return table_row

        all_sequences = []
        with open(all_seq_file,'r') as f:
            all_sequences = f.readlines()

        if not all_sequences:
            print 'No sequence found. File %s is empty.' % all_seq_file
            app_logger.log_error('No sequence data found. File %s is empty.' % all_seq_file)
            print 'Exiting program...'
            return

        all_sequences = [seq.split(',') for seq in all_sequences]

        remaining_sequence = all_sequences

        def check_sequence_in_all_sequence(seq_check,all_sequence):
            #seq_check = ['policy01','master']

            seq_matched = False
            for seq in all_sequences:
                #if seq[0].strip() == seq_check[0].strip() and seq[1].strip() == seq_check[1].strip():
                if seq[0].strip() == seq_check[0].strip() and seq[1].strip() == '-'.join(seq_check[1:]):
                    seq_matched = True
                    break

            if seq_matched:
                index_delete = -1
                for i,sq in enumerate(remaining_sequence):
                    #if sq[0].strip() == seq_check[0].strip() and sq[1].strip() == seq_check[1].strip():
                    if sq[0].strip() == seq_check[0].strip() and sq[1].strip() == '-'.join(seq_check[1:]):
                        index_delete = i
                        break
                if index_delete != -1:
                    del remaining_sequence[i]

            return seq_matched

        large_file = open(input_file_name,'r')
        last_line_read = 0

        for i,(last_line_read,lines,seq_name) in enumerate(self.read_sequence_in_chunks(large_file,last_line_read)):
            page_title = seq_name
            upper_html_part = self.get_static_html_part_upper(page_title)
            html_page = upper_html_part

            lines.sort(key=lambda line: int(line.split(',')[2].strip()) if not '-' in line[2] else self.unix_time(datetime.strptime(line.split(',').strip(),'%Y-%m-%d %H:%M:%S')),reverse=True)


            if check_sequence_in_all_sequence(seq_name.split('-'),all_sequences):
                """ Now generate the html table with the data. """

                html_table = """\n<table class="BackupData">"""
                html_table += """\n    <tr class="TopHeader"><td> Policy Name </td><td> Server Name</td><td>Backup Time</td><td>Backup Expiration Time</td><td>Schedule Type</td><td>Backup Elapsed Time</td><td>Backup Size</td><td> Number of Files</td></tr>"""

                for line in lines:
                    table_row = prepare_html_table_row(line)
                    html_table += table_row

                html_table += """\n</table>"""

                html_page += html_table
            else:
                html_page += """\n<div> No valid Backup exist for this policy </div>"""
                html_page += """\n<div> 1. This is a new created policy and no backup have been started or script didn't run yet - If a successful backup exist, please  wait the next refresh windows</div>"""
                html_page += """\n<div>2. All valid backup for this server in this policy  have expired due to unfixed long backup error or long inactive policy</div>"""

            html_page += self.read_static_html_part_lower()

            save_file_name = seq_name+'.html'
            with open(output_directory+save_file_name,'w') as of:
                of.write(html_page)

        
        for i, seq in enumerate(remaining_sequence):
            # import ipdb; ipdb.set_trace()
            page_title = seq[0].strip()+'-'+seq[1].strip()
            upper_html_part = self.get_static_html_part_upper(page_title)
            html_page = upper_html_part
            html_page += """\n<div>No valid Backup exist for this policy </div>"""
            html_page += """\n<div>1. This is a new created policy and no backup have been started or script didn't run yet - If a successful backup exist, please  wait the next refresh windows</div>"""
            html_page += """\n<div>2. All valid backup for this server in this policy  have expired due to unfixed long backup error or long inactive policy</div>"""
            html_page += self.read_static_html_part_lower()

            save_file_name = seq[0].strip()+'-'+seq[1].strip()+'.html'
            print 'Saving output to: %s' % (output_directory+save_file_name)
            app_logger.log_info('Saving output to: %s' % (output_directory+save_file_name))
            with open(output_directory+save_file_name,'w') as of:
                of.write(html_page)
        
        large_file.close()
        

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def run_main():
    html_generator_obj = HtmlGeneratorHistory()

    if not os.path.isfile(input_file_name):
        print '%s is not a valid file.' % input_file_name
        app_logger.log_error('%s is not a valid file.' % input_file_name)
        return

    if not os.path.isdir(output_directory):
        print '%s is not a valid directory.' % output_directory
        app_logger.log_error('%s is not a valid directory.' % output_directory)
        return

    if not os.path.isfile(all_seq_file):
        print '%s is not a valid file.' % all_seq_file
        app_logger.log_error('%s is not a valid file.' % all_seq_file)
        return

    try:
        html_generator_obj.generate_html_page(input_file_name,output_directory=output_directory,all_seq_file=all_seq_file)
    except Exception,msg:
        print 'Exception occured inside generate_html_page() method. Exception message: %s' % msg
        app_logger.log_error('Exception occured inside generate_html_page() method. Exception message: %s' % msg)

if __name__ == '__main__':
    print 'Program is starting...'
    app_logger.log_info('Program is starting...')
    print 'Started running...'
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    run_main()

    dt = datetime.now()
    end_time = unix_time(dt)

    print 'Time to run %s seconds.' % str(end_time-start_time)

    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print 'Ended running...'
    app_logger.log_info('Ended running...')
