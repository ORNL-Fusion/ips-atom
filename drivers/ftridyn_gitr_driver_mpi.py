#! /usr/bin/env python

from  component import Component
import os
import numpy as np

class ftridyn_gitr_driver(Component):
    def __init__(self, services, config):
        Component.__init__(self, services, config)
        print 'Created %s' % (self.__class__)

    def init(self, timeStamp=0.0):

        current_namelist = self.services.get_config_param('PLASMA_STATE_FILES')
        ##split filenames into a list of strings
        file_list = current_namelist.split()
        ##loop over file names and create dummy files in ftridynInit work area
        for index in range(len(file_list)):
            if os.path.isfile(file_list[index]) == 0 :
                open(file_list[index], 'a').close()

        #update plasma state from relevant files in work area
        self.services.update_plasma_state()        

        #Get info from config file about port 'WORKER'
        self.ftridyn_comp = self.services.get_port('WORKER')
        self.gitr_comp = self.services.get_port('GWORKER')

        self.services.call(self.gitr_comp, 'init', 0.0)

        return

    def step(self, timeStamp=0.0):
        energies = self.ENERGY.split()
        if energies[0] == 'log' :
            en1 = float(energies[1])
            en2 = float(energies[2])
            nEnergies = int(energies[3])
            energy = np.logspace(en1, en2, num=nEnergies, base=10.0)
        else :
            energy = [float(i) for i in self.ENERGY.split()]
        angle = [float(i) for i in self.ANGLE.split()]
        roughness = [float(i) for i in self.ROUGHNESS.split()]
        

        #call init method of WORKER ('ftridyn_worker.py')
        self.services.call(self.ftridyn_comp, 'init', timeStamp,ffilename = self.FILENAME, beam = self.BEAM,target = self.TARGET,nH = int(self.NH), eArg =energy,aArg = angle,dArg = roughness)
                    
        #call step method of WORKER ('ftridyn_worker.py')
        self.services.call(self.ftridyn_comp, 'step', timeStamp,ffilename = self.FILENAME, beam = self.BEAM,target = self.TARGET,nH = int(self.NH),eArg =energy,aArg = angle,dArg = roughness )
        self.services.call(self.gitr_comp, 'step', 0.0) 
    def finalize(self, timeStamp=0.0):
        print('ftridyn_driver: finalize')
        self.services.call(self.ftridyn_comp, 'finalize', timeStamp)
