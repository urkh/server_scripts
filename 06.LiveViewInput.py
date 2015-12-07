#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Codengine'
import os.path
import calendar
import time
import csv
from datetime import datetime, timedelta, date
from math import floor
from LoggingManager import LoggingManager
from GlobalConfig import GlobalConfig

CONFIG_VARS = GlobalConfig.read_vars('06.LiveViewInput')
COLUMN_FIVE_PERCENTAGE = CONFIG_VARS.get('column_five_percentage')
FILE1_NAME = CONFIG_VARS.get('file1_name')
FILE2_NAME = CONFIG_VARS.get('file2_name')
FILE3_NAME = CONFIG_VARS.get('file3_name')
HISTORY_FILE_NAME = CONFIG_VARS.get('history_file')
CALENDAR_FILE_NAME = CONFIG_VARS.get('calander_file_name')
OUTPUT_FILE = CONFIG_VARS.get('output_file')
NOSCHEDULT_DATA_FILE = CONFIG_VARS.get('noschedult_data_file')
INACTIVE_POLICIES_DATA_FILE = CONFIG_VARS.get('inactive_policies_file_name')
APP_LOGGER = LoggingManager('06.LiveViewInput.py')


class FileHandler(object):
    # def __init__(self):
    #    pass

    @staticmethod
    def read_csv(file_name):
        lines = []
        error = False
        try:
            with open(file_name, 'r') as f:
                lines = f.readlines()

            contents = []
            for line in lines:
                contents += [[i.strip() for i in line.split(',')]]
        except Exception as msg:
            error = True
            print 'Exception occured inside read_csv() method in FileHandler.'
            APP_LOGGER.log_error('Exception occured inside read_csv() method in FileHandler. Exception message: %s' % str(msg))
        if not contents and error:
            print 'Data file empty. File name: %s' % file_name
            APP_LOGGER.log_error('Data file %s is empty. Inside method read_csv().' % file_name)
        return contents

    @staticmethod
    def read_sequence_in_chunks(file_object, last_line_read=0):
        """Lazy function (generator) to read a file piece by piece."""
        while True:
            policy_name = None
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
                policy_name = data_split[0].strip()

            while same_sequence_found:
                file_object.seek(last_line_read)
                data = file_object.readline()

                if data == '\n':
                    last_line_read = last_line_read + len(data)
                    continue

                if not data:
                    break

                temp_data_split = data.split(',')

                if temp_data_split and temp_data_split[0] == data_split[
                        0] and temp_data_split[1] == data_split[1]:
                    data_sequence += [data]
                    last_line_read = last_line_read + len(data)
                else:
                    same_sequence_found = False

            yield last_line_read, data_sequence, policy_name

    @staticmethod
    def write_output(file1_contents, output_data, file_name):
        try:
            contents = []
            for f1_data, o_data in zip(file1_contents, output_data):
                if len(f1_data) == 8:
                    f1_data[7] = o_data['status']
                    line = f1_data
                elif len(f1_data) == 7:
                    line = f1_data + [o_data['status']]
                if o_data['status'] == 'NoSchedule':
                    for i in range(2, len(line)):
                        line[i] = o_data['status']
                contents += [line]

            """ Here modify the output in the list. """
            temp_contents = []
            for row in contents:
                temp_row = row
                tmp_third_col_val = row[2]
                time_stamp = row[3]
                status_val = row[7]

                temp_row[2] = status_val
                timestamp_error = False
                try:
                    time_stamp = int(time_stamp)
                except Exception as msg:
                    timestamp_error = True
                col_three_val = time_stamp
                # if not timestamp_error:
                #    col_three_val = int(time_stamp)/3600
                col_three_val = str(col_three_val).zfill(10)
                if status_val != 'Active' and status_val != 'LongRun':
                    datetime_str = str(
                        datetime.fromtimestamp(
                            float(time_stamp))) if not timestamp_error else time_stamp
                    col_three_val = datetime_str
                temp_row[3] = col_three_val
                temp_row[7] = tmp_third_col_val
                temp_contents += [temp_row]

            contents = temp_contents

            # First write the data to csv file using .txt extension with csv
            # module.
            with open(file_name, 'w') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(contents)

            # To remove all whitespaces read the contents and remove all
            # whitespaces and write back to the file.
            contents = []
            with open(file_name, 'r') as f:
                contents = f.readlines()

            temp_contents = [
                line.rstrip() if i == len(contents) -
                1 else line.rstrip() +
                '\n' for i,
                line in enumerate(contents)]
            contents = temp_contents

            with open(file_name, 'w') as f:
                for line in contents:
                    f.write(line)
        except Exception as msg:
            print 'Exception inside filewrite'
            APP_LOGGER.log_error(
                'Exception occured inside write_output() method. Exception message: %s' %
                str(msg))


def get_day_of_the_week():
    day_l = ['Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Satur', 'Sun']
    return day_l[date(datetime.now().year, datetime.now().month, datetime.now().day).weekday()] + 'day'


def unix_time(dt):
    return int(time.mktime(dt.timetuple()))


class Main(object):

    def __init__(self):
        self.static_header = ["Sunday", "stime", "Monday", "mtime", "Tuesday", "ttime", "Wednesday", "wtime", "Thursday", "thtime", "Friday", "ftime", "Saturday", "satime"]

    def get_row_index(self):
        # Get today's day name like: Saturday
        today_day = get_day_of_the_week()
        # Now check for matching value in static list and return the index.
        for i, val in enumerate(self.static_header):
            if val == today_day:
                return i

    def get_current_time_in_seconds(self):
        current_time_hour = datetime.now().hour
        current_time_min = datetime.now().minute
        s_float = str(current_time_hour) + '.' + str(current_time_min)
        current_time = float(s_float)
        return int(current_time * 3600)

    def get_stop_index(self, index):
        if index == 0:
            return 2
        elif index == 2:
            return 4
        elif index == 4:
            return 6
        elif index == 6:
            return 8
        elif index == 8:
            return 10
        elif index == 10:
            return 12
        elif index == 12:
            return 0

    def get_previous_index(self, index):
        if index == 0:
            return 12
        elif index == 2:
            return 0
        elif index == 4:
            return 2
        elif index == 6:
            return 4
        elif index == 8:
            return 6
        elif index == 10:
            return 8
        elif index == 12:
            return 10

    def find_f2_and_f3(self, f2_row, f3_row):
        row_index = self.get_row_index()

        stop_index = self.get_stop_index(row_index)

        f2_val = int(f2_row[row_index])
        f3_val = int(f3_row[row_index])

        current_time_secs = self.get_current_time_in_seconds()

        if (f2_val != 91911 and f2_val > current_time_secs) or (
                f3_val != 91911 and f3_val > current_time_secs):
            prev_row_index = row_index
            while True:
                prev_row_index = self.get_previous_index(prev_row_index)
                if prev_row_index == stop_index:
                    break
                f2_val = int(f2_row[prev_row_index])
                f3_val = int(f3_row[prev_row_index])

                if f2_val > 0 or f3_val > 0:
                    break

        return f2_val, f3_val

    def get_stop_index2(self, index):
        return index

    def find_f2_and_f3_two(self, f2_row, f3_row):
        row_index = self.get_row_index()

        stop_index = self.get_stop_index2(row_index)

        current_index = row_index

        current_time_secs = self.get_current_time_in_seconds()

        iteration_required = 0
        valid_data_found = False

        f2_val = int(f2_row[current_index])
        f3_val = int(f3_row[current_index])

        if f2_val != 91911 or f3_val != 91911:
            if (f2_val != 0 and f2_val < current_time_secs) or (
                    f3_val != 0 and f3_val < current_time_secs):
                valid_data_found = True
                pass
            else:
                current_index = self.get_previous_index(current_index)
                f2_val = int(f2_row[current_index])
                f3_val = int(f3_row[current_index])
                while current_index != stop_index:
                    iteration_required += 1
                    if (f2_val != 0 and f2_val != 91911) or (
                            f3_val != 0 and f3_val != 91911):
                        valid_data_found = True
                        break
                    current_index = self.get_previous_index(current_index)
                    f2_val = int(f2_row[current_index])
                    f3_val = int(f3_row[current_index])
                    if current_index == stop_index:
                        iteration_required += 1

        else:
            pass

        return self.static_header[
            current_index], iteration_required, valid_data_found, f2_val, f3_val

    def check_and_return(self):
        """ This function read data from all the three files, process the data and return list of output. """

        # First read file1.txt,file2.txt and file3.txt. The program assumes that the contents of the file will be
        # comma separated. FileHandler.read_csv file will return a list of list where each inner list is a data row
        # like [[server1,windows,0,120,running,BAD0],
        # [server2,linux,1,250,offline,NOK1], .....]
        file1_data = FileHandler.read_csv(FILE1_NAME)

        if not file1_data:
            print 'input data is empty for file %s' % FILE1_NAME
            APP_LOGGER.log_error(
                'input data is empty for file %s' %
                FILE1_NAME)
            return None, None

        file2_data = FileHandler.read_csv(FILE2_NAME)

        if not FILE2_NAME:
            print 'input data is empty for file %s' % FILE2_NAME
            APP_LOGGER.log_error(
                'input data is empty for file %s' %
                FILE2_NAME)
            return None, None

        file3_data = FileHandler.read_csv(FILE3_NAME)

        if not FILE3_NAME:
            print 'input data is empty for file %s' % FILE3_NAME
            APP_LOGGER.log_error(
                'input data is empty for file %s' %
                FILE3_NAME)
            return None, None

        history_file = open(HISTORY_FILE_NAME, 'r')
        history_data_dict = {}
        last_line_read = 0
        for last_line_read, data_seq_lines, policy_name in FileHandler.read_sequence_in_chunks(history_file, last_line_read):
            if history_data_dict.get(policy_name):
                history_data_dict[policy_name] += data_seq_lines
            else:
                history_data_dict[policy_name] = data_seq_lines
        history_file.close()

        if not history_data_dict:
            print 'History data file is empty.'
            APP_LOGGER.log_error('History data file is empty.')
            return None, None

        def check_for_any_full(rows):
            for row in rows:
                row_split = row.split(',')
                if row_split[3].strip() == '0':
                    return True
            return False

        def split_calander_row_third_col(third_col_val):
            titles = ['SCHEDCALIDATES', 'SCHEDCALDAYOWEEK', 'SCHEDCALDAYOMONTH']
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

        def match_todays_date(timestamp):
            target_datetime = datetime.fromtimestamp(int(timestamp))
            target_date = target_datetime.date()
            tdays_date = datetime.now().date()
            if target_date == tdays_date:
                return True
            return False

        def week_of_month(dt):
            """ Returns the week of the month for the specified date."""
            first_day = dt.replace(day=1)
            dom = dt.day
            adjusted_dom = dom + first_day.weekday()
            return int(floor(adjusted_dom / 7.0))

        def adjust_tdays_day(day):
            if day == 6:  # if day is sunday. calendar week starts from monday = 0. so sunday is 6 here.
                return 1
            elif day == 0:  # if day is monday
                return 2
            elif day == 1:  # if day is tuesday.
                return 3
            elif day == 2:  # if day is wednesday.
                return 4
            elif day == 3:  # if day is thursday.
                return 5
            elif day == 4:  # if day is friday.
                return 6
            elif day == 5:  # if day is saturday.
                return 7

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

        def get_todays_day_week_pair():
            tday = datetime.now()
            tday_day = tday.weekday()
            week_month = week_of_month(tday)
            adjusted_day = adjust_tdays_day(tday_day)
            return adjusted_day, week_month

        def define_f2_f3_value(value):
            if value == 0 or value == 91911:
                return value
            else:
                return 'VALID'

        def find_valid_data_expected_day(f2_row):
            for i, value in enumerate(f2_row):
                if i % 2 == 0:
                    int_val = int(value)
                    if int_val > 0 and int_val < 91911:
                        return i

        # datetime_val is a string representing the datetime.
        def report_noschedule_data(policy_name, server_name):
            todays_datetime = datetime.now()
            todays_timestamp_str = unix_time(todays_datetime)
            data_line = policy_name + ', ' + server_name + ', ' + str(todays_timestamp_str) + ', ' + 'NoSchedule\n'
            with open(NOSCHEDULT_DATA_FILE, 'a') as nrf:
                nrf.write(data_line)

        def resport_inactive_policy(policy_name, server_name):
            todays_datetime = datetime.now()
            todays_timestamp_str = unix_time(todays_datetime)
            data_line = policy_name + ', ' + server_name + ', ' + str(todays_timestamp_str) + ', ' + 'Inactive\n'
            with open(INACTIVE_POLICIES_DATA_FILE, 'a') as ipf:
                ipf.write(data_line)

        def check_valid_data_between_expectedday_today(
                policy_name, server_name, todays_datetime, day_gap_between_expected, policy_history_data):
            days_gap_list = range(day_gap_between_expected)
            days_gap_list = [i + 1 for i in days_gap_list]

            if not days_gap_list:
                return False

            dates_to_check = [todays_datetime + timedelta(days=-i) for i in days_gap_list]
            dates_to_check = [dt.date() for dt in dates_to_check]
            valid_data_found_on_another_day = False

            for line in policy_history_data:
                line = line.replace('\n', '')
                line_split = line.split(',')
                pname = line_split[0].strip()
                sname = line_split[1].strip()
                if pname == policy_name and sname == server_name:
                    policy_timestamp = line_split[2]
                    try:
                        policy_timestamp = int(policy_timestamp)
                    except Exception:
                        print 'Invalid timestamp value.'
                        policy_timestamp = -1

                    if policy_timestamp != -1:
                        policy_datetime = datetime.fromtimestamp(policy_timestamp)
                        policy_date = policy_datetime.date()
                        if policy_date in dates_to_check:
                            valid_data_found_on_another_day = True
                            break
            return valid_data_found_on_another_day

        def find_valid_data_expected_day_calender(third_col_val_dict):

            all_dates = {}

            for key, value in third_col_val_dict.items():
                if key == 'SCHEDCALIDATES':
                    for each_tstamp in value:
                        target_datetime = datetime.fromtimestamp(int(each_tstamp))
                        if all_dates.get(key):
                            all_dates[key] += [target_datetime]
                        else:
                            all_dates[key] = [target_datetime]
                    if all_dates.get(key):
                        all_dates[key] = [dt.date() for dt in all_dates[key]]

                elif key == 'SCHEDCALDAYOWEEK':
                    tday_datetime = datetime.now()
                    previous_month = False
                    for dayweek_pair in value:
                        dayweek_list = dayweek_pair.split(';')
                        for each_pair in dayweek_list:
                            day_week = each_pair.split(',')
                            day = int(day_week[0])
                            week = int(day_week[1])
                            tday, tweek = get_todays_day_week_pair()
                            if week > tweek:
                                previous_month = True
                                break
                            elif week == tweek and day < tday:
                                previous_month = True
                                break

                    dtd = tday_datetime.date()

                    if previous_month:
                        first_day_cm = date(day=1, month=tday_datetime.month, year=tday_datetime.year)
                        dtd = first_day_cm + timedelta(days=-1)

                    last_day = calendar.monthrange(dtd.year, dtd.month)
                    dates_in_ranges = [date(day=i + 1, month=dtd.month, year=dtd.year) for i in range(last_day[1])]
                    day_week_pairs = [(dt.weekday(), week_of_month(dt)) for dt in dates_in_ranges]

                    def find_wdate_by_index(index):
                        for ii, ddate in enumerate(dates_in_ranges):
                            if ii == index:
                                return ddate

                    for dayweek_pair in value:
                        dayweek_list = dayweek_pair.split(';')
                        for each_pair in dayweek_list:
                            day_week = each_pair.split(',')
                            day = int(day_week[0])
                            week = int(day_week[1])
                            adjusted_wday = adjust_day_reverse(day)

                            for j, day_week in enumerate(day_week_pairs):
                                if day_week[0] == adjusted_wday and day_week[1] == week:
                                    wdate = find_wdate_by_index(j)
                                    if all_dates.get(key):
                                        all_dates[key] += [wdate]
                                    else:
                                        all_dates[key] = [wdate]

                elif key == 'SCHEDCALDAYOMONTH':
                    tday_datetime = datetime.now()
                    today_day = tday_datetime.day
                    value = [int(val) for val in value]
                    max_int_val = max(value)
                    previous_month = False
                    # Last day of month. It can be current month or previous
                    # month based on decission.
                    if today_day < max_int_val:
                        last_day = calendar.monthrange(tday_datetime.year, tday_datetime.month)
                        if max_int_val == 32:
                            if today_day == last_day:
                                pass
                            else:
                                # Previous month.
                                previous_month = True
                        else:
                            previous_month = True
                    else:
                        previous_month = False

                    for day in value:
                        val_int = int(day)
                        if previous_month:
                            first_day_cm = date(day=1, month=tday_datetime.month, year=tday_datetime.year)
                            previous_month_date = first_day_cm + timedelta(days=-1)
                            pm_last_day = calendar.monthrange(previous_month_date.year, previous_month_date.month)
                            if val_int == 32:
                                val_int = pm_last_day[1]
                            dtt = date(day=val_int, month=previous_month_date.month, year=previous_month_date.year)
                            if all_dates.get(key):
                                all_dates[key] += [dtt]
                            else:
                                all_dates[key] = [dtt]
                        else:
                            if val_int == 32:
                                last_day = calendar.monthrange(tday_datetime.year, tday_datetime.month)
                                # if 'val_int' is equal to 32, then we assign
                                # to this, the second value of 'last_day'
                                val_int = last_day[1]
                            dtt = date(day=val_int, month=tday_datetime.month, year=tday_datetime.year)
                            if all_dates.get(key):
                                all_dates[key] += [dtt]
                            else:
                                all_dates[key] = [dtt]

            return all_dates

        def calculate_calander_decision(policy_name, server_name, calander_date_data, file2_val, file3_val, policy_history_data):
            third_col_val = None
            decision_value = None
            for row in calander_date_data:
                cd_pname = row[0].strip()
                cd_sname = row[1].strip()
                if cd_pname == policy_name and cd_sname == server_name:
                    third_col_val = ''  # row[2].strip()
                    remaining_cols = row[2:]
                    third_col_val = ','.join(remaining_cols)
                    break

            if third_col_val:

                if third_col_val.startswith('NotCalendar'):

                    valid_data_expected_day_index = find_valid_data_expected_day(file2_val)
                    todays_day_index = self.get_row_index()
                    day_gap_between_expected = todays_day_index - valid_data_expected_day_index
                    todays_datetime = datetime.now()
                    valid_day, day_gap, valid_data_found, f2_val, f3_val = self.find_f2_and_f3_two(file2_val, file3_val)
                    valid_data_datetime = todays_datetime + timedelta(days=-day_gap if day_gap > 0 else day_gap)
                    valid_data_date = valid_data_datetime.date()
                    temp_datetime = datetime.combine(valid_data_datetime.date(), todays_datetime.time())
                    valid_data_datetime = temp_datetime
                    f2_value_defined = define_f2_f3_value(f2_val)
                    f3_value_defined = define_f2_f3_value(f3_val)
                    valid_data_found = 0  # 0 for False, 1 for True and any value is for Misc
                    pshistory_lines = []
                    valid_data_found_on_expected_day = False

                    for line in policy_history_data:
                        line = line.replace('\n', '')
                        line_split = line.split(',')
                        pname = line_split[0].strip()
                        sname = line_split[1].strip()
                        if pname == policy_name and sname == server_name:
                            policy_timestamp = line_split[2]
                            try:
                                policy_timestamp = int(policy_timestamp)
                            except Exception:
                                print 'Invalid timestamp value.'
                                policy_timestamp = -1

                            if policy_timestamp != -1:
                                policy_datetime = datetime.fromtimestamp(policy_timestamp)
                                policy_date = policy_datetime.date()

                                if policy_date == valid_data_date:
                                    valid_data_found_on_expected_day = True
                                    pshistory_lines += [line_split]

                    if not valid_data_found_on_expected_day:
                        valid_data_found_between_today_expected_day = check_valid_data_between_expectedday_today(policy_name, server_name, todays_datetime, day_gap, policy_history_data)
                        if not valid_data_found_between_today_expected_day:
                            decision_value = 'NoBackup'
                        else:
                            decision_value = 'NoSchedule'
                    else:
                        for line_split in pshistory_lines:
                            column4_val = line_split[3].strip()
                            if f2_value_defined == 'VALID' and f3_value_defined == 'VALID':
                                # check for 0 in column four. if 1 then misc.
                                if column4_val == '0':
                                    valid_data_found = 1  # NoSchedule
                                elif column4_val == '1':
                                    valid_data_found = 3  # misc
                            elif f2_value_defined == 91911 and f3_value_defined == 'VALID':
                                if column4_val == '1':
                                    valid_data_found = 1  # NoSchedule
                                elif column4_val == '0':
                                    valid_data_found = 3  # misc
                            elif f2_value_defined == 'VALID' and f3_value_defined == 91911:
                                if column4_val == '0':
                                    valid_data_found = 1  # NoSchedule
                                else:
                                    # NoBackup
                                    pass
                            elif f2_value_defined == 0 and f3_value_defined == 'VALID':
                                # 1 valid, misc with 0,if no line nobackup
                                if column4_val == '1':
                                    valid_data_found = 1  # NoSchedule
                                elif column4_val == '0':
                                    valid_data_found = 3  # misc
                            elif f2_value_defined == 'VALID' and f3_value_defined == 0:
                                # 0 valid, 1 misc if no line nobackup
                                if column4_val == '0':
                                    valid_data_found = 1  # NoSchedule.
                                elif column4_val == '1':
                                    valid_data_found = 3  # misc
                            elif f2_value_defined == 91911 and f3_value_defined == 0:
                                # nobackup
                                pass
                            elif f2_value_defined == 0 and f3_value_defined == 91911:
                                # nobackup
                                pass
                            elif f2_value_defined == 91911 and f3_value_defined == 91911:
                                # nobackup
                                pass
                            elif f2_value_defined == 0 and f3_value_defined == 0:
                                # nobackup
                                pass

                        if valid_data_found == 1:
                            decision_value = 'NoSchedule'
                        elif valid_data_found == 0:
                            decision_value = 'NoBackup'
                        else:
                            decision_value = 'Misc'
                else:
                    third_col_vals = split_calander_row_third_col(third_col_val)
                    date_match_found = False
                    for key, value in third_col_vals.items():
                        if key == 'SCHEDCALIDATES':
                            for each_tstamp in value:
                                if match_todays_date(each_tstamp):
                                    decision_value = 'NoBackup'
                                    date_match_found = True
                                    break

                        elif key == 'SCHEDCALDAYOWEEK':
                            for dayweek_pair in value:
                                dayweek_list = dayweek_pair.split(';')
                                for each_pair in dayweek_list:
                                    day_week = each_pair.split(',')
                                    day = int(day_week[0])
                                    week = int(day_week[1])
                                    tday, tweek = get_todays_day_week_pair()
                                    if day == tday and week == tweek:
                                        decision_value = 'NoBackup'
                                        date_match_found = True
                                        break

                        elif key == 'SCHEDCALDAYOMONTH':
                            for day in value:
                                day_int = int(day)
                                tday_datetime = datetime.now()
                                if day_int == 32:
                                    last_day = calendar.monthrange(tday_datetime.year, tday_datetime.month)
                                    if tday_datetime.day == last_day[1]:
                                        decision_value = 'NoBackup'
                                        date_match_found = True
                                        break
                                else:
                                    if tday_datetime.day == day_int:
                                        decision_value = 'NoBackup'
                                        date_match_found = True
                                        break

                    decision_value = 'NoSchedule'

                    todays_datetime = datetime.now()
                    tdays_date_only = todays_datetime.date()

                    all_dates = find_valid_data_expected_day_calender(third_col_vals)

                    dates_list = []
                    for key, value in all_dates.items():
                        for each_date in value:
                            if not each_date in dates_list:
                                dates_list += [each_date]

                    last_valid_date = None

                    lower_dates = []
                    for each_date in dates_list:
                        if each_date <= tdays_date_only:
                            lower_dates += [each_date]

                    if not lower_dates:
                        if dates_list:
                            recent_bckups_history_dates = []
                            min_backup_date = min(dates_list)
                            for line in policy_history_data:
                                line = line.replace('\n', '')
                                line_split = line.split(',')
                                plcname = line_split[0].strip()
                                srvrname = line_split[1].strip()
                                if plcname == policy_name and srvrname == server_name:
                                    policy_timestamp = line_split[2]
                                    try:
                                        policy_timestamp = int(policy_timestamp)
                                    except Exception:
                                        print 'Invalid timestamp value.'
                                        policy_timestamp = -1

                                    if policy_timestamp != -1:
                                        policy_datetime = datetime.fromtimestamp(policy_timestamp)
                                        policy_date = policy_datetime.date()
                                        if policy_date < min_backup_date:
                                            recent_bckups_history_dates += [policy_date]

                            if recent_bckups_history_dates:
                                last_valid_date = max(recent_bckups_history_dates)

                    else:
                        lower_dates.sort(reverse=True)

                        current_date_from_cal = None

                        closest_date_from_cal = None

                        last_valid_date = None

                        if not date_match_found:

                            if lower_dates:
                                if len(lower_dates) >= 1:
                                    closest_date_from_cal = lower_dates[0]
                            last_valid_date = closest_date_from_cal
                        else:
                            valid_day, day_gap, valid_data_found, f2_val, f3_val = self.find_f2_and_f3_two(file2_val, file3_val)
                            valid_current_data_found = False
                            current_time_secs = self.get_current_time_in_seconds()
                            if f2_val != 91911 or f3_val != 91911:
                                if (f2_val != 0 and f2_val < current_time_secs) or (f3_val != 0 and f3_val < current_time_secs):
                                    valid_current_data_found = True
                                    #pass
                            if valid_current_data_found:
                                last_valid_date = tdays_date_only
                            else:
                                if lower_dates:
                                    if lower_dates[0] == tdays_date_only:
                                        current_date_from_cal = lower_dates[0]
                                    if current_date_from_cal:
                                        if len(lower_dates) >= 2:
                                            closest_date_from_cal = lower_dates[1]
                                    else:
                                        closest_date_from_cal = lower_dates[0]

                                last_valid_date = closest_date_from_cal

                    if last_valid_date:
                        date_diff = tdays_date_only - last_valid_date

                        day_gap_between_expected = date_diff.days

                        valid_data_found_between_today_expected_day = check_valid_data_between_expectedday_today(policy_name, server_name, todays_datetime, day_gap_between_expected, policy_history_data)

                        if not valid_data_found_between_today_expected_day:
                            decision_value = 'NoBackup'
                        else:
                            decision_value = 'NoSchedule'
                    else:
                        decision_value = 'NoBackup'

            return decision_value

        def calculate_schedule(f1_val, f2_val, f3_val):
            schedule = "ToBeSet"

            # Both Schedules exist in the policy - Policy well configured  and
            # Full backup will start - OK
            if 0 < f2_val < 90000 and f3_val == 0 and f1_val == '0':
                schedule = "Full"
            # Both Schedules exist in the policy - Policy well configured  and
            # Incr backup will start - OK
            elif f2_val == 0 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                schedule = "Incr"
            # Both Schedules exist in the policy - Incr backup scheduled but
            # Full backup started - WARNING
            elif f2_val == 0 and 0 < f3_val < 90000 and f1_val == '0':
                schedule = "MiscFull"
            # Both Schedules exist in the policy - Full backup scheduled but
            # Incr backup started - ALERT
            elif 0 < f2_val < 90000 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                schedule = "IncrMisc"
            # Both Schedules exist in the policy - Policy misconfigured  both
            # Full & Incr backup will start - WARNING
            elif 0 < f2_val < 90000 and 0 < f3_val < 90000 and f1_val == '0':
                schedule = "FullIncrMisc"
            # Both Schedules exist in the policy - Policy misconfigured  both
            # Full & Incr backup will start - WARNING
            elif 0 < f2_val < 90000 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                schedule = "IncrMiscFull"
            # Both Schedules exist in the policy - Policy misconfigured but no
            # backup will start - WARNING
            elif f2_val == 0 and f3_val == 0 and f1_val == '0':
                schedule = "NoBackSched"
            # Both Schedules exist in the policy - Policy misconfigured but no
            # backup will start - WARNING
            elif f2_val == 0 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                schedule = "NoBackSched"
            # No Incr schedule exist in the policy at all - Full backup only
            # will start - OK
            elif 0 < f2_val < 90000 and f3_val > 90000 and f1_val == '0':
                schedule = "FullOnly"
            # No Incr schedule exist in the policy at all - Incr backup instead
            # of Full - ALERT
            elif 0 < f2_val < 90000 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                schedule = "FullOnlyMisc"
            # No Full schedule exist in the policy at all - Incr backup only
            # will start - ALERT
            elif f2_val > 90000 and 0 < f3_val < 90000 and f1_val == '0':
                schedule = "IncrOnlyMisc"
            # No Full schedule exist in the policy at all - Incr backup only
            # will start - ALERT
            elif f2_val > 90000 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                schedule = "IncrOnly"
            # No Incr schedule exist in the policy at all - Policy
            # misconfigured but no backup will start - OK
            elif f2_val == 0 and f3_val > 90000 and f1_val == '0':
                schedule = "FullSchedOnlyNoBckFull"
            # No Incr schedule exist in the policy at all - Policy
            # misconfigured but no backup will start - WARNING (few chance to
            # exist)
            elif f2_val == 0 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                schedule = "FullSchedOnlyNoBckIncr"
            # No Full schedule exist in the policy at all - Policy
            # misconfigured and no backup will start - WARNING
            elif f2_val > 90000 and f3_val == 0 and f1_val == '0':
                schedule = "IncrSchedOnlyNoBckFull"
            # No Full schedule exist in the policy at all - Policy
            # misconfigured and no backup will start - WARNING
            elif f2_val > 90000 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                schedule = "IncrSchedOnlyNoBckIncr"
            # No Full and Incr schedule exist in the policy at all - no backup
            # will start from this policy - WARNING
            elif f2_val > 90000 and f3_val > 90000 and f1_val == '0':
                schedule = "NoScheduleFull"
            # No Full and Incr schedule exist in the policy at all - no backup
            # will start from this policy - WARNING
            elif f2_val > 90000 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                schedule = "NoScheduleIncr"
            elif f1_val == 'Active':
                schedule = "Active"
            elif f1_val == 'Inactive':
                schedule = "Inactive"
            elif f1_val == 'NoSchedule':
                schedule = 'NoSchedule'
            elif f1_val == 'NoBackup':
                schedule = "NoBackup"
            else:
                schedule = "ERROR"
            return schedule

        def read_last_backup(sequence):
            seq_lines = [line for line in sequence if line.split(',')[3].strip() == '0']
            data_lines = []
            if seq_lines:
                data_lines = seq_lines[-1:]
            else:
                data_lines = sequence[-1:]
            return data_lines[0] if data_lines else None

        calander_data_csv = FileHandler.read_csv(CALENDAR_FILE_NAME)

        chances = []

        for file1_val, file2_val, file3_val in zip(
                file1_data, file2_data, file3_data):

            # file1.txt data may be either string or int. So the comparison
            # should be in string.
            f1_val = file1_val[2]
            # Convert the value to int. Get column value for this row using the r_index we got earlier by today's day name.
            #f2_val = int(file2_val[r_index])
            #f3_val = int(file3_val[r_index])
            f2_val, f3_val = self.find_f2_and_f3(file2_val, file3_val)

            f2_val = int(f2_val)
            f3_val = int(f3_val)

            ppolicy_name_ = file1_val[0].strip()
            pserver_name = file1_val[1].strip()

            misc_list = ['Full', 'Incr', 'FullMisc', 'IncrMisc', 'FullIncrMisc', 'IncrFullMisc', 'NoBackSched',
                         'FullOnly', 'FullOnlyMisc', 'IncrOnlyMisc', 'IncrOnly', 'FullSchedOnlyNoBckFull',
                         'FullSchedOnlyNoBckIncr', 'IncrSchedOnlyNoBckFull', 'IncrSchedOnlyNoBckIncr',
                         'NoScheduleFull', 'NoScheduleIncr']

            schedule = "ToBeSet"

            data_sequence = history_data_dict.get(file1_val[0].strip())

            if not data_sequence:
                schedule = calculate_schedule(f1_val, f2_val, f3_val)
                # Append the result in a list.
                chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]
            else:
                if f1_val == 'Inactive':
                    schedule = "Inactive"
                    resport_inactive_policy(ppolicy_name_, pserver_name)
                    chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]
                elif f1_val == 'NoSchedule':
                    schedule = "NoSchedule"
                    chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]
                    report_noschedule_data(ppolicy_name_, pserver_name)
                elif f1_val == 'NoBackup':
                    schedule = "NoBackup"

                    """ Read calander_date.txt file and apply the appropriate logic. """
                    schedule = calculate_calander_decision(
                        ppolicy_name_,
                        pserver_name,
                        calander_data_csv,
                        file2_val,
                        file3_val,
                        data_sequence)
                    if schedule == 'NoSchedule':
                        full_datafound = check_for_any_full(data_sequence)
                        if not full_datafound:
                            schedule = 'FullMissing'
                        report_noschedule_data(ppolicy_name_, pserver_name)

                    chances += [{'Server': file1_val[0],
                                 'ServerType':file1_val[1], 'status':schedule}]
                elif f1_val == 'Active':
                    last_backup = read_last_backup(data_sequence)

                    if last_backup:
                        column_five_val = last_backup.split(',')[4].strip()
                        column_five_val = float(column_five_val)

                        extended_val = column_five_val + (float(COLUMN_FIVE_PERCENTAGE) / 100) * column_five_val
                        col_four_val_f1 = file1_val[3]
                        col_four_val_f1 = float(col_four_val_f1)

                        if col_four_val_f1 > extended_val:
                            schedule = 'LongRun'
                            chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]
                        else:
                            schedule = calculate_schedule(f1_val, f2_val, f3_val)
                            # Append the result in a list.
                            chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]

                else:
                    # Both Schedules exist in the policy - Policy well
                    # configured  and Full backup will start - OK
                    if 0 < f2_val < 90000 and f3_val == 0 and f1_val == '0':
                        schedule = "Full"
                    # Both Schedules exist in the policy - Policy well
                    # configured  and Incr backup will start - OK
                    elif f2_val == 0 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "Incr"
                    # Both Schedules exist in the policy - Incr backup
                    # scheduled but Full backup started - WARNING
                    elif f2_val == 0 and 0 < f3_val < 90000 and f1_val == '0':
                        schedule = "FullMisc"
                    # Both Schedules exist in the policy - Full backup
                    # scheduled but Incr backup started - ALERT
                    elif 0 < f2_val < 90000 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                        schedule = "IncrMisc"
                    # Both Schedules exist in the policy - Policy misconfigured
                    # both Full & Incr backup will start - WARNING
                    elif 0 < f2_val < 90000 and 0 < f3_val < 90000 and f1_val == '0':
                        schedule = "FullIncrMisc"
                    # Both Schedules exist in the policy - Policy misconfigured
                    # both Full & Incr backup will start - WARNING
                    elif 0 < f2_val < 90000 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "IncrFullMisc"
                    # Both Schedules exist in the policy - Policy misconfigured
                    # but no backup will start - WARNING
                    elif f2_val == 0 and f3_val == 0 and f1_val == '0':
                        schedule = "NoBackSched"
                    # Both Schedules exist in the policy - Policy misconfigured
                    # but no backup will start - WARNING
                    elif f2_val == 0 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                        schedule = "NoBackSched"
                    # No Incr schedule exist in the policy at all - Full backup
                    # only will start - OK
                    elif 0 < f2_val < 90000 and f3_val > 90000 and f1_val == '0':
                        schedule = "FullOnly"
                    # No Incr schedule exist in the policy at all - Incr backup
                    # instead of Full - ALERT
                    elif 0 < f2_val < 90000 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "FullOnlyMisc"
                    # No Full schedule exist in the policy at all - Incr backup
                    # only will start - ALERT
                    elif f2_val > 90000 and 0 < f3_val < 90000 and f1_val == '0':
                        schedule = "IncrOnlyMisc"
                    # No Full schedule exist in the policy at all - Incr backup
                    # only will start - ALERT
                    elif f2_val > 90000 and 0 < f3_val < 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "IncrOnly"
                    # No Incr schedule exist in the policy at all - Policy
                    # misconfigured but no backup will start - OK
                    elif f2_val == 0 and f3_val > 90000 and f1_val == '0':
                        schedule = "FullSchedOnlyNoBckFull"
                    # No Incr schedule exist in the policy at all - Policy
                    # misconfigured but no backup will start - WARNING (few
                    # chance to exist)
                    elif f2_val == 0 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "FullSchedOnlyNoBckIncr"
                    # No Full schedule exist in the policy at all - Policy
                    # misconfigured and no backup will start - WARNING
                    elif f2_val > 90000 and f3_val == 0 and f1_val == '0':
                        schedule = "IncrSchedOnlyNoBckFull"
                    # No Full schedule exist in the policy at all - Policy
                    # misconfigured and no backup will start - WARNING
                    elif f2_val > 90000 and f3_val == 0 and f1_val == '1' or f1_val == '4':
                        schedule = "IncrSchedOnlyNoBckIncr"
                    # No Full and Incr schedule exist in the policy at all - no
                    # backup will start from this policy - WARNING
                    elif f2_val > 90000 and f3_val > 90000 and f1_val == '0':
                        schedule = "NoScheduleFull"
                    # No Full and Incr schedule exist in the policy at all - no
                    # backup will start from this policy - WARNING
                    elif f2_val > 90000 and f3_val > 90000 and f1_val == '1' or f1_val == '4':
                        schedule = "NoScheduleIncr"
                    else:
                        schedule = "ERROR"

                    full_data_found = check_for_any_full(data_sequence)

                    if schedule in misc_list and not full_data_found:
                        schedule = 'FullMissing'
                    chances += [{'Server': file1_val[0], 'ServerType':file1_val[1], 'status':schedule}]

        # return file1.txt file contents and resulted data list.
        return file1_data, chances

    def run(self):
        file1_data, output_data = self.check_and_return()

        if file1_data is None:
            return

        # print 'No output data is found from check_and_return() method of 24h3ViewBackupScheduleInput.py.'
        #APP_LOGGER.log_warning('No output data is found from check_and_return() method of 24h3ViewBackupScheduleInput.py.')

        # We have the data. So we now need to write it to out file.
        print '%s INFO 06.InputLiveView.py  Saving output to: %s' % (get_date(), OUTPUT_FILE)
        APP_LOGGER.log_info('Saving output to: %s' % OUTPUT_FILE)
        FileHandler.write_output(file1_data, output_data, OUTPUT_FILE)

def get_date():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def run_main():
    print '%s INFO 06.InputLiveView.py  Start Generating input.txt...' % get_date()
    APP_LOGGER.log_info('Start Generating input.txt...')
    start_time = unix_time(datetime.now())

    if not APP_LOGGER.error:

        if not COLUMN_FIVE_PERCENTAGE:
            APP_LOGGER.log_warning('%s must be a valid value.' % COLUMN_FIVE_PERCENTAGE)
            print '%s WARNING 06.InputLiveView.py  %s must be a valid value.' % (get_date(), COLUMN_FIVE_PERCENTAGE)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        try:
            float(COLUMN_FIVE_PERCENTAGE)
        except Exception as msg:
            APP_LOGGER.log_warning('%s must be a valid value.' % COLUMN_FIVE_PERCENTAGE)
            print '%s WARNING 06.InputLiveView.py  %s must be a valid value.' % (get_date(), COLUMN_FIVE_PERCENTAGE)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.isfile(FILE1_NAME):
            APP_LOGGER.log_warning('%s is not a valid file.' % FILE1_NAME)
            print '%s WARNING 06.InputLiveView.py  %s is not a valid file.' % (get_date(), FILE1_NAME)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.isfile(FILE2_NAME):
            APP_LOGGER.log_warning('%s is not a valid file.' % FILE2_NAME)
            print '%s WARNING 06.InputLiveView.py  %s is not a valid file.' % (get_date(), FILE2_NAME)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.isfile(FILE3_NAME):
            APP_LOGGER.log_warning('%s is not a valid file.' % FILE3_NAME)
            print '%s WARNING 06.InputLiveView.py  %s is not a valid file.' % (get_date(), FILE3_NAME)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.isfile(HISTORY_FILE_NAME):
            APP_LOGGER.log_warning(
                '%s is not a valid file' %
                HISTORY_FILE_NAME)
            print '%s WARNING 06.InputLiveView.py  %s is not a valid file' % (get_date(), HISTORY_FILE_NAME)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.isfile(CALENDAR_FILE_NAME):
            APP_LOGGER.log_warning('%s is not a valid file' % CALENDAR_FILE_NAME)
            print '%s WARNING 06.InputLiveView.py  %s is not a valid file' % (get_date(), CALENDAR_FILE_NAME)
            print '%s WARNING 06.InputLiveView.py  Program is exiting...' % get_date()
            return
        if not os.path.exists(NOSCHEDULT_DATA_FILE):
            with open(NOSCHEDULT_DATA_FILE, 'w'):
                pass

        if not os.path.exists(INACTIVE_POLICIES_DATA_FILE):
            with open(INACTIVE_POLICIES_DATA_FILE, 'w'):
                pass

        Main().run()
        try:
            pass
            # Main().run()
        except Exception as msg:
            print '%s ERROR 06.InputLiveView.py  Exception occured in main block. Exception message: %s' % (get_date(), str(msg))
            APP_LOGGER.log_error('Exception occured. Exception message: %s' % str(msg))

    print '%s INFO 06.InputLiveView.py  noschedules reporting file: %s' % (get_date(), NOSCHEDULT_DATA_FILE)
    APP_LOGGER.log_info('noschedules reporting file: %s' % NOSCHEDULT_DATA_FILE)

    print '%s INFO 06.InputLiveView.py  inactive policy reporting file: %s' % (get_date(), INACTIVE_POLICIES_DATA_FILE)
    APP_LOGGER.log_info('inactive policy reporting file: %s' % INACTIVE_POLICIES_DATA_FILE)

    end_time = unix_time(datetime.now())
    print '%s INFO 06.InputLiveView.py  Time to run %s seconds' % (get_date(), str(end_time - start_time))
    APP_LOGGER.log_info('Time to run %s seconds' % str(end_time - start_time))

    print '%s INFO 07.InputLiveView.py  End Generating input.txt' % get_date()
    APP_LOGGER.log_info('End Generating input.txt')

if __name__ == "__main__":
    #try:
    run_main()
    #except:
    #    print '%s ERROR 06.InputLiveView.py  Script didn\'t complete successfully' % get_date()
    #    APP_LOGGER.log_error('Script didn\'t complete successfully.')
