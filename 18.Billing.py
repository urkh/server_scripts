#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Codengine'

import time
from datetime import datetime
import csv
import collections
from LoggingManager import *
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('18.Billing')

page_title = config_vars.get('page_title')
value_undefined = config_vars.get('value_undefined')
backup_size_default = config_vars.get('backup_capacity_default')
additional_backup_size_default = config_vars.get('additional_backup_capacity_default')
additional_backup_price_per_gb_default = config_vars.get('additional_backup_price_per_gb_default')
backup_usage_default = config_vars.get('backup_usage_default')
total_backup_capacity_default = config_vars.get('total_backup_capacity_default')
total_backup_usage_default = config_vars.get('total_backup_usage_default')
total_backup_quota_default = config_vars.get('total_backup_quota_default')
bill_eoros_default = config_vars.get('bill_eoros_default')

backup_contract_file_path = config_vars.get('backup_contract_file_path')
backup_customer_file_path = config_vars.get('backup_customer_file_path')
backup_usage_file_path = config_vars.get('backup_usage_file_path')
all_seq_file_path = config_vars.get('all_seq_file_path')
csv_report_path_default = config_vars.get("csv_report_path_default")
billing_file_path = config_vars.get('billing_file_path')
output_csv_path_default = config_vars.get("output_csv_path_default")
timetorun_file = config_vars.get('timetorun_file')
app_logger = LoggingManager('18.Billing.py')
dformat = '%Y-%m-%d %H:%M:%S'

class FileProcessor(object):
    def __init__(self):
        pass

    def process_backup_usage_file(self):
        file_contents = []
        with open(backup_usage_file_path,'r') as bu:
            file_contents = bu.readlines()

        file_contents = [line.replace('\n','').strip() for line in file_contents]

        if file_contents:
            file_contents = file_contents[1:]

        backup_usages = {}
        #Sample data: {"policy01_master":544,"policy_bengreen:123}
        for line in file_contents:
            line = line.replace('\n','').strip()
            if line:
                line_split = line.split(',')
                policy_name = line_split[0].strip()
                server_name = line_split[1].strip()
                backup_usage = line_split[2].strip()
                backup_usages[policy_name+"_"+server_name] = backup_usage
        return backup_usages

    def process_backup_contract_file(self):
        file_contents = []
        with open(backup_contract_file_path,'r') as bc:
            file_contents = bc.readlines()

        file_contents = [line.replace('\n','').strip() for line in file_contents]

        if file_contents:
            file_contents = file_contents[1:]

        backup_contracts = {}

        for line in file_contents:
            line = line.replace('\n','').strip()
            if line:
                line_split = line.split(',')
                cust_name = line_split[0].strip()
                cust_id = line_split[1].strip()
                default_backup_capacity = line_split[2].strip()
                additional_backup_capacity = line_split[3].strip()
                additional_backup_price_per_gb = line_split[4].strip()
                backup_contracts[cust_id] = {
                    "cust_name": cust_name,
                    "cust_id":cust_id,
                    "default_backup_capacity":default_backup_capacity,
                    "additional_backup_capacity":additional_backup_capacity,
                    "additional_backup_price_per_gb":additional_backup_price_per_gb
                }
        return backup_contracts

    def process_backupcustomer_file(self):
        file_contents = []
        with open(backup_customer_file_path,'r') as bf:
            file_contents = bf.readlines()

        file_contents = [line.replace('\n','').strip() for line in file_contents]

        #Now store to a dictionary where key will be customer ID and values will be the sequence.
        #like {
        #   "CUST01": {"p_s_u": [(policy01,master, 100),(policy01,master2,13),(policy01,bengreen,0)],"default_backup_capacity": value, additional_backup_capacity: value,
        # total_backup_capacity: value, total_backup_usage: value, total_backup_quota: value, additional_backup_price_per_gb: value, bill_uoros: value}
        # }

        if file_contents:
            file_contents = file_contents[1:]

        backup_contracts = self.process_backup_contract_file()
        backup_usages = self.process_backup_usage_file()

        calculate_total_backup_capacity = lambda dc,ns,abc: (dc * ns) + abc #dc = default backup capacity, ns = number of servers, abc = additional backup capacity.

        cust_entries = {}
        for line in file_contents:
            line = line.replace('\n','').strip()
            if line:
                line_split = line.split(',')
                policy_name = line_split[0].strip()
                server_name = line_split[1].strip()
                cust_name = line_split[2].strip()

                #import ipdb; ipdb.set_trace()
                cust_id = line_split[3].strip()


                if not cust_id:
                    cust_id = value_undefined
                    cust_name = value_undefined

                cust_record = cust_entries.get(cust_id)

                if cust_record:
                    #{
                    #   "p_s_u": [(policy_name, server_name, backup_usage)],
                    #   "cust_name": customer name,
                    #   "default_backup_capacity": value,
                    #   "server_count":server_count,
                    #   "additional_backup_capacity": value,
                    #   "total_backup_capacity": value,
                    #   "total_backup_usage": value,
                    #   "total_backup_quota": value,
                    #   "additional_backup_price_per_gb": value,
                    #   "bill_euros": value
                    #}

                    p_s_u = cust_record.get("p_s_u")
                    p_s_exist = False
                    for each_psu in p_s_u:
                        if each_psu[0] == policy_name and each_psu[1] == server_name:
                            p_s_exist = True
                            break
                    # temp = []
                    # for each_psu in p_s_u:
                    #     temp += [each_psu[1]]
                    server_count = len(cust_record.get("p_s_u"))

                    if not p_s_exist:
                        backup_usage_val = backup_usages.get(policy_name+"_"+server_name)
                        if not backup_usage_val:
                            backup_usage_val = backup_usage_default
                        p_s_u += [(policy_name,server_name,backup_usage_val)]

                    total_backup_usage = 0
                    if cust_id == value_undefined:
                        total_backup_usage = value_undefined
                    else:
                        for each_psu in p_s_u:
                            total_backup_usage += float(each_psu[2])

                    total_backup_capacity = 0
                    if cust_id == value_undefined:
                        total_backup_capacity = value_undefined
                    else:
                        total_backup_capacity = calculate_total_backup_capacity(float(cust_record.get("default_backup_capacity")),server_count + 1,float(cust_record.get("additional_backup_capacity")))

                    total_backup_quota = 0
                    if cust_id == value_undefined:
                        total_backup_quota = value_undefined
                    else:
                        total_backup_quota = float(total_backup_capacity) - total_backup_usage

                    bill_euros = 0
                    if cust_id == value_undefined:
                        bill_euros = value_undefined
                    else:
                        if total_backup_quota < 0:
                            bill_euros = float(total_backup_quota) * float(cust_record.get("additional_backup_price_per_gb")) * -1

                    modified_record = {
                        "p_s_u": p_s_u,
                        "cust_name": cust_name,
                        "default_backup_capacity": cust_record.get("default_backup_capacity"),
                        "additional_backup_capacity": cust_record.get("additional_backup_capacity"),
                        "total_backup_capacity": total_backup_capacity,
                        "total_backup_usage": total_backup_usage,
                        "total_backup_quota": total_backup_quota,
                        "additional_backup_price_per_gb": cust_record.get("additional_backup_price_per_gb"),
                        "bill_euros": bill_euros
                    }
                    cust_entries[cust_id] = modified_record

                else:
                    backup_usage_val = backup_usages.get(policy_name+"_"+server_name)
                    if not backup_usage_val:
                        backup_usage_val = backup_usage_default
                    p_s_u = [(policy_name,server_name,backup_usage_val)]

                    # temp = []
                    # for each_psu in p_s_u:
                    #     temp += [each_psu[1]]
                    server_count = len(p_s_u)
                    #print cust_id
                    cust_backup_contract_record = backup_contracts.get(cust_id)

                    default_backup_capacity = backup_size_default
                    if cust_id == value_undefined:
                        default_backup_capacity = value_undefined
                    else:
                        default_backup_capacity = cust_backup_contract_record.get("default_backup_capacity")
                        if not default_backup_capacity:
                            default_backup_capacity = backup_size_default

                    additional_backup_capacity = additional_backup_size_default
                    if cust_id == value_undefined:
                        additional_backup_capacity = value_undefined
                    else:
                        additional_backup_capacity = cust_backup_contract_record.get("additional_backup_capacity")
                        if not additional_backup_capacity:
                            additional_backup_capacity = additional_backup_size_default

                    additional_backup_price_per_gb = additional_backup_price_per_gb_default
                    if cust_id == value_undefined:
                        additional_backup_price_per_gb = value_undefined
                    else:
                        additional_backup_price_per_gb = cust_backup_contract_record.get("additional_backup_price_per_gb")
                        if not additional_backup_price_per_gb:
                            additional_backup_price_per_gb = additional_backup_price_per_gb_default

                    total_backup_capacity = 0
                    if cust_id == value_undefined:
                        total_backup_capacity = value_undefined
                    else:
                        try:
                            total_backup_capacity = calculate_total_backup_capacity(float(default_backup_capacity),1,float(additional_backup_capacity))
                        except Exception,msg:
                            dt = datetime.now()
                            print "%s WARNING 18.Billing.py  Exception occured while calculating total backup capacity." % dt.strftime(dformat)
                            app_logger.log_warning("Exception occured while calculating total backup capacity.")

                    total_backup_usage = backup_usage_val
                    if cust_id == value_undefined:
                        total_backup_usage = value_undefined

                    total_backup_quota = 0
                    if cust_id == value_undefined:
                        total_backup_quota = value_undefined
                    else:
                        try:
                            total_backup_quota = float(total_backup_capacity) - float(total_backup_usage)
                        except Exception,msg:
                            dt = datetime.now()
                            print "%s WARNING 18.Billing.py  Exception ocured while calculating total backup quota." % dt.strftime(dformat)
                            app_logger.log_warning("Exception ocured while calculating total backup quota.")

                    bill_euros = 0
                    if cust_id == value_undefined:
                        bill_euros = value_undefined
                    else:
                        if total_backup_quota < 0:
                            try:
                                bill_euros = float(total_backup_quota) * float(additional_backup_price_per_gb) * -1
                            except Exception,msg:
                                dt = datetime.now()
                                print "%s WARNING 18.Billing.py  Exception occured while calculating backup quota." % dt.strftime(dformat)
                                app_logger.log_warning("Exception occured while calculating backup quota.")
                    cust_entries[cust_id] = {
                        "p_s_u": p_s_u,
                        "cust_name": cust_name,
                        "default_backup_capacity": default_backup_capacity,
                        "additional_backup_capacity": additional_backup_capacity,
                        "total_backup_capacity": total_backup_capacity,
                        "total_backup_usage": total_backup_usage,
                        "total_backup_quota": total_backup_quota,
                        "additional_backup_price_per_gb": additional_backup_price_per_gb,
                        "bill_euros": bill_euros
                    }
        return cust_entries

class Billing:
    def __init__(self):
        pass

    def get_static_page_upper(self):

        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')
        _timetorun = open(timetorun_file, 'r').readlines()[-1]

        html = """<!DOCTYPE html>"""
        html += """\n<html>"""
        html += """\n   <head>"""
        html += """\n       <meta charset="utf-8" />"""
        html += """\n       <title>"""+ page_title +"""</title>"""
        html += """\n       <link rel="stylesheet" type="text/css" href="css/view.css">"""
        html += """\n   </head>"""
        html += """\n   <body>"""
        html += """\n       <div style="visibility: hidden; position: absolute; overflow: hidden; padding: 0px; width: auto; left: 0px; top: 0px; z-index: 1010;" id="WzTtDiV"></div>"""
        html += """\n       <script type="text/javascript" src="js/wz_tooltip.js"></script>"""
        html += """\n       <table class="BackupTimeRun" align="right">"""
        html += """\n         <tbody>"""
        html += """\n           <tr>"""
        html += """\n             <td>Time to Run:<br>""" + _timetorun + """</td>"""
        html += """\n           </tr>"""
        html += """\n         </tbody>"""
        html += """\n       </table>"""
        html += """\n       <table class="BackupDataTime" align="right">"""
        html += """\n           <tbody>"""
        html += """\n               <tr>"""
        html += """\n                   <td> Last Updated:<br>"""+ str(timenow) +"""</td>"""
        html += """\n               </tr>"""
        html += """\n           </tbody>"""
        html += """\n       </table>"""
        html += """\n       <div id='logo'>"""
        html += """\n           <header>"""
        html += """\n               <div id='header'></div>\n           <div id='headerbar'></div>"""
        html += """\n               <div>"""
        html += """\n                   <img src="img/version.png" alt="version logo" id="version"/>"""
        html += """\n               </div>"""
        html += """\n           </header>"""
        html += """\n       </div>"""
        html += """\n       <nav>"""
        html += """\n           <ul id="menubar">"""
        html += """\n               <li><a href="./index.html">Dashboard</a></li>"""
        html += """\n               <li><a href="./reports.html">Reports</a></li>"""
        html += """\n               <li><a href="./policyconfig.html">Policy Config</a></li>"""
        html += """\n               <li><a href="./backupsize.html">Backup Size</a></li>"""
        html += """\n               <li><a href="./catalog.html">Catalog</a></li>"""
        html += """\n               <li><a href="./backupwritetime.html">Bck Write Time</a></li>"""
        html += """\n               <li><a href="./billing.html" class="selected">Billing</a></li>"""
        html += """\n               <li><a href="./help.html">Help</a></li>"""
        html += """\n           </ul>"""
        html += """\n       </nav>"""
        html += """\n       <div id='body'></div>"""
        html += """\n       <p>"""
        html += """\n           <a href='"""+ csv_report_path_default +"""' style="text-decoration: underline; float: right";>csv download</a>"""
        html += """\n       </p>"""
        return html

    def get_static_page_lower(self):
        timenow = datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')
        html = """\n        <p></p>"""
        html += """*Backup size in KB\n        <p></p>        <p>"""+ str(timenow) +"""</p>"""
        html += """\n    </body>"""
        html += """\n</html>"""
        return html

    def generate_data_table(self):
        table_header =  """\n       <table class="BackupData2">"""
        table_header += """\n           <tbody>"""
        table_header += """\n               <tr>"""
        table_header += """\n                   <td class="polconfighead">Customer Name</td>"""
        table_header += """\n                   <td class="polconfighead">Customer ID</td>"""
        table_header += """\n                   <td class="polconfighead">Policy Name</td>"""
        table_header += """\n                   <td class="polconfighead">Server Name</td>"""
        table_header += """\n                   <td class="polconfighead">Backup Usage*</td>"""
        table_header += """\n                   <td class="polconfighead">Server Numbers</td>"""
        table_header += """\n                   <td class="polconfighead">Default Backup Capacity*</td>"""
        table_header += """\n                   <td class="polconfighead">Additional Backup Capacity*</td>"""
        table_header += """\n                   <td class="polconfighead">TOTAL Backup Capacity*</td>"""
        table_header += """\n                   <td class="polconfighead">TOTAL Backup Usage*</td>"""
        table_header += """\n                   <td class="polconfighead">TOTAL Backup Quota*</td>"""
        table_header += """\n                   <td class="polconfighead">Additional Backup Price per GB</td>"""
        table_header += """\n                   <td class="polconfighead">To Bill in Euros</td>"""
        table_header += """\n               </tr>"""

        html = table_header

        file_processor = FileProcessor()

        cust_entries = file_processor.process_backupcustomer_file()

        def prepare_rows(key,record,class_name):
            row_span_one = len(record.get("p_s_u")) + 1
            row_span_two = len(record.get("p_s_u"))
            #{
            #   "p_s_u": [(policy_name, server_name, backup_usage)],
            #   "cust_name": customer name,
            #   "default_backup_capacity": value,
            #   "additional_backup_capacity": value,
            #   "total_backup_capacity": value,
            #   "total_backup_usage": value,
            #   "total_backup_quota": value,
            #   "additional_backup_price_per_gb": value,
            #   "bill_euros": value
            #}
            cust_name = record.get("cust_name")

            data_row = """\n               <tr>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_one) +"""\">"""+ cust_name +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_one) +"""\">"""+ key +"""</td>"""
            data_row += """\n               </tr>"""

            ###Get the first policy, server, usage tuple.
            first_psu = record.get("p_s_u")[0]
            data_row += """\n               <tr>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ first_psu[0] +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ first_psu[1] +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ first_psu[2] +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(len(record.get("p_s_u"))) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("default_backup_capacity")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("additional_backup_capacity")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("total_backup_capacity")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("total_backup_usage")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("total_backup_quota")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("additional_backup_price_per_gb")) +"""</td>"""
            data_row += """\n                   <td class=\""""+ class_name +"""\" rowspan=\""""+ str(row_span_two) +"""\">"""+ str(record.get("bill_euros")) +"""</td>"""
            data_row += """\n               </tr>"""

            remaining_psu = record.get("p_s_u")[1:]
            for each_psu in remaining_psu:
                data_row += """\n               <tr>"""
                data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ each_psu[0] +"""</td>"""
                data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ each_psu[1] +"""</td>"""
                data_row += """\n                   <td class=\""""+ class_name +"""\">"""+ each_psu[2] +"""</td>"""
                data_row += """\n               </tr>"""
            return data_row

        record_undefined_key = None
        record_undefined_value = None

        csv_contents = [
            ["Customer Name","Customer ID","Policy Name","Server Name","Backup Usage*","Server Numbers","Default Backup Capacity*","Additional Backup Capacity*",
             "TOTAL Backup Capacity*","TOTAL Backup Usage*","TOTAL Backup Quota*","Additional Backup Price per GB","To Bill in Euros"]
        ]

        ###Now sort customer entries by customer name.
        temp = []

        for key,value in cust_entries.items():
            temp += [{key: value}]

        temp = sorted(temp,key=lambda x: x.values()[0]["cust_name"])

        original_dict = collections.OrderedDict()

        for item in temp:
            for key,value in item.items():
                original_dict[key] = value

        cust_entries = original_dict

        class_name = "polconfig1"
        for key, record in cust_entries.items():
            #Process csv data.
            csv_row = []
            csv_row += [record.get("cust_name")]
            csv_row += [key]

            p_s_u = record.get("p_s_u")
            p_s_u_sorted = sorted(p_s_u,key=lambda x: (x[0],x[1]))
            policies = []
            servers = []
            usages = []
            for each in p_s_u_sorted:
                policies += [each[0]]
                servers += [each[1]]
                usages += [each[2]]

            csv_row += [" ".join(policies)]
            csv_row += [" ".join(servers)]
            csv_row += [" ".join(usages)]
            csv_row += [len(p_s_u)]
            csv_row += [record.get("default_backup_capacity")]
            csv_row += [record.get("additional_backup_capacity")]
            csv_row += [record.get("total_backup_capacity")]
            csv_row += [record.get("total_backup_usage")]
            csv_row += [record.get("total_backup_quota")]
            csv_row += [record.get("additional_backup_price_per_gb")]
            csv_row += [record.get("bill_euros")]

            csv_contents += [csv_row]

            record["p_s_u"] = p_s_u_sorted

            if key == value_undefined:
                record_undefined_key = key
                record_undefined_value = record
                continue

            data_row = prepare_rows(key,record,class_name)

            if class_name == "polconfig1":
                class_name = "polconfig2"
            else:
                class_name = "polconfig1"

            html += data_row

        if record_undefined_value:
            class_name = "polconfig3"
            data_row = prepare_rows(record_undefined_key,record_undefined_value,class_name)
            html += data_row

        html += """\n           </tbody>"""
        html += """\n       </table>"""
        return html,csv_contents

    def generate_page(self):
        html = self.get_static_page_upper()
        data_table,csv_contents = self.generate_data_table()
        html += data_table
        html += self.get_static_page_lower()
        return html,csv_contents

def run_main():
    dformat = '%Y-%m-%d %H:%M:%S'
    dt = datetime.now()

    if not page_title:
        print '%s WARNING 18.Billing.py  Page title is not set.' % dt.strftime(dformat)
        app_logger.log_warning('Page title is not set.')

    if not os.path.isfile(backup_contract_file_path):
        print '%s ERROR 18.Billing.py  %s is not a valid file.' % (dt.strftime(dformat), backup_contract_file_path)
        app_logger.log_error('%s is not a valid file.' % backup_contract_file_path)
        
        print '%s INFO 18.Billing.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(backup_customer_file_path):
        print '%s ERROR 18.Billing.py  %s is not a valid file.' % (dt.strftime(dformat), backup_customer_file_path)
        app_logger.log_error('%s is not a valid file.' % backup_customer_file_path)
        
        print '%s INFO 18.Billing.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(backup_usage_file_path):
        print '%s ERROR 18.Billing.py  %s is not a valid file.' % (dt.strftime(dformat), backup_usage_file_path)
        app_logger.log_error('%s is not a valid file.' % backup_usage_file_path)
        
        print '%s INFO 18.Billing.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    if not os.path.isfile(all_seq_file_path):
        print '%s ERROR 18.Billing.py  %s is not a valid file.' % (dt.strftime(dformat), all_seq_file_path)
        app_logger.log_error('%s is not a valid file.' % all_seq_file_path)
        
        print '%s INFO 18.Billing.py  Exiting program...' % dt.strftime(dformat)
        app_logger.log_info('Exiting program...')
        return

    billing = Billing()
    html_page,csv_contents = billing.generate_page()
    ###Now save the html page.
    dt = datetime.now()
    print "%s INFO 18.Billing.py  Saving output page to: %s" % (dt.strftime(dformat), billing_file_path)
    app_logger.log_info("Saving output page to: %s" % billing_file_path)
    with open(billing_file_path,'w') as bf:
        bf.write(html_page)
    
    dt = datetime.now()
    print "%s INFO 18.Billing.py  Page saved." % dt.strftime(dformat)
    app_logger.log_info("Page saved.")
    
    print "%s INFO 18.Billing.py  Generating CSV file..." % dt.strftime(dformat)
    app_logger.log_info("Generating CSV file...")

    print '%s INFO 18.Billing.py  CSV file is saving to: %s' % (dt.strftime(dformat), output_csv_path_default)
    app_logger.log_info('CSV file is saving to: %s' % output_csv_path_default)

    with open(output_csv_path_default, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(csv_contents)

    dt = datetime.now()
    print '%s INFO 18.Billing.py  Saved.' % dt.strftime(dformat)
    app_logger.log_info('Saved.')

def unix_time(dt):
    return int(time.mktime(dt.timetuple()))

if __name__ == "__main__":
    dformat = '%Y-%m-%d %H:%M:%S'
    dt = datetime.now()
    print '%s INFO 18.Billing.py  Program is starting...' % dt.strftime(dformat)
    app_logger.log_info('Program is starting...')

    dt = datetime.now()
    print '%s INFO 18.Billing.py  Started running...' % dt.strftime(dformat)
    app_logger.log_info('Started running...')
    
    dt = datetime.now()
    start_time = unix_time(dt)
    dt = datetime.now()
    end_time = unix_time(dt)
    
    #try:
    run_main()
    #except:
    #    print '%s ERROR 18.Billing.py  Script didn\'t complete successfully.' % dt.strftime('%Y-%m-%d %H:%M:%S')
    #    app_logger.log_error('Script didn\'t complete successfully.')
        
    dt = datetime.now()
    print '%s INFO 18.Billing.py  Time to run %s seconds.' % (dt.strftime(dformat), str(end_time-start_time))
    app_logger.log_info('Time to run %s seconds.' % str(end_time-start_time))
    
    dt = datetime.now()
    print '%s INFO 18.Billing.py  Ended running...' % dt.strftime(dformat)
    app_logger.log_info('Ended running...')
