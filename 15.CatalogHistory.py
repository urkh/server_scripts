#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Codengine'

from datetime import datetime
import time
import os

from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('15.CatalogHistory')

dashboard_catalog_live_file_path = config_vars.get('dashboard_catalog_live_file_path')
dashboard_catalog_all_file_path = config_vars.get('dashboard_catalog_all_file_path')
dashboard_catalog_tmp_file_path = config_vars.get('dashboard_tmp_file_path')

app_logger = LoggingManager('15.CatalogHistory.py')
dformat = '%Y-%m-%d %H:%M:%S'

class CatalogHistory:
    def __init__(self):
        pass

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

    def process_data(self):
        dashboard_catalog_all_file = open(dashboard_catalog_all_file_path,'r')

        dashboard_catalog_live_data = []

        with open(dashboard_catalog_live_file_path,'r') as f:
            dashboard_catalog_live_data = f.readlines()

        temp_live_data = []

        for line in dashboard_catalog_live_data:
            line = line.strip().replace('\n','')
            if line:
                temp_live_data += [line]

        dashboard_catalog_live_data = temp_live_data

        with open(dashboard_catalog_tmp_file_path,'w') as f:
            pass

        output_temp_file = open(dashboard_catalog_tmp_file_path,'a+')

        additional_lines = dashboard_catalog_live_data

        last_line_read = 0

        for i,(last_line_read,line) in enumerate(self.read_in_chunks(dashboard_catalog_all_file,last_line_read)):

            line = line.replace('\n','').strip()

            if line:
                line_split = line.split(',')
                last_colmn = line_split[len(line_split)-1]
                if last_colmn == 'LiveData' or last_colmn == 'ExpiredData':
                    modified_line_split = line_split[:-1]
                    line = ','.join(modified_line_split)

                if line in dashboard_catalog_live_data:
                    modified_line = line+','+'LiveData'
                    dashboard_catalog_live_data.remove(line)
                else:
                    modified_line = line+','+'ExpiredData'

                output_temp_file.write(modified_line+'\n')

        for aline in additional_lines:
            output_temp_file.write(aline+','+'LiveData\n')

        output_temp_file.close()
        dashboard_catalog_all_file.close()

        dt = datetime.now()

        print '%s INFO 15.CatalogHistory.py  Output is saved to a temporary file: %s' % (dt.strftime(dformat), dashboard_catalog_tmp_file_path)
        app_logger.log_info('Output is saved to a temporary file: %s' % dashboard_catalog_tmp_file_path)

        """ Now delete old dashboard-catalog-live.txt file and rename dashboard-catalog-all-temp.txt to dashboard-catalog-all.txt """
        try:
            #import ipdb; ipdb.set_trace()
            print '%s INFO 15.CatalogHistory.py  Delete file: %s' % (dt.strftime(dformat), dashboard_catalog_all_file_path)
            app_logger.log_info('Delete file: %s' % dashboard_catalog_all_file_path)
            os.remove(dashboard_catalog_all_file_path)
            print '%s INFO 15.CatalogHistory.py  Rename %s to %s' % (dt.strftime(dformat), dashboard_catalog_tmp_file_path,dashboard_catalog_all_file_path)
            app_logger.log_info('Rename %s to %s' % (dashboard_catalog_tmp_file_path,dashboard_catalog_all_file_path))
            os.rename(dashboard_catalog_tmp_file_path,dashboard_catalog_all_file_path)
        except Exception,msg:
            print '%s ERROR 15.CatalogHistory.py  Exception occured while deleting and renaming files.' % dt.strftime(dformat)
            print msg
            app_logger.log_error('Exception occured while deleting and renaming files. Exception message: %s' % str(msg))



def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def run_main():
    dt = datetime.now()

    if not os.path.isfile(dashboard_catalog_live_file_path):
        print '%s ERROR 15.CatalogHistory.py  %s is not a valid file.' % (dt.strftime(dformat), dashboard_catalog_live_file_path)
        app_logger.log_error('%s is not a valid file.' % dashboard_catalog_live_file_path)
        return

    if not os.path.isfile(dashboard_catalog_all_file_path):
        with open(dashboard_catalog_all_file_path,'w') as f:
            pass

    catalog_history = CatalogHistory()
    catalog_history.process_data()

if __name__ == "__main__":
    dt = datetime.now()
    print '%s INFO 15.CatalogHistory.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')
    print '%s INFO 15.CatalogHistory.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    dt = datetime.now()
    start_time = unix_time(dt)

    try:
        run_main()
    except:
        dt = strftime(dformat)
        print '%s ERROR 15.CatalogHistory.py  Script didn\'t complete successfully.' % dt.strftime(dformat)
        app_logger.log_error('Script didn\'t complete sucessfully.')

    dt = datetime.now()
    end_time = unix_time(dt)

    print '%s INFO 15.CatalogHistory.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 15.CatalogHistory.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
