#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import os.path
import re
from datetime import datetime
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

__author__ = 'urKh'

app_logger = LoggingManager('05.PolicyConfig')
config_vars = GlobalConfig.read_vars('05.PolicyConfig')

input_policies_l_details = config_vars.get('policies_l_details_file')
input_policies_u_details = config_vars.get('policies_u_details_file')
output_policy_config_csv = config_vars.get('output_policy_config_csv')

class PolicyConfig(object):

    tmp_pd = []
    tmp_policyu = []
    
    def process_policy_u(self):

        policy = None
        policy_type = None
        active = None
        backup = None
        new_policy = False
        has_calendar = 'no'
        date_backups = ['', '']
        hour_backups = ['', '']
        backups = ['', '']
        schedule_qty = 0

        policies_u_details = open(input_policies_u_details, 'r').readlines()
        for pud in policies_u_details:

            line = [x.replace(' ', '').strip() for x in pud.split(':')]

            if line[0] == 'PolicyName' and new_policy:

                self.tmp_policyu.append({'policy': policy, 'policy_type':policy_type, 'active':active, 'retention':date_backups, 'type':backup, 'hour_backups':hour_backups, 'calendar':has_calendar})
                new_policy = False
                has_calendar = 'no'
                backups = ['','']
                date_backups = ['','']
                hour_backups = ['','']
                schedule_qty = 0
                
            if line[0] == 'PolicyName' and not new_policy:
                policy = line[1]
                new_policy = True
            elif line[0] == 'PolicyType' and new_policy:
                policy_type = line[1]
            elif line[0] == 'Active' and new_policy:
                active = line[1]
            elif line[0] == 'Schedule' and new_policy:
                schedule_qty += 1
            elif line[0] == 'Calendarsched' and new_policy:
                has_calendar = 'yes'
            elif line[0] == 'RetentionLevel' and new_policy:
                retention_level = line[1][line[1].find("(") + 1:line[1].find(")")] # get value in parenthesis
                retention_level = re.split('(\d+)', retention_level) # separate numbers from letters in list
                retention_level = ' '.join(retention_level).strip() # join array and drop first white space
                if schedule_qty == 1:
                    date_backups[0] = retention_level
                if schedule_qty == 2:
                    date_backups[1] = retention_level
            elif line[0] == 'Type' and new_policy:
                if schedule_qty == 1:
                    backup = re.sub('([a-z])([A-Z])', r'\g<1> \g<2>', line[1])
                #    backups[0] = backup
                #if schedule_qty == 2:
                #    backups[1] = backup
            elif pud.find('-->') > -1 and new_policy:
                hour_b = re.sub(' +', ' ', pud).strip()
                if schedule_qty == 1:
                    hour_backups[0] += ' ' + hour_b
                if schedule_qty == 2:
                    hour_backups[1] += ' ' + hour_b

        # append the last
        self.tmp_policyu.append({'policy': policy, 'policy_type':policy_type, 'active':active, 'retention':date_backups, 'type':backup, 'hour_backups':hour_backups, 'calendar':has_calendar})


    def process_data(self):
        new_class = False
        sched_set = False
        policy_name = None
        client = None
        include = None
        sched = None
        tmp_policy = []

        policies_details = open(input_policies_l_details, 'r').readlines()
        for pd in policies_details:
            pd = pd.strip().split(' ')

            if pd[0] == 'CLASS' and new_class:
                clients = ' '.join(tmp_policy)
                self.tmp_pd.append([policy_name, clients, 'None', 'None', 'None', 'None', sched, 'None', 'None', include, 'None', 'None'])
                new_class = False
                sched_set = False
                tmp_policy = []
            if pd[0] == 'CLASS' and not new_class:
                policy_name = pd[1]
                new_class = True
            elif pd[0] == 'CLIENT' and new_class:
                client = pd[1]
                tmp_policy.append(client)
            elif pd[0] == 'SCHED' and new_class:
                if not sched_set:
                    if pd[2] == '0':
                        sched = 'Full Backup'
                    elif pd[2] == '1':
                        sched = 'Differential Incremental Backup'
                    elif pd[2] == '4':
                        sched = 'Cumulative Incremental Backup'
                    else:
                        sched = ''
                sched_set = True
            elif pd[0] == 'INCLUDE' and new_class:
                include = pd[1]


        # always check the last item
        clients = ' '.join(tmp_policy)
        self.tmp_pd.append([policy_name, clients, 'None', 'None', 'None', 'None', sched, 'None', 'None', include, 'None', 'None'])
        self.process_policy_u()
        
        for rowl in self.tmp_pd:
            for rowu in self.tmp_policyu:
                if rowl[0] == rowu['policy']:
                    rowl[2] = rowu['policy_type']
                    rowl[3] = rowu['type']
                    rowl[4] = rowu['hour_backups'][0].strip()
                    rowl[5] = rowu['retention'][0]
                    #rowl[6] = rowu['type'][1]
                    rowl[7] = rowu['hour_backups'][1].strip()
                    rowl[8] = rowu['retention'][1]
                    rowl[10] = rowu['active']
                    rowl[11] = rowu['calendar']

        # write definitive result in output file
        _file = open(output_policy_config_csv, 'w')
        print >> _file, 'Policy, Server, Backup Type, Full Backup Type, Full Backup Windows, Full Retention, Incr Backup Type, Incr Backup Windows, Incr Retention, Backup Selection, Policy Active, Calendar'
        for row in self.tmp_pd:
            print '%s INFO 05.PolicyConfig.py  Entered sequence for: %s, %s' % (get_date(), row[0], row[1])
            app_logger.log_info('Entered sequence for: %s, %s' % (row[0], row[1]))
            print >> _file, ', '.join(row)


def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def run_main():
    if not os.path.isfile(input_policies_l_details):
        print '%s ERROR 05.PolicyConfig.py  %s is not a valid file.' % (get_date(), input_policies_l_details)
        app_logger.error('%s is not a valid file.' % input_policies_l_details)
        return
    if not os.path.isfile(input_policies_u_details):
        print '%s ERROR 05.PolicyConfig.py  %s is not a valid file.' % (get_date(), input_policies_u_details)
        app_logger.error('%s is not a valid file.' % input_policies_u_details)
        return
    policy_config = PolicyConfig()
    policy_config.process_data()


if __name__ == '__main__':
    print '%s INFO 05.PolicyConfig.py  Program is starting...' % get_date()
    app_logger.log_info('Program is starting')
    print '%s INFO 05.PolicyConfig.py  Started running...' % get_date()
    app_logger.log_info('Started running...')
    print '%s INFO 05.PolicyConfig.py  Start generating policyconfignew.csv' % get_date()
    app_logger.log_info('Start generating policyconfignew.csv')

    start_time = unix_time(datetime.now())

    try:
        run_main()
    except:
        print '%s ERROR 05.PolicyConfig.py  Scrip\'t didnt complete successfully.' % get_date()
        app_logger.log_error('Script didn\'t complete successfully.')
    
    end_time = unix_time(datetime.now())
    print '%s INFO 05.PolicyConfig.py  Saving output to: %s' % (get_date(), output_policy_config_csv)
    app_logger.log_info('Saving output to: %s' % output_policy_config_csv)
    print '%s INFO 05.PolicyConfig.py  Time to run %s seconds.' % (get_date(), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))
    print '%s INFO 05.PolicyConfig.py  Ended running...' % get_date()
    app_logger.log_info('Ended running...')
