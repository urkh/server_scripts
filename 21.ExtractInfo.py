#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import os.path
from datetime import datetime
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

__author__ = 'urKh'

app_logger = LoggingManager('21.ExtractInfo')
config_vars = GlobalConfig.read_vars('03.ExtractInfo')

input_bpdbjobs_file = config_vars.get('bpdbjobs_file')
input_bpimagelist_file = config_vars.get('bpimagelist_file')
#input_allpolicies_file = config_vars.get('allpolicies_file')
input_policies_l_details_file = config_vars.get('policies_l_details_file')
output_extracted_info = config_vars.get('output_extracted_info')

class ExtractInfo(object):

    def process_data(self):

        policy_name = ''
        client = ''
        value_info = ''
        new_class = False
        tmp_pd = []
        tmp_sched = []
        tmp_schedwin = []
        tmp_policies_info = []

        policies_details = open(input_policies_l_details_file, 'r').readlines()
        for pd in policies_details:
            pd = pd.strip().split(' ')
           
            if pd[0] == 'CLASS' and new_class:
                for row in tmp_pd:
                    if row[0].split(', ')[0] == policy_name and len(row) < 3:
                        if len(tmp_sched) < 2:

                            sched1 = tmp_sched[0].split(', ')
                            if sched1[2] == '0':
                                row.append([tmp_schedwin[0]])
                                row.append(['91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911'])
                            if sched1[2] == '1' or sched1[2] == '4':
                                row.append(['91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911, 91911'])
                                row.append([tmp_schedwin[0]])
                        else: 
                            for index, sched in enumerate(tmp_sched):
                                if sched.split(', ')[2] == '0':
                                    row.append([tmp_schedwin[index]])
                                if sched.split(', ')[2] == '1' or sched.split(', ')[2] == '4':
                                    row.append([tmp_schedwin[index]])

                #import ipdb; ipdb.set_trace()
                tmp_policies_info.append('%s, %s' % (policy_name, value_info)) 
                new_class = False
                tmp_sched = []
                tmp_schedwin = []

            if pd[0] == 'CLASS' and not new_class:
                policy_name = pd[1]
                new_class = True
            elif pd[0] == 'CLIENT' and new_class:
                client = pd[1]
                tmp_pd.append(['%s, %s' % (policy_name, client)])
            elif pd[0] == 'SCHED' and new_class:
                tmp_sched.append(', '.join(pd))
            elif pd[0] == 'SCHEDWIN' and new_class:
                tmp_schedwin.append(', '.join(pd[1:]))
            elif pd[0] == 'INFO':
                value_info = pd[11]

        # always check the last item
        #import ipdb; ipdb.set_trace()
        for row in tmp_pd:
            if len(row) == 1:
                for index, sched in enumerate(tmp_sched):
                    if sched.split(', ')[2] == '0':
                        row.append([tmp_schedwin[index]])
                    if sched.split(', ')[2] == '1' or sched.split(', ')[2] == '3':
                        row.append([tmp_schedwin[index]])

        # check for bpdb_jobs
        bpdbjobs = open(input_bpdbjobs_file, 'r').readlines()
        for row in tmp_pd:
            for bprow in bpdbjobs:
                bprow = bprow.split(', ')
                policy_client = bprow[0] + ', ' + bprow[1]
                elapsed = int(bprow[3].strip())
                if row[0] == policy_client:
                    row[0] += ', Active'
                    row[0] += ', %s' % str(elapsed)
                    row[0] += ', Running, Running, Running'

        # check for bp_imagelist
        bpimagelist = open(input_bpimagelist_file, 'r').readlines()
        for row in tmp_pd:
            for bpirow in bpimagelist:
                bpirow = bpirow.split(', ')
                policy_client = bpirow[0] + ', ' + bpirow[1]
                if row[0] == policy_client and row[0].split(', ')[-1] != 'Running':
                    row[0] = ', '.join(bpirow).strip()

        # amend the info row
        for row in tmp_pd:
            policy = row[0].split(', ')[0]
            for pol in tmp_policies_info:
                pol_info = pol.split(', ')[0]
                pol_value = pol.split(', ')[1]
                import ipdb; ipdb.set_trace()
                if pol_info == policy and pol_value == '1' and len(row[0].split(', ')) == 2:
                    row[0] += ', Inactive, Inactive, Inactive, Inactive, Inactive'

        # amend the NoBackup row
        for row in tmp_pd:
            if len(row[0].split(', ')) == 2:
                row[0] += ', NoBackup, NoBackup, NoBackup, NoBackup, NoBackup'

        # write definitive result in output file
        _file = open(output_extracted_info, 'w')
        for row in tmp_pd:
            print '%s INFO 21.ExtractInfo  Entered sequence for: %s, %s' % (get_date(), row[0].split(', ')[0], row[0].split(', ')[1])
            app_logger.log_info('Entered sequence for: %s, %s' % (row[0].split(', ')[0], row[0].split(', ')[1]))
            print >> _file, row[0]

            for srow in row:
                if isinstance(srow, list):
                    print >> _file, ', '.join(srow)

       

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def run_main():
    if not os.path.isfile(input_bpdbjobs_file):
        print '%s ERROR 21.ExtractInfo.py  %s is not a valid file.' % (get_date(), input_bpdbjobs_file)
        app_logger.log_error('%s is not a valid file.' % input_bpdbjobs_file)
        return
    if not os.path.isfile(input_bpimagelist_file):
        print '%s ERROR 21.ExtractInfo.py  %s is not a valid file.' % (get_date(), input_bpimagelist_file)
        app_logger.log_error('%s is not a valid file.' % input_bpimagelist_file)
        return
    """
    if not os.path.isfile(input_allpolicies_file):
        print '%s ERROR 21.Test.py  %s is not a valid file.' % (get_date(), input_allpolicies_file)
        app_logger.log_error('%s is not a valid file.' % input_allpolicies_file)
        return
    """
    if not os.path.isfile(input_policies_l_details_file):
        print '%s ERROR 21.ExtractInfo.py  %s is not a valid file.' % (get_date(), input_policies_l_details_file)
        app_logger.log_error('%s is not a valid file.' % input_policies_l_details_file)
        return

    extract_info = ExtractInfo()
    extract_info.process_data()

if __name__ == '__main__':
    print '%s INFO 21.ExtractInfo  Program is starting...' % get_date()
    app_logger.log_info('Program is starting...')
    print '%s INFO 21.ExtractInfo  Started running...' % get_date()
    app_logger.log_info('Started running...')
    print '%s INFO 21.ExtractInfo  Start generating extracted_info.txt' % get_date()
    
    app_logger.log_info('Start generating extracted_info.txt')
    start_time = unix_time(datetime.now())
    
    try:
        run_main()
    except:
        print '%s ERROR 21.ExtractInfo  Script didn\'t complete successfully.' % get_date()
        app_logger.log_error('Script didn\'t complete successfully.')

    end_time = unix_time(datetime.now())

    print '%s INFO 21.ExtractInfo  Saving output to: %s' % (get_date(), output_extracted_info)
    app_logger.log_info('Saving output to: %s' % output_extracted_info)

    print '%s INFO 21.ExtractInfo  Time to run %s seconds.' % (get_date(), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))

    print '%s INFO 21.ExtractInfo  Ended running...' % get_date()
    app_logger.log_info('Ended running...')

