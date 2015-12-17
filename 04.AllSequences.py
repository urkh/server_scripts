#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import os.path
from datetime import datetime
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

__author__ = 'urKh'

app_logger = LoggingManager('04.AllSequences')
config_vars = GlobalConfig.read_vars('04.AllSequences')

input_policies_l_details = config_vars.get('policies_l_details_file')
output_allseq = config_vars.get('output_allseq_file')

class AllSequences(object):

    tmp_pd = []

    def process_polcli(self, tmp_policy_client):
        for polcli in tmp_policy_client:
            #import ipdb; ipdb.set_trace()
            self.tmp_pd.append([polcli])


    def process_data(self):
        new_class = False
        policy_name = None
        client = None
        tmp_policy_client = []

        policies_details = open(input_policies_l_details, 'r').readlines()
        for pd in policies_details:
            pd = pd.strip().split(' ')

            if pd[0] == 'CLASS' and new_class:
                self.process_polcli(tmp_policy_client)
    
                new_class = False
                tmp_policy_client = []

            if pd[0] == 'CLASS' and not new_class:
                policy_name = pd[1]
                new_class = True
            elif pd[0] == 'CLIENT' and new_class:
                client = pd[1]
                tmp_policy_client.append('%s, %s' % (policy_name, client))


        # always check the last item
        self.process_polcli(tmp_policy_client)

        # write definitive result in output file
        _file = open(output_allseq, 'w')
        for row in self.tmp_pd:
            #import ipdb; ipdb.set_trace()
            print '%s INFO 04.AllSequences  Entered sequence for: %s' % (get_date(), row[0])
            app_logger.log_info('Entered sequence for: %s' % row[0])
            print >> _file, row[0]


def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def run_main():
    if not os.path.isfile(input_policies_l_details):
        print '%s ERROR 04.AllSequences.py  %s is not a valid file.' % (get_date(), input_policies_l_details)
        app_logger.log_error('%s is not a valid file.' % input_policies_l_details)

    all_sequences = AllSequences()
    all_sequences.process_data()

if __name__ == '__main__':
    print '%s INFO 04.AllSequences.py  Program is starting...' % get_date()
    app_logger.log_info('Program is starting...')
    print '%s INFO 04.AllSequences.py  Started running...' % get_date()
    app_logger.log_info('Started running...')
    print '%s INFO 04.AllSequences.py  Start generating allseq.txt' % get_date()
    app_logger.log_info('Start generating allseq.txt')

    start_time = unix_time(datetime.now())

    try:
        run_main()
    except:
        print '%s ERROR 04.AllSequences.py  Script didn\'t complete successfully.' % get_date()
        app_logger.log_error('Script didn\'t complete successfuly.')

    end_time = unix_time(datetime.now())
    
    print '%s INFO 04.AllSequences.py  Saving output to: %s' % (get_date(), output_allseq)
    app_logger.log_info('Saving output to: %s' % output_allseq)
    print '%s INFO 04.AllSequences.py  Time to run %s seconds.' % (get_date(), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds' % str(end_time-start_time))
    print '%s INFO 04.AllSequences.py  Ended running...' % get_date()
    app_logger.log_info('Ended running...')


