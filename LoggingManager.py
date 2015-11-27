#! /usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
import logging
from GlobalConfig import *

config_vars = GlobalConfig.read_vars('LOGGING')

application_name = config_vars.get('application_name')
log_file_path = config_vars.get('log_file_path')

class LoggingManager:
    def __init__(self,script_name):
        if not os.path.isfile(log_file_path):
            print '%s is not a valid file' % log_file_path
            print 'Exiting...'
            self.error = True
            return
        self.error = False
        self.logger = logging.getLogger(application_name)
        self.hdlr = logging.FileHandler(log_file_path)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s '+script_name+'  %(message)s','%Y-%m-%d %H:%M:%S')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)

    def log_error(self,msg):
        self.logger.setLevel(logging.ERROR)
        self.logger.error(msg)

    def log_info(self,msg):
        self.logger.setLevel(logging.INFO)
        self.logger.info(msg)

    def log_warning(self,msg):
        self.logger.setLevel(logging.WARNING)
        self.logger.warning(msg)

if __name__ == '__main__':
    log_manager = LoggingManager('LoggingManager.py')
    if not log_manager.error:
        log_manager.log_info('Hello, this is test message! :)')
    else:
        print 'Program exiting...'


