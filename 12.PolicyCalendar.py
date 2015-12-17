#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
import re
import csv
import datetime
from datetime import datetime
from datetime import date
from datetime import timedelta
import calendar
from math import floor
import time
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('12.PolicyCalendar')

default_page_title = config_vars.get('default_page_title')
csv_report_file_path = config_vars.get('csv_report_file_path')
policy_calendar_file = config_vars.get('policy_calendar_file')
default_output_directory = config_vars.get('default_html_output_directory')
default_csv_directory = config_vars.get('default_csv_output_directory')
previous_month = config_vars.get('previous_month')
next_month = config_vars.get('next_month')
timetorun_file = config_vars.get('timetorun_file')

app_logger = LoggingManager('12.PolicyCalendar2HTML.py')
dformat = '%Y-%m-%d %H:%M:%S'

class PolicyCalendarHTMLGenerator:
    def __init__(self):
        pass

    def get_static_html_part_upper(self,page_title,csv_report_file_name):

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
        html += """\n        <tbody>"""
        html += """\n            <tr>"""
        html += """\n              <td> Last Updated:<br>"""+str(timenow)+""" </td>"""
        html += """\n            </tr>"""
        html += """\n        </tbody>"""
        html += """\n    </table>"""
        html += """\n    <div id='logo'>\n        <header>\n            <div id='header'></div>\n            <div>"""
        html += """\n                    <img src="img/version.png" alt="version logo" id="version"/>\n            </div>"""
        html += """\n        </header>\n                </div>\n                <nav>\n                    <ul id="menubar">"""
        html += """\n                        <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n                        <li><a href="./reports.html">Reports</a></li>"""
        html += """\n                        <li><a href="./policyconfig.html" class="selected">Policy Config</a></li>"""
        html += """\n                        <li><a href="./backupsize.html">Backup Size</a></li>"""
        html += """\n                        <li><a href="./files.html">Files</a></li>"""
        html += """\n                        <li><a href="./billing.html">Billing</a></li>"""
        html += """\n                        <li><a href="./help.html">Help</a></li>"""
        html += """\n                    </ul>"""
        html += """\n                </nav>"""
        html += """\n    <div id='body'></div>"""
        html += """\n    <p>\n    <a href='""" + csv_report_file_name + """' style="text-decoration: underline; float: right";>csv download</a>\n    </p>"""

        return html

    def generate_data_table(self,policy_name,previous_month,next_month,calendar_date_data): #policy_name = policy22,  calendar_date_data = SCHEDCALDAYOWEEK 1,1;6,1;4,2;4,3;5,4;7,5

        def split_calander_row_third_col(third_col_val):
            titles = ['SCHEDCALIDATES','SCHEDCALDAYOWEEK','SCHEDCALDAYOMONTH']
            third_col_val_split = third_col_val.split(' ')
            values_split = {}
            current_title = None
            for i, val in enumerate(third_col_val_split):
                if val in titles:
                    current_title = val
                    continue
                if current_title:
                    if values_split.get(current_title):
                        values_split[current_title] += [val]
                    else:
                        values_split[current_title] = [val]

            return values_split

        def week_of_month(dt):
            """ Returns the week of the month for the specified date.
            """
            first_day = dt.replace(day=1)

            dom = dt.day

            adjusted_dom = dom + first_day.weekday()

            return int(floor(adjusted_dom/7.0))

        def adjust_tdays_day(day):
            if day == 6: ###if day is sunday. calendar week starts from monday = 0. so sunday is 6 here.
                return 1
            elif day == 0: ###if day is monday
                return 2
            elif day == 1: ###if day is tuesday.
                return 3
            elif day == 2: ###if day is wednesday.
                return 4
            elif day == 3: ###if day is thursday.
                return 5
            elif day == 4: ###if day is friday.
                return 6
            elif day == 5: ###if day is saturday.
                return 7

        def get_todays_day_week_pair():
            tday = datetime.now()
            tday_day = tday.weekday()
            week_month = week_of_month(tday)
            adjusted_day = adjust_tdays_day(tday_day)
            return adjusted_day,week_month

        def adjust_day_reverse(day):
            if day == 1:
                return 6
            elif day == 2:
                return 0
            elif day == 3:
                return 1
            elif day == 4:
                return 2
            elif day == 5:
                return 3
            elif day == 6:
                return 4
            elif day == 7:
                return 5

        def describe_day(day):
            if day == 1:
                return 'Sunday'
            elif day == 2:
                return 'Monday'
            elif day == 3:
                return 'Tuesday'
            elif day == 4:
                return 'Wednesday'
            elif day == 5:
                return 'Thursday'
            elif day == 6:
                return 'Friday'
            elif day == 7:
                return 'Saturday'

        def describe_day_of_week_month(year,month):
            cal = calendar.Calendar()
            month_cal = cal.monthdayscalendar(year,month)
            month_description = {
                'Sunday':{},
                'Monday':{},
                'Tuesday':{},
                'Wednesday':{},
                'Thursday':{},
                'Friday':{},
                'Saturday':{}
            }

            day_occurrance_count = {
                'Sunday':0,
                'Monday':0,
                'Tuesday':0,
                'Wednesday':0,
                'Thursday':0,
                'Friday':0,
                'Saturday':0
            }

            for week_no, week in enumerate(month_cal):
                for week_day, date_day in enumerate(week):
                    if date_day != 0:
                        week_day_description = None
                        if week_day == 0: ###Monday
                            week_day_description = 'Monday'
                        elif week_day == 1:
                            week_day_description = 'Tuesday'
                        elif week_day == 2:
                            week_day_description = 'Wednesday'
                        elif week_day == 3:
                            week_day_description = 'Thursday'
                        elif week_day == 4:
                            week_day_description = 'Friday'
                        elif week_day == 5:
                            week_day_description = 'Saturday'
                        elif week_day == 6:
                            week_day_description = 'Sunday'
                        if week_day_description:
                            day_occurance_cnt = day_occurrance_count[week_day_description] + 1
                            day_occurrance_count[week_day_description] = day_occurance_cnt
                            month_description[week_day_description][day_occurance_cnt] = date(day=date_day,month=month,year=year)

            return month_description


        def calculate_months(previous_month,next_month):
            tday_datetime = datetime.now()

            previous_months = []
            next_months = []

            temp_datetime = tday_datetime
            for i in range(previous_month):
                first_day_of_month = date(day=1,month=temp_datetime.month,year=temp_datetime.year)
                prev_month = first_day_of_month + timedelta(days=-1)
                previous_months += [prev_month]
                temp_datetime = prev_month

            temp_datetime = tday_datetime
            for i in range(next_month):
                lst_day = calendar.monthrange(temp_datetime.year,temp_datetime.month)
                last_day_of_month = date(day=lst_day[1],month=temp_datetime.month,year=temp_datetime.year)
                nxt_month = last_day_of_month + timedelta(days=1)
                next_months += [nxt_month]
                temp_datetime = nxt_month

            all_months = previous_months + [tday_datetime.date()] + next_months
            return all_months

        def find_calendar_day_of_week_dates(previous_month,next_month,value):
            dates = []
            month_data = {}
            tday_datetime = datetime.now()

            all_months = calculate_months(previous_month,next_month)

            for i,each_date in enumerate(all_months):

                current_month_description = describe_day_of_week_month(each_date.year,each_date.month)

                dtd = each_date

                last_day = calendar.monthrange(dtd.year,dtd.month)

                dates_in_ranges = [date(day=i + 1,month=dtd.month, year=dtd.year) for i in range(last_day[1])]

                day_week_pairs = [(dt.weekday(),week_of_month(dt)) for dt in dates_in_ranges]

                def find_wdate_by_index(index):
                    for ii, ddate in enumerate(dates_in_ranges):
                        if ii == index:
                            return ddate

                for index, dayweek_pair in enumerate(value):
                    dayweek_list = dayweek_pair.split(';')
                    for each_pair in dayweek_list:
                        day_week = each_pair.split(',')
                        day = int(day_week[0])
                        week = int(day_week[1])

                        day_name = describe_day(day)

                        wdate = current_month_description[day_name].get(week)

                        if week == 5:
                            max_key = max(k for k, v in current_month_description[day_name].iteritems())
                            wdate = current_month_description[day_name].get(max_key)

                        if wdate:
                            day_val_int = wdate.day
                            target_last_day = calendar.monthrange(wdate.year,wdate.month)
                            if target_last_day[1] == day_val_int:
                                last_day = calendar.monthrange(each_date.year,each_date.month)
                                day_val_int = last_day[1]

                            wdate = date(day=day_val_int,month=each_date.month,year=each_date.year)
                            row_data = []
                            month_name = wdate.strftime('%B')
                            row_data += [month_name]
                            row_data += ['DAY OF WEEK']
                            row_data += [describe_day(day) +', Week '+ str(week)]
                            row_data += [wdate.strftime('%a %Y-%m-%d')]
                            if month_data.get(month_name):
                                month_data[month_name] += [row_data]
                            else:
                                month_data[month_name] = [row_data]
            dates += [month_data]
            return dates

        def find_calendar_day_of_month_dates(previous_month,next_month,value):
            dates = []
            month_data = {}
            tday_datetime = datetime.now()

            all_months = calculate_months(previous_month,next_month)

            today_day = tday_datetime.day
            value = [int(val) for val in value]
            max_int_val = max(value)

            for i, each_date in enumerate(all_months):
                for index,day in enumerate(value):
                    val_int = int(day)
                    if val_int == 32:
                        last_day = calendar.monthrange(each_date.year,each_date.month)
                        val_int = last_day[1]
                    dtt = date(day=val_int,month=each_date.month,year=each_date.year)
                    row_data = []
                    month_name = dtt.strftime('%B')
                    row_data += [month_name]
                    row_data += ['DAY OF MONTH']
                    row_data += [str(val_int)]
                    row_data += [dtt.strftime('%a %Y-%m-%d')]
                    if month_data.get(month_name):
                        month_data[month_name] += [row_data]
                    else:
                        month_data[month_name] = [row_data]

            dates += [month_data]

            return dates

        def find_calendar_day_of_specific_dates(previous_month,next_month,value):
            dates = []
            month_data = {}
            tday_datetime = datetime.now()
            all_months = calculate_months(previous_month,next_month)

            previous_min_month = min(all_months)

            previous_min_month = date(day=1,month=previous_min_month.month,year=previous_min_month.year)

            next_max_month = max(all_months)

            next_month_last_day = calendar.monthrange(next_max_month.year,next_max_month.month)

            next_max_month = date(day=next_month_last_day[1],month=next_max_month.month,year=next_max_month.year)

            for index,each_tstamp in enumerate(value):
                target_datetime = datetime.fromtimestamp(int(each_tstamp))
                target_date = target_datetime.date()

                if target_date >= previous_min_month and target_date <= next_max_month:
                    row_data = []
                    month_name = target_date.strftime('%B')
                    row_data += [month_name]
                    row_data += ['SPECIFIC DATE']
                    row_data += ['No '+str(index)]
                    row_data += [target_date.strftime('%a %Y-%m-%d')]
                    if month_data.get(month_name):
                        month_data[month_name] += [row_data]
                    else:
                        month_data[month_name] = [row_data]
            dates += [month_data]
            return dates

        def calendar_values_to_dates(previous_month,next_month,third_col_val_dict):

            #Calendar Date Format:
            # SPECIFIC DATE 0 - 07/01/2014 for SCHEDCALIDATES
            #DAY OF WEEK - Sunday, Week 1 - 08/27/2014 for SCHEDCALDAYOWEEK
            #DAY OF MONTH - 1 - 08/01/2014 for SCHEDCALDAYOMONTH

            all_dates = {}

            for key,value in third_col_val_dict.items():
                if key == 'SCHEDCALIDATES':
                    dates = find_calendar_day_of_specific_dates(previous_month,next_month,value)
                    all_dates[key] = dates

                elif key == 'SCHEDCALDAYOWEEK':
                    dates = find_calendar_day_of_week_dates(previous_month,next_month,value)
                    all_dates[key] = dates

                elif key == 'SCHEDCALDAYOMONTH':
                    dates = find_calendar_day_of_month_dates(previous_month,next_month,value)
                    all_dates[key] = dates

            return all_dates

        html = """"""

        calendar_values = split_calander_row_third_col(calendar_date_data)

        calendar_dates = calendar_values_to_dates(previous_month,next_month,calendar_values)

        temp_dates_list = []

        for calendar_title,values in calendar_dates.items():

            for i, row_data_month_dict in enumerate(values):
                #print row_data_month_dict
                for j,(key, row_data_list) in enumerate(row_data_month_dict.items()):
                    temp_dates_list += row_data_list

        ##Now sort.

        for i in range(len(temp_dates_list)):
            #a = len(temp_dates_list)
            for j in range(len(temp_dates_list) - 1 - i):
                temp_rowj = temp_dates_list[j]
                temp_datej = datetime.strptime(temp_rowj[3],'%a %Y-%m-%d')
                temp_rowj1 = temp_dates_list[j + 1]
                temp_datej1 = datetime.strptime(temp_rowj1[3],'%a %Y-%m-%d')
                if temp_datej > temp_datej1:
                    temp_dates_list[j], temp_dates_list[j + 1] = temp_dates_list[j + 1], temp_dates_list[j]

        nearest_next_date = None

        todays_date = datetime.now().date()

        for date_row in temp_dates_list:
            temp_date = datetime.strptime(date_row[3],'%a %Y-%m-%d')
            temp_date = temp_date.date()
            if temp_date >= todays_date:
                if nearest_next_date:
                    if temp_date < nearest_next_date:
                        nearest_next_date = temp_date
                else:
                    nearest_next_date = temp_date

        class_name = "polconfig1"

        html_table = """\n<table class="BackupData2">"""
        html_table += """\n <tbody>"""
        html_table += """\n     <tr><td class="polconfighead">Month</td><td class="polconfighead">Type</td>"""
        html_table += """\n          <td class="polconfighead">Schedule</td><td class="polconfighead">Dates</td></tr>"""

        for indx,row in enumerate(temp_dates_list):
            table_row = """\n       <tr>"""
            temp_class_name = class_name
            try:
                converted_date =  datetime.strptime(row[3],'%a %Y-%m-%d')
                converted_date = converted_date.date()
                if nearest_next_date:
                    if converted_date == nearest_next_date:
                        class_name = 'polconfignext'
            except Exception,msg:
                print 'Exception occured while converting date str to date object.'
                pass
            table_row += """\n          <td class=\"""" + class_name + """\">""" + row[0] + """</td>"""
            table_row += """\n          <td class=\"""" + class_name + """\">""" + row[1] + """</td>"""
            table_row += """\n          <td class=\"""" + class_name + """\">""" + row[2] + """</td>"""
            table_row += """\n          <td class=\"""" + class_name + """\">""" + row[3] + """</td>"""
            class_name = temp_class_name
            table_row += """\n      </tr>"""
            html_table += table_row
            month_name = row[0]
            if len(temp_dates_list) >= indx + 2:
                if temp_dates_list[indx][0] != temp_dates_list[indx + 1][0]:
                    if class_name == 'polconfig1':
                        class_name = 'polconfig2'
                    else:
                        class_name = 'polconfig1'

        html_table += """\n <tbody>"""
        html_table += """\n</table>"""
        html += html_table

        return html,calendar_dates

    def read_static_html_part_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')

        html = """\n    <p>\n    </p>"""
        html += """\n    <p>\n    </p>"""
        html += """\n    <p>"""+str(timenow)+"""\n    </p>"""
        html += """\n    </body>\n</html>"""
        return html

    def generate_html(self,page_title,csv_report_file_path,policy_name,policy_calendar_data,previous_month,next_month):
        html = """"""
        csv_report_file_path = csv_report_file_path + policy_name+'-calendar.csv'
        html += self.get_static_html_part_upper(page_title,csv_report_file_path)
        html_data,calendar_dates = self.generate_data_table(policy_name,previous_month,next_month,policy_calendar_data)
        html += html_data
        html += self.read_static_html_part_lower()
        return html,calendar_dates



def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def run_main():
    dt = datetime.now()
    if not default_page_title:
        print '%s WARNING 12.PolicyCalendar.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set!')

    if not os.path.isfile(policy_calendar_file):
        print '%s ERROR 12.PolicyCalendar.py  %s is not a valid file.' % (dt.strftime(dformat), policy_calendar_file)
        app_logger.log_error('%s is not a valid file.' % policy_calendar_file)
        print '%s INFO 12.PolicyCalendar.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    try:
        int(previous_month)
    except Exception,msg:
        print '%s ERROR 12.PolicyCalendar.py  A valid previous month value is needed.' % dt.strftime(dformat)
        app_logger.log_error('A valid previous month value is needed.')
        print '%s INFO 12.PolicyCalendar.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    try:
        int(next_month)
    except Exception,msg:
        print '%s ERROR 12.PolicyCalendar.py  A valid next month value is needed.' % dt.strftime(dformat)
        app_logger.log_error('A valid next month value is needed.')
        print '%s INFO 12.PolicyCalendar.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    print '%s INFO 12.PolicyCalendar.py  Previous month value found: %s' % (dt.strftime(dformat), previous_month)
    app_logger.log_info('Previous month value found: %s' % previous_month)

    print '%s INFO 12.PolicyCalendar.py  Next month value found: %s' % (dt.strftime(dformat), next_month)
    app_logger.log_info('Next month value found: %s' % next_month)

    if not os.path.exists(default_output_directory):
        os.makedirs(default_output_directory)

    if not os.path.exists(default_csv_directory):
        os.makedirs(default_csv_directory)

    previous_month_count = int(previous_month)
    next_month_count = int(next_month)

    policy_calendar_data = []
    with open(policy_calendar_file,'r') as cf:
        policy_calendar_data = cf.readlines()

    policy_calender_data_dict = {}

    for i, line in enumerate(policy_calendar_data):
        line = line.replace('\n','')
        line_split = line.split(',')
        policy_name = line_split[0].strip()
        calendar_type = line_split[1].strip()
        if calendar_type != 'NotCalendar':
            policy_calender_data_dict[policy_name] = line.replace(policy_name+',','').strip()

    policy_calendar_html_generator = PolicyCalendarHTMLGenerator()

    for policy_name, calendar_data in policy_calender_data_dict.items():
        policy_calendar_html_table,calendar_dates = policy_calendar_html_generator.generate_html(default_page_title,csv_report_file_path,policy_name,calendar_data,previous_month_count,next_month_count)
        file_name = policy_name+'-calendar.html'
        dt = datetime.now()
        print '%s INFO 12.PolicyCalendar.py  Output is saving to: %s' % (dt.strftime(dformat), os.path.join(default_output_directory,file_name))
        app_logger.log_info('Output is saving to: %s' % os.path.join(default_output_directory,file_name))
        with open(os.path.join(default_output_directory,file_name),'w') as f:
            f.write(policy_calendar_html_table)
        
        dt = datetime.now()
        print '%s INFO 12.PolicyCalendar.py  Ouput is saved.' % dt.strftime(dformat)
        app_logger.log_info('Output is saved.')

        date_values = [['Month','Type','Schedule','Dates']]
        for calendar_type, values in calendar_dates.items():
            for data_dict in values:
                for month_name, month_data_list in data_dict.items():
                    for row_data in month_data_list:
                        date_values += [row_data]

        csv_file_name = policy_name+'-calendar.csv'

        dt = datetime.now()
        print '%s INFO 12.PolicyCalendar.py  Output is saving to: %s' % (dt.strftime(dformat), os.path.join(default_csv_directory,csv_file_name))
        app_logger.log_info('Output is saving to: %s' % os.path.join(default_csv_directory,csv_file_name))

        with open(os.path.join(default_csv_directory,csv_file_name), 'w') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(date_values)

        dt = datetime.now()
        print '%s INFO 12.PolicyCalendar.py  Output is saved.' % dt.strftime(dformat)
        app_logger.log_info('Output is saved.')


if __name__ == "__main__":
    dt = datetime.now()
    print '%s INFO 12.PolicyCalendar.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 12.PolicyCalendar.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 12.PolicyCalendar.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 12.PolicyCalendar.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 12.PolicyCalendar.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
