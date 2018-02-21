#! /usr/bin/env python

#-------------------------------------------------------------------------------
#
#  IPS wrapper for VMEC component. This wapper only takes a VMEC input file and
#  runs VMEC.
#
#-------------------------------------------------------------------------------

from component import Component
import os

#-------------------------------------------------------------------------------
#
#  Helper function to detect the end of a namelist input file. This finds if the
#  '/' character is found withing a string. However, this if this character is
#  is located after a '!' character or between '\'' characters ignore it.
#
#-------------------------------------------------------------------------------
def contains_end(line):
    
#  Check and remove every character after the !.
    line = line.split('!')[0]
    
    if (line == ''):
        return False, ''
    
    if (line[0] == '/'):
        return True, ''

    in_single_quote = line[0] == '\''
    in_double_quote = line[0] == '\"'
    
    for i, c in enumerate(line[1:]):
        
#  Do not close the quote when a single quote is encounterd in the following
#  situations.
#
#  '\''
#  "'"
        if ((c == '\'') and line[i - 1] != '\\' and not in_double_quote):
            in_single_quote = not in_single_quote
        
#  Do not close the quote when a single quote is encounterd in the following
#  situations.
#
#  "\""
#  '"'
        elif ((c == '\"') and line[i - 1] != '\\' and not in_single_quote):
            in_double_quote = not in_double_quote
        elif ((c == '/') and not in_double_quote and not in_single_quote):
            return True, line[:i]
        elif ((c == '&') and not in_double_quote and not in_single_quote):
            if (i + 4 <= len(line)) and (line[i:i + 4] == '&end'):
                return TRUE, line[:i]

    return False, ''

#-------------------------------------------------------------------------------
#
#  VMEC Component Constructor
#
#-------------------------------------------------------------------------------
class vmec(Component):
    def __init__(self, services, config):
        print('vmec: Construct')
        Component.__init__(self, services, config)
        
        self.vmec_exe = self.VMEC_EXE

#-------------------------------------------------------------------------------
#
#  VMEC Component init method. This method prepairs the namelist input file.
#
#-------------------------------------------------------------------------------
    def init(self, timeStamp=0.0, **keywords):
        print('vmec: init')
        self.services.stage_plasma_state()
        
        self.current_vmec_namelist = self.services.get_config_param('CURRENT_VMEC_NAMELIST')

        params = keywords['name_list_params']

#  Append the new parameters to the end of the namelist input file before the
#  end. Mark the start of the dakota parameter with a comment. To avoid
#  littering the namelist file. NAMELIST_FILE should reference a file in the
#  plasma state.
        
        vmec_namelist = open(self.current_vmec_namelist, 'r')
        vmec_namelist_lines = vmec_namelist.readlines()
        vmec_namelist.close()

#  Reopen for writting.
        vmec_namelist = open(self.current_vmec_namelist, 'w')

        for line in vmec_namelist_lines:
#  Name list input files can have strings containing path separators. Check for
#  an equals sign to avoid these.
            end_found, short_line = contains_end(line)
            if (end_found):
                vmec_namelist.write(short_line)
                vmec_namelist.write('\n!  VMEC params\n')
                for key, value in params.iteritems():
                    vmec_namelist.write('%s = %s\n'%(key, value))
                vmec_namelist.write('/\n')
                break
            elif ('!  VMEC params\n' in line):
                vmec_namelist.write(line)
                for key, value in params.iteritems():
                    vmec_namelist.write('%s = %s\n'%(key, value))
                vmec_namelist.write('/\n')
                break
            else:
                vmec_namelist.write(line)

        vmec_namelist.close()

#-------------------------------------------------------------------------------
#
#  VMEC Component step method. This runs vmec.
#
#-------------------------------------------------------------------------------
    def step(self, timeStamp=0.0):
        print('vmec: step')

        task_id = self.services.launch_task(self.NPROC,
                                            self.services.get_working_dir(),
                                            self.VMEC_EXE,
                                            self.current_vmec_namelist,
                                            logfile = 'vmec.log')
    
        if (self.services.wait_task(task_id)):
            self.services.error('vmec: step failed.')

        self.services.update_plasma_state()

#-------------------------------------------------------------------------------
#
#  VMEC Component finalize method. This cleans up afterwards. Not used.
#
#-------------------------------------------------------------------------------
    def finalize(self, timeStamp=0.0):
        print('vmec: finalize')