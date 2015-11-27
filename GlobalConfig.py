#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Codengine'

import os.path
import ConfigParser

#import ipdb; ipdb.set_trace()


#CONFIG_FILE_PATH = '/data/www/bengreen/nbumas/scripts/global_config.cfg'
CONFIG_FILE_PATH = '/home/urkh/proyectos/python/odesk/scripts/global_config.cfg'

config = ConfigParser.RawConfigParser()

config.read(CONFIG_FILE_PATH)

class GlobalConfig:
    def __init__(self):
        pass

    @staticmethod
    def read_vars(section_name):
        if not os.path.isfile(CONFIG_FILE_PATH):
            raise Exception('%s is not a valid file' % CONFIG_FILE_PATH)
        try:
            config_items = config.items(section_name)
            items = {}
            for item in config_items:
                items[item[0]] = item[1]
            return items
        except Exception,msg:
            print 'Exception in GlobalConfig.py file: %s' % msg
            return {}

if __name__ == '__main__':
    GlobalConfig.read_vars('')
