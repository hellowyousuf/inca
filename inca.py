'''
ooooo ooooo      ooo   .oooooo.         .o.       
`888' `888b.     `8'  d8P'  `Y8b       .888.      
 888   8 `88b.    8  888              .8"888.     
 888   8   `88b.  8  888             .8' `888.    
 888   8     `88b.8  888            .88ooo8888.   
 888   8       `888  `88b    ooo   .8'     `888.  
o888o o8o        `8   `Y8bood8P'  o88o     o8888o 
                                                  
Welcome to INCA

This module provides some data-scraping, searching and analysis functionality. 
You can run this locally, at a server, or perhaps on a cluster without too much
hassle. 

Please consult the `README.md` file for more information about setting up and
running INCA. 

Start an API server:
        `inca` 

Commandline usage: 
        `inca <function> <task> <arguments>` 
Example: 
        `inca scrapers tweedekamer_handelingen run`

'''

##### SETTINGS TEMPORARILY DEFINED HERE ######

LOCAL_ONLY = True
LOGLEVEL   = 'DEBUG'

##############################################

from celery import Celery
from flask import Flask
import sys
import os
import scrapers
import logging
import argparse
import core

logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)

api        = Flask(__name__)
taskmaster = Celery()

expose = [ "scrapers", "processors", "analysis"]

def show_functions():
    available_functions = """
    scrapers   : %s
        includes (`list` to see all options): %s
    processors : %s
        includes (`list` to see all options): %s
    analysis   : %s
        includes (`list` to see all options): %s
    """ %(
        core.scraper_class.Scraper.__doc__,
        show_tasks('scrapers',3),
        core.processor_class.Processer.__doc__,
        show_tasks('processors',3),
        'ANALYSIS NOT IMPLEMENTED YET',
        'NO ANALYSIS TASKS AVAILABLE YET'
        )
    return available_functions

def show_tasks(function, limit=0):
    helpstring = "{function} provides the following tasks:\n\n".format(**locals())
    for function_task in [taskname for taskname in taskmaster.tasks if taskname.split('.')[0]==function]:
        taskdoc  = taskmaster.tasks[function_task].__doc__
        taskname = function_task.split('.')[-1]
        helpstring += "\t\t{taskname} : {taskdoc}\n".format(**locals())
    return helpstring

def identify_task(function,task):
    options = taskmaster.tasks.keys()
    fit     = [option for option in options if option.split('.')[0]==function and option.split('.')[-1]==task]
    if len(fit)==1:
        return fit[0]
    elif len(fit)<1:
        print("Did not find `{task}` ".format(**locals()))
        return "help"
    else:
        n_options = len(fit)
        print("found {n_options} for {function}/{task}!".format(**locals()))
        return "help"
    
def handle(function, task, arguments=None):
    ''' this handler function calls the appropriate celery task'''
    task_key = identify_task(function,task)
    if task_key =='help':
        print(show_tasks(function))
    else:
        run_method = LOCAL_ONLY and 'run' or 'apply_async'
        getattr(taskmaster.tasks[task_key],run_method)()

if __name__ == '__main__':
    print(__doc__)
    parser = argparse.ArgumentParser()
    parser.add_argument('function', help="functions performed by INCA", default=False, nargs="?")
    parser.add_argument('task', help="a task to be preformed such as tokenizing, expanding urls...", default='list', nargs="?")
    parser.add_argument('task_args', help='arguments passed to task (not all tasks take arguments!)', nargs='*')
    parser.add_argument('-p','--port', help='set port for api server', default=5000, type=int)
    
    args = parser.parse_args()
    if not args.function:
        # run API server
        api.run()

    else:
        handle(args.function, args.task, args.task_args)
    