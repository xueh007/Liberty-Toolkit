#
# IBM Confidential
# OCO Source Materials
# 5725-B69
# Copyright IBM Corp. 2015
# The source code for this program is not published or otherwise
# divested of its trade secrets, irrespective of what has
# been deposited with the U.S Copyright Office.
#

import os
import platform
import shutil

from commons import process
from serveradmin import AdminTask


if platform.system() == 'Windows':
    _SERVER = 'server.bat'
else: # Assuming Posix system
    _SERVER = 'server'
    
    
class Liberty(object):
    
    def __init__(self, liberty_home):
        self._liberty_home = liberty_home

    def get_home(self):
        return self._liberty_home
    
    def get_server_template_dir(self):
        return os.path.join(self.get_home(), 'templates', 'servers')
    
    def get_server(self, server_name):
        if not self._is_server_exist(server_name):
            raise LibertyException("the server named '{0}' doesn't exist".format(server_name))
        return LibertyServer(self, server_name)
    
    def start_server(self, server_name):
        _cmd = ['start', server_name]
        self._execute_cmd(_cmd)
    
    def stop_server(self, server_name):
        _cmd = ['stop', server_name]
        self._execute_cmd(_cmd)
    
    def create_server(self, server_name, template_name='defaultServer'):
        if self._is_server_exist(server_name):
            raise LibertyException("can not create a existed server named '{0}'".format(server_name))
        _cmd = ['create', server_name, '--template=' + template_name]
        self._execute_cmd(_cmd)
    
    def remove_server(self, server_name):
        if not self._is_server_exist(server_name):
            raise LibertyException("can not remove a non-existed server named '{0}'".format(server_name))
        usr_servers_dir = os.path.join(self._liberty_home, 'usr', 'servers', server_name)
        shutil.rmtree(usr_servers_dir)
    
    def _is_server_exist(self, server_name):
        return server_name in self.servers()
    
    def servers(self):
        names = []
        usr_servers_dir = os.path.join(self._liberty_home, 'usr', 'servers')
        for child in os.listdir(usr_servers_dir):
            child_path = os.path.join(usr_servers_dir, child)
            if not os.path.isdir(child_path):
                continue
            
            server_xml = os.path.join(child_path, 'server.xml')
            if os.path.exists(server_xml):
                names.append(child)
                
        return names
            
    def _execute_cmd(self, _cmd):
        _bin_dir = os.path.join(self.get_home(), 'bin')
        cmd = [os.path.join(_bin_dir, _SERVER)] + _cmd
        proc = process.SubProcess(cmd)
        proc.set_cwd(_bin_dir)
        return proc.run()
    

class LibertyServer(object):
    
    def __init__(self, liberty, server_name):
        self._liberty = liberty
        self._server_name = server_name
        self._config = None
        
    def get_name(self):
        return self._server_name
    
    def get_home(self):
        return os.path.join(self._liberty.get_home(), 'usr', 'servers', self.get_name())
    
    def get_apps_dir(self):
        return os.path.join(self.get_home(), 'apps')
    
    def start(self):
        self._liberty.start_server(self.get_name())
    
    def stop(self):
        self._liberty.stop_server(self.get_name())
    
    def get_server_xml(self):
        return os.path.join(self.get_home(), 'server.xml')
    
    def get_jvm_options(self):
        jvm_options = os.path.join(self.get_home(), 'jvm.properties') 
        if os.path.exists(jvm_options):
            return jvm_options
        
    def get_bootstrap_prop(self):
        bootstrap_prop = os.path.join(self.get_home(), 'bootstrap.properties') 
        if os.path.exists(bootstrap_prop):
            return bootstrap_prop
    
    def get_server_admin_task(self):
        return AdminTask(self)
    

class LibertyException (Exception):
    pass    