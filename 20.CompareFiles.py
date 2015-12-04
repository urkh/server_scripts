#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import os
import os.path
from datetime import datetime
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

__author__ = 'urKh'

app_logger = LoggingManager('20.CompareFiles')
config_vars = GlobalConfig.read_vars('20.CompareFiles')

input_allseq_file = config_vars.get('input_allseq_file')
input_historyallsorted_file = config_vars.get('input_historyallsorted_file')
output_nopolicy_file = config_vars.get('output_nopolicy_file')


class CompareFiles:

    def process_data(self):
        temp_historyall = []
        temp_allseq = []

        allseq_file = open(input_allseq_file, 'r').readlines()
        historyallsorted_file = open(input_historyallsorted_file, 'r').readlines()

        [temp_historyall.append(row.split(',')[0].strip() + ', ' + row.split(',')[1].strip()) for row in historyallsorted_file]
        [temp_allseq.append(row.split(',')[0].strip() + ', ' + row.split(',')[1].strip()) for row in allseq_file]

        print '%s INFO 20.CompareFiles.py  Output is saving to %s' % (get_date(), output_nopolicy_file)
        app_logger.log_info('Output is saving to %s' % output_nopolicy_file)

        _file = open(output_nopolicy_file, 'a')

        for row in temp_historyall:
            if row not in temp_allseq:
                row += ', %s' % str(unix_time(datetime.now()))
                row += ', %s' % 'NoPolicy'
                print >> _file, row
                print '%s INFO 20.CompareFiles.py  Entered sequence %s' % (get_date(), row)
                app_logger.log_info('Entered sequence %s' % row)

        print '%s INFO 20.CompareFiles.py  Output saved.' % get_date()
        app_logger.log_info('Output saved.')


def unix_time(dt):
    return int(time.mktime(dt.timetuple()))


def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def run_main():
    if not os.path.isfile(input_allseq_file):
        print '%s ERROR 20.CompareFiles.py  %s is not a valid file.' % (get_date(), input_allseq_file)
        app_logger.log_error('%s is not a valid file.' % input_allseq_file)
        return
    if not os.path.isfile(input_historyallsorted_file):
        print '%s ERROR 20.CompareFiles.py  %s is not a valid file.' % (get_date(), input_historyallsorted_file)
        app_logger.log_error('%s is not a valid file.' % input_historyallsorted_file)
        return

    compare_files = CompareFiles()
    compare_files.process_data()

if __name__ == '__main__':
    print '%s INFO 20.CompareFiles.py  Program is starting...' % get_date()
    app_logger.log_info('Program is starting...')
    print '%s INFO 20.CompareFiles.py  Started running...' % get_date()
    app_logger.log_info('Started running...')
    print '%s INFO 20.CompareFiles.py  Start Generating nopolicy.txt...' % get_date()
    app_logger.log_info('Start Generating nopolicy.txt')

    start_time = unix_time(datetime.now())

    try:
        run_main()
    except:
        print '%s ERROR 20.CompareFiles.py  Script didn\'t complete successfully.' % get_date()
        app_logger.log_error('Script didn\'t complete successfully.')

    end_time = unix_time(datetime.now())

    print '%s INFO 20.CompareFiles.py  Time to run %s seconds.' % (get_date(), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 20.CompareFiles.py  Ended running...' % get_date()
    app_logger.log_info('Ended running...')
