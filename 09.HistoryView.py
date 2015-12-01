#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

from datetime import datetime
import time
import sys
import os
import os.path
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('09.HistoryView')

DATA_AGE_IN_YEARS = config_vars.get('data_age_in_years')
HISTORY_DATA_FILE = config_vars.get('history_data_file')
HISTORY_ALL_DATA_FILE = config_vars.get('history_all_data_file')
OUTPUT_DATA_FILE = config_vars.get('output_data_file')
EXISTING_POLICIES_FILE = config_vars.get('existing_policies_file')
POLICIES_ARCHIVED = config_vars.get('policies_archived')

app_logger = LoggingManager('09.HistoryView.py')
dformat = '%Y-%m-%d %H:%M:%S'

class History3ViewBackup:
    def __init__(self):
        pass

    def unix_time(self,dt):
        return int(time.mktime(dt.timetuple()))

    def get_diff_in_year(self,time_in_mills):
        if '-' in time_in_mills:
            dt = datetime.strptime(time_in_mills,'%Y-%m-%d %H:%M:%S')
            return dt.year - datetime.now().year
        else:
            return datetime.fromtimestamp(int(time_in_mills)).year - datetime.now().year

    def read_in_chunks(self,file_object, last_line_read =0):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            file_object.seek(last_line_read)
            data = file_object.readline()

            last_line_read = last_line_read + len(data)
            if not data:
                break
            yield last_line_read,data

    def reformat_line(self,line):
        #policy01, bengreen,2014-06-16 06:21:29, 0, 2, 32, 6,LiveData
        line_split = line.split(',')
        formatted_line_split = []
        formatted_line_split += [line_split[0]]
        formatted_line_split += [line_split[1]]
        dt = datetime.strptime(line_split[2],'%Y-%m-%d %H:%M:%S')
        formatted_line_split += [' '+str(self.unix_time(dt))]
        formatted_line_split += [line_split[3]]
        formatted_line_split += [line_split[4]]
        formatted_line_split += [line_split[5]]
        formatted_line_split += [line_split[6]]
        dt = datetime.strptime(line_split[7],'%Y-%m-%d %H:%M:%S')
        formatted_line_split += [' '+str(self.unix_time(dt))]
        return ','.join(formatted_line_split)

    def start_processing(self):

        dt = datetime.now()
        existing_policies = []
        with open(EXISTING_POLICIES_FILE,'r') as ef:
            existing_policies = ef.readlines()

        if not existing_policies:
            print '%s ERROR 09.HistoryView.py  No data is found on %s' % (dt.strftime(dformat), EXISTING_POLICIES_FILE)
            app_logger.log_error('No data is found on %s' % EXISTING_POLICIES_FILE)
            print 'Exiting program...'
            return

        existing_policies = [p.replace('\n','') for p in existing_policies]

        archived_policies_file = open(POLICIES_ARCHIVED,'a')

        archived_file_empty = False
        if os.stat(POLICIES_ARCHIVED)[6]==0:
            print '%s INFO 09.HistoryView.py  Archive is Empty' % dt.strftime(dformat)
            app_logger.log_info('Archive is Empty')
            archived_file_empty = True
        else:
            print '%s INFO 09.HistoryView.py  Archive is not Empty' % dt.strftime(dformat)
            app_logger.log_info('Archive is not Empty')
            archived_file_empty = False

        cr_appended_archived = False

        input_data = []
        with open(HISTORY_DATA_FILE,'r') as input_file:
            input_data = input_file.readlines()

        if not input_data:
            print '%s ERROR 09.HistoryView.py  History data file is empty.' % dt.strftime(dformat)
            app_logger.log_error('History data is empty on %s' % HISTORY_DATA_FILE)
            
            print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
            app_logger.log_info('Exiting program...')
            return

        temp = []
        for i in input_data:
            i = i.replace('\n','')
            data_split = i.split(',')
            temp += [','.join(data_split)]

        input_data = temp

        input_data = list(set(input_data))

        large_file = open(HISTORY_ALL_DATA_FILE,'r')

        output_file = open(OUTPUT_DATA_FILE,'w')

        last_line_read = 0

        additional_rows = input_data

        for i,(last_line_read,line) in enumerate(self.read_in_chunks(large_file,last_line_read)):
            lsplit = line.split(',')
            policy_name = lsplit[0].strip()

            if policy_name in existing_policies:
                file_data_line = ''
                data_age = self.get_diff_in_year(line.split(',')[2])
                line = line.replace('\n','')
                if data_age < DATA_AGE_IN_YEARS:
                    line = self.reformat_line(line)
                    if line in input_data:
                        line = line.replace('\n','')
                        line_split = line.split(',')

                        time_stamp = line_split[2]
                        timestamp_error = False
                        try:
                            float(time_stamp)
                        except Exception,msg:
                            timestamp_error = True
                        datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

                        line_split[2] = str(datetime_str)

                        time_stamp2 = line_split[7]
                        timestamp2_error = False
                        try:
                            float(time_stamp2)
                        except Exception,msg:
                            timestamp2_error = True
                        datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

                        line_split[7] = datetime2_str

                        line_split[2] = str(datetime_str)

                        modified_line_split = line_split

                        if len(line_split) == 8:
                            modified_line_split += ['LiveData\n']
                        else:
                            modified_line_split[8] = 'LiveData\n'
                        file_data_line = ','.join(modified_line_split)
                        if line in additional_rows:
                            additional_rows.remove(line)
                    else:
                        line = line.replace('\n','')
                        line_split = line.split(',')

                        time_stamp = line_split[2]
                        timestamp_error = False
                        try:
                            float(time_stamp)
                        except Exception,msg:
                            timestamp_error = True
                        datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

                        time_stamp2 = line_split[7]
                        timestamp2_error = False
                        try:
                            float(time_stamp2)
                        except Exception,msg:
                            timestamp2_error = True
                        datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

                        line_split[7] = datetime2_str

                        line_split[2] = str(datetime_str)

                        modified_line_split = line_split
                        if len(line_split) == 8:
                            modified_line_split += ['ExpiredData\n']
                        else:
                            modified_line_split[8] = 'ExpiredData\n'
                        file_data_line = ','.join(modified_line_split)

                if file_data_line:
                    output_file.writelines(file_data_line)

            else:

                line = line.replace('\n','')
                if line:
                    line_split = line.split(',')

                    time_stamp = line_split[2]
                    timestamp_error = False
                    try:
                        float(time_stamp)
                    except Exception,msg:
                        timestamp_error = True
                    datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

                    line_split[2] = str(datetime_str)

                    time_stamp2 = line_split[7]
                    timestamp2_error = False
                    try:
                        float(time_stamp2)
                    except Exception,msg:
                        timestamp2_error = True
                    datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

                    line_split[7] = datetime2_str

                    line = ','.join(line_split)

                    l = line.replace('\n','')+','+' ArchivedData\n'

                    if not archived_file_empty and not cr_appended_archived:
                        l = '\r'+l
                        archived_file_empty = False
                        cr_appended_archived = True

                    archived_policies_file.writelines(l)


        for l in additional_rows:
            policy_name = ''
            if l:
                policy_name = l.split(',')[0]
                policy_name = policy_name.strip()
            if policy_name in existing_policies:
                line_split = l.split(',')
                time_stamp = line_split[2]
                timestamp_error = False
                try:
                    float(time_stamp)
                except Exception,msg:
                    timestamp_error = True
                datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

                line_split[2] = str(datetime_str)

                time_stamp2 = line_split[7]
                timestamp2_error = False
                try:
                    float(time_stamp2)
                except Exception,msg:
                    timestamp2_error = True
                datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

                line_split[7] = datetime2_str

                line_split[2] = str(datetime_str)

                t = ','.join(line_split)

                l = t.replace('\n','')+','+'LiveData\n'
                output_file.writelines(l)
            else:
                l = l.replace('\n','')
                if l:
                    line_split = l.split(',')

                    time_stamp = line_split[2]
                    timestamp_error = False
                    try:
                        float(time_stamp)
                    except Exception,msg:
                        timestamp_error = True
                    datetime_str = str(datetime.fromtimestamp(float(time_stamp))) if not timestamp_error else time_stamp

                    line_split[2] = str(datetime_str)

                    time_stamp2 = line_split[7]
                    timestamp2_error = False
                    try:
                        float(time_stamp2)
                    except Exception,msg:
                        timestamp2_error = True
                    datetime2_str = str(datetime.fromtimestamp(float(time_stamp2))) if not timestamp2_error else time_stamp2

                    line_split[7] = datetime2_str

                    l = ','.join(line_split)

                    l = l.replace('\n','')+','+' ArchivedData\n'

                    if not archived_file_empty and not cr_appended_archived:
                        l = '\r'+l
                        archived_file_empty = False
                        cr_appended_archived = True

                    archived_policies_file.writelines(l)

        #archived_policies_file.writelines('\r')

        archived_policies_file.close()
        large_file.close()
        output_file.close()

        """ Now delete old historyall.txt file and rename history_all_updated.txt to historyall.txt """
        history_all_file = os.path.join(os.getcwd(),HISTORY_ALL_DATA_FILE)
        history_updated_file = os.path.join(os.getcwd(),OUTPUT_DATA_FILE)
        dt = datetime.now()
        print '%s INFO 09.HistoryView.py  %s file is updated.' % (dt.strftime(dformat), HISTORY_ALL_DATA_FILE)
        app_logger.log_info('%s file is updated.' % HISTORY_ALL_DATA_FILE)

        try:
            os.remove(history_all_file)
            os.rename(history_updated_file,history_all_file)
        except Exception,msg:
            print '%s ERROR 09.HistoryView.py  Exception occured while deleting and renaming files.' % dt.strftime(dformat)
            print msg
            app_logger.log_error('Exception occured while deleting and renaming files.')

def run_main():


    dt = datetime.now()

    try:
        DATA_AGE_IN_YEARS = int(config_vars.get('data_age_in_years'))
    except Exception,msg:
        print '%s ERROR 09.HistoryView.py  Exception occured with value %s' % (dt.strftime(dformat), str(DATA_AGE_IN_YEARS))
        app_logger.log_error('Exception occured with value %s. Exception message: %s' % (str(DATA_AGE_IN_YEARS),str(msg)))
        
        print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(HISTORY_DATA_FILE):
        print '%s ERROR 09.HistoryView.py  %s is not a valid file.' % (dt.strftime(dformat), HISTORY_DATA_FILE)
        app_logger.log_error('%s is not a valid file.' % HISTORY_DATA_FILE)
        
        print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(HISTORY_ALL_DATA_FILE):
        print '%s ERROR 09.HistoryView.py  %s is not a valid file.' % (dt.strftime(dformat), HISTORY_ALL_DATA_FILE)
        app_logger.log_error('%s is not a valid file.' % HISTORY_ALL_DATA_FILE)
        
        print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(EXISTING_POLICIES_FILE):
        print '%s ERROR 09.HistoryView.py  %s is not a valid file.' % (dt.strftime(dformat), EXISTING_POLICIES_FILE)
        app_logger.log_error('%s is not a valid file.' % EXISTING_POLICIES_FILE)
        
        print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(POLICIES_ARCHIVED):
        print '%s ERROR 09.HistoryView.py  %s is not a valid file.' % (dt.strftime(dformat), POLICIES_ARCHIVED)
        app_logger.log_error('%s is not a valid file.' % POLICIES_ARCHIVED)
        
        print '%s INFO 09.HistoryView.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    history3_view_backup_obj = History3ViewBackup()
    try:
        history3_view_backup_obj.start_processing()
    except Exception,msg:
        print '%s ERROR 09.HistoryView.py  Exception occured in start_processing() method. Exception message: %s' % (dt.strftime(dformat), str(msg))
        app_logger.log_error('Exception occured in start_processing() method. Exception message: %s' % str(msg))

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

if __name__ == '__main__':
    dt = datetime.now()
    print '%s INFO 09.HistoryView.py  Start Generating historyall.txt...' % dt.strftime(dformat)
    app_logger.log_info('Start Generating historyall.txt...')
    
    #print 'Start Generating historyall.txt...'
    #app_logger.log_info('Start Generating historyall.txt...')
    
    dt = datetime.now()
    start_time = unix_time(dt)
    
    try:
        run_main()
    except:
        dt = datetime.now()
        print '%s ERROR 09.HistoryView.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete successfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 09.HistoryView.py  Time to run %s seconds' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 09.HistoryView.py  End Generating historyall.txt' % dt.strftime(dformat)
    app_logger.log_info('End Generating historyall.txt')
