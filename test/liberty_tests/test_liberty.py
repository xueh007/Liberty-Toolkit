import os
from unittest import TestCase

from liberty.liberty import Liberty, LibertyException


class LibertyTest (TestCase):
    
    def setUp(self):
        liberty_home = os.path.join(os.path.dirname(__file__), 'resources', 'wlp')
        self._liberty = MockLiberty(liberty_home)
    
    def test_list_server_names(self):
        names = self._liberty.servers()
        self.assertEquals(1, len(names))
        self.assertEquals('server1', names[0])
    
    def test_start_server(self):
        self._liberty.start_server('server1')
        self.assertEquals(['start', 'server1'], self._liberty.log[0])
    
    def test_stop_server(self):
        self._liberty.stop_server('server1')
        self.assertEquals(['stop', 'server1'], self._liberty.log[0])
    
    def test_create_server_by_template(self):
        self._liberty.create_server('newServer', 'templateServer')
        self.assertEquals(['create', 'newServer', '--template=templateServer'], self._liberty.log[0])
    
    def test_create_existed_server(self):
        try:
            self._liberty.create_server('server1')
            self.fail()
        except LibertyException:
            pass
    
    def test_remove_unexisted_server(self):
        try:
            self._liberty.remove_server('notExistServer')
            self.fail()
        except LibertyException:
            pass
    
    def test_get_server(self):
        server = self._liberty.get_server('server1')
        self.assertEquals('server1', server.get_name())
    
    def test_get_unexisted_server(self):
        try:
            self._liberty.get_server('notExistServer')
            self.fail()
        except LibertyException:
            pass


class MockLiberty(Liberty):
    
    def __init__(self, liberty_home):
        Liberty.__init__(self, liberty_home)
        self.log = []
    
    def _execute_cmd(self, _cmd):
        self.log.append(_cmd)