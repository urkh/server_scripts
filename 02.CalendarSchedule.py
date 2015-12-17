#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import os.path
from datetime import datetime
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

__author__ = 'urKh'

app_logger = LoggingManager('02.ExtractInfo')
config_vars = GlobalConfig.read_vars('02.ExtractInfo')

input_policies_l_details = config_vars.get('policies_l_details_file')
output_extracted_info = config_vars.get('output_extracted_info')

class ExtractInfo(object):
    
    def process_data(self):

        new_class = False
        has_calendar = False
        policy_name = ''
        client = ''
        tmp_caldates = ''
        tmp_calmonth = ''
        tmp_calweek = ''
        tmp_pd = []
        tmp_policy_client = []

        policies_details = open(input_policies_l_details, 'r').readlines()

        for pd in policies_details:
            pd = pd.strip().split(' ')
            if pd[0] == 'CLASS' and new_class:
                for polcli in tmp_policy_client:
                    if has_calendar:
                        tmp_pd.append(['%s, %s %s %s' % (polcli, tmp_caldates, tmp_calweek, tmp_calmonth)])
                    else:
                        tmp_pd.append(['%s, NotCalendar' % polcli])
                
                has_calendar = False
                new_class = False
                tmp_policy_client = []
                tmp_caldates = ''
                tmp_calweek = ''
                tmp_calmonth = ''


            if pd[0] == 'CLASS' and not new_class:
                policy_name = pd[1]
                new_class = True
            elif pd[0] == 'CLIENT' and new_class:
                client = pd[1]
                tmp_policy_client.append('%s, %s' % (policy_name, client))
            elif pd[0] == 'SCHEDCALENDAR' and new_class:
                has_calendar = True
            elif pd[0] == 'SCHEDCALIDATES' and new_class:
                tmp_caldates = pd[0] + ' ' + ' '.join(pd[1:])
            elif pd[0] == 'SCHEDCALDAYOWEEK' and new_class:
                tmp_calweek = pd[0] + ' ' + pd[1]
            elif pd[0] == 'SCHEDCALDAYOMONTH' and new_class:
                tmp_calmonth = pd[0] + ' ' + ' '.join(pd[1:])

        # always check the last item
        for polcli in tmp_policy_client:
            if has_calendar:
                tmp_pd.append(['%s, %s %s %s' % (polcli, tmp_caldates, tmp_calweek, tmp_calmonth)])
            else:
                tmp_pd.append(['%s, NotCalendar' % polcli])

        # write definitive result in output file
        _file = open(output_extracted_info, 'w')
        for row in tmp_pd:
            print '%s INFO 02.ExtractInfo  Entered sequence for: %s, %s' % (get_date(), row[0].split(', ')[0], row[0].split(', ')[1])
            app_logger.log_info('Entered sequence for: %s, %s' % (row[0].split(', ')[0], row[0].split(', ')[1]))
            print >> _file, row[0].replace('  ', '')

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def run_main():
    if not os.path.isfile(input_policies_l_details):
        print '%s ERROR 02.CalendarSchedule.py  %s is not a valid file.' % (get_date(), input_policies_l_details)
        app_logger.log_error('%s is not a valid file.' % input_policies_l_details)
    extract_info = ExtractInfo()
    extract_info.process_data()

if __name__ == '__main__':
    print '%s INFO 02.CalendarSchedule.py  Program is starting...' % get_date()
    app_logger.log_info('Program is starting...')
    print '%s INFO 02.CalendarSchedule.py  Started running...' % get_date()
    app_logger.log_info('Started running...')
    print '%s INFO 02.CalendarSchedule.py  Start generatind calendar_schedule.txt'
    app_logger.log_info('Start generating calendar_schedule.txt')
    
    start_time = unix_time(datetime.now())

    try:
        run_main()
    except:
        print '%s ERROR 02.CalendarSchedule.py  Scrip\'t didnt complete successfully.' % get_date()
        app_logger.log_error('Script didn\'t complete successfully.')

    end_time = unix_time(datetime.now())

    print '%s INFO 02.CalendarSchedule.py  Saving output to: %s' % (get_date(), output_extracted_info)
    app_logger.log_info('Saving output to: %s' % output_extracted_info)
    print '%s INFO 02.CalendarSchedule.py  Time to run %s seconds.' % (get_date(), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds' % str(end_time-start_time))
    print '%s INFO 02.CalendarSchedule.py  Ended running...' % get_date()
    app_logger.log_info('Ended running...')


