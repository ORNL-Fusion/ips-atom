#! /usr/bin/env python

from  component import Component
import os

class iter_data_driver(Component):
    def __init__(self, services, config):
        Component.__init__(self, services, config)
        print 'Created %s' % (self.__class__)

    def init(self, timeStamp=0.0):

        solps_plasma_state_files = self.services.get_config_param('PLASMA_STATE_FILES')
        ##split filenames into a list of strings
        file_list = solps_plasma_state_files.split()
        ##loop over file names and create dummy files in ftridynInit work area
        for index in range(len(file_list)):
            if os.path.isfile(file_list[index]) == 0 :
                open(file_list[index], 'a').close()

        #update plasma state from relevant files in ftridynInit work area
        self.services.update_plasma_state()        
        return

    def step(self, timeStamp=0.0):
        print 'solss-iter-data-driver: beginning step call' 
        try:
            worker_comp = self.services.get_port('WORKER')
        except Exception:
            self.services.exception('Error accessing worker component')
            raise
        self.services.call(worker_comp, 'step', 0.0)
        print 'solps-iter-data-driver: finished worker call' 
        return

    def finalize(self, timeStamp=0.0):
        return
