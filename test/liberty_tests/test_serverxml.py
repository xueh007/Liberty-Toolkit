import os
import unittest

from liberty.serverxml import Builder, XmlOutputter, ServerModel, FeatureManager, \
    HttpEndpoint, BasicRegistry, User, Group, Library, Fileset, JdbcDriver, \
    DB2JCCProp, OracleProp, Datasource, Application, \
    SecurityRole, Feature, KeyStore, ManagedExecutorService, SSL


class TestBuilder(unittest.TestCase):
    
    def setUp(self):
        self._builder = Builder()
    
    def test_build_server(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'server.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('server1', model.desc)
        
    def test_build_feature_manager(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'feature_manager.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual(['servlet-3.0', 'jsp-2.2'], model.list_features())

    def test_build_http_endpoint(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'http_endpoint.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('defaultHttpEndpoint', model.id)
        self.assertEqual('*', model.host)
        self.assertEqual('9080', model.http_port)
        self.assertEqual('9443', model.https_port)

    def test_build_basic_registry(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'basic_registry.xml')
        model = self._builder.build(xml_file)

        self.assertEqual('basic', model.id)
        self.assertEqual('customRealm', model.realm)
        
        self.assertEqual(4, model.children().__len__())
        
        self.assertEqual('resAdmin', model.children()[0].name)
        self.assertEqual('resAdmin_pwd', model.children()[0].password)
        self.assertEqual('resDeploy', model.children()[1].name)
        self.assertEqual('resDeploy_pwd', model.children()[1].password)
        
        self.assertEqual('resAdministrators', model.children()[2].name)
        self.assertEqual(['resAdmin'], model.children()[2].list_members())
        self.assertEqual('resDeployers', model.children()[3].name)
        self.assertEqual(['resAdmin', 'resDeploy'], model.children()[3].list_members())

    def test_build_jdbc_driver(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'jdbc_driver.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('db2-driver', model.id)
        self.assertEqual('db2Lib', model.library_ref)
        
        lib = model.find(Library)
        
        self.assertEqual('db2Lib', lib.id)
        self.assertEqual(1, len(lib.children()))
        self.assertEqual('lib', lib.children()[0].dir)
        self.assertEqual('*.jar', lib.children()[0].includes)

    def test_build_db2_datasource(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'db2_datasource.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('jdbc/ilogDataSource', model.id)
        self.assertEqual('TRANSACTION_READ_COMMITTED', model.isolation_level)
        self.assertEqual('jdbc/ilogDataSource', model.jndi)
        self.assertEqual('db2-driver', model.jdbc_driver_ref)
        
        prop = model.find(DB2JCCProp)
        self.assertEqual('odmdb', prop.database_name)
        self.assertEqual('ilog', prop.db_user)
        self.assertEqual('passw0rd', prop.db_password)
        self.assertEqual('localhost', prop.server_name)
        self.assertEqual('50000', prop.db_port)
        self.assertEqual('odm', prop.schema)
    
    def test_build_oracle_datasource(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'oracle_datasource.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('jdbc/resdatasource', model.id)
        self.assertEqual(None, model.isolation_level)
        self.assertEqual('jdbc/resdatasource', model.jndi)
        self.assertEqual('oracle-driver', model.jdbc_driver_ref)
        
        prop = model.find(OracleProp)
        self.assertEqual('odmdb', prop.database_name)
        self.assertEqual('ilog', prop.db_user)
        self.assertEqual('passw0rd', prop.db_password)
        self.assertEqual('localhost', prop.server_name)
        self.assertEqual('1521', prop.db_port)
        
    def test_build_application(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'application.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('testing', model.id)
        self.assertEqual('testing', model.name)
        self.assertEqual('war', model.type)
        self.assertEqual('${server.config.dir}/apps/testing.war', model.location)
        
        self.assertEqual(1, len(model.children()))
        
        app_bnd = model.children()[0]
        self.assertEqual(2, len(app_bnd.children()))
        
        security_role = app_bnd.children()[0]
        self.assertEqual('resAdministrators', security_role.name)
        self.assertEqual(1, len(security_role.children()))
        group = security_role.children()[0]
        self.assertEqual('resAdministrators', group.name)
        
        security_role = app_bnd.children()[1]
        self.assertEqual('resDeployers', security_role.name)
        self.assertEqual(1, len(security_role.children()))
        group = security_role.children()[0]
        self.assertEqual('resDeployers', group.name)
        
    def test_build_key_store(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'key_store.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('defaultKeyStore', model.id)
        self.assertEqual('tester', model.password)
        
    def test_build_managed_executor_srvice(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'managed_executor_srvice.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('concurrent/drExecutorService', model.jndi_name)
        
    def test_build_ssl(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'ssl.xml')
        model = self._builder.build(xml_file)
        
        self.assertEqual('defaultSSLConfig', model.id)
        self.assertEqual('defaultKeyStore', model.key_store_ref)
        self.assertEqual('TLS', model.ssl_protocol)
        

class TestXmlOutputter(unittest.TestCase):
    
    def _read_from_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        return content 
    
    def test_output_server(self):
        outputter = XmlOutputter()
        model = ServerModel()
        model.desc = 'NewServer01'
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_server.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_feature_manager(self):
        outputter = XmlOutputter()
        model = FeatureManager()
        model.add_features(['servlet-3.0', 'jsp-2.2', 'jsp-2.2'])
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_feature_manager.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_http_endpoints(self):
        outputter = XmlOutputter()
        model = HttpEndpoint()
        model.id = 'defaultHttpEndpoint'
        model.host = '*'
        model.http_port = '9080'
        model.https_port = '9443'
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_http_endpoints.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_basic_registry(self):
        outputter = XmlOutputter()
        model = BasicRegistry()
        model.id = 'basic'
        model.realm = 'customRealm'
        
        user = User()
        user.name = 'tester'
        user.password = 'tester_pwd'
        model.add(user)
        
        user = User()
        user.name = 'admin'
        user.password = 'passw0rd'
        model.add(user)
        
        group = Group()
        group.name = 'resAdministrators'
        group.add_members(['admin'])
        model.add(group)
        
        group = Group()
        group.name = 'resDeployers'
        group.add_members(['tester', 'admin'])
        model.add(group)
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_basic_registry.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_jdbc_driver(self):
        outputter = XmlOutputter()
        model = JdbcDriver()
        model.id = 'oracle-driver'
        model.library_ref = 'oracleLib'
        
        lib = Library()
        lib.id = 'oracleLib'
        model.add(lib)
        
        fileset = Fileset()
        fileset.dir = 'lib'
        fileset.includes = '*.jar'
        lib.add(fileset)
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_jdbc_driver.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_db2_datasource(self):
        outputter = XmlOutputter()
        model = Datasource()
        model.id = 'jdbc/ilogDataSource'
        model.isolation_level = 'TRANSACTION_READ_COMMITTED'
        model.jndi = 'jdbc/ilogDataSource'
        model.jdbc_driver_ref = 'db2-driver'
        
        prop = DB2JCCProp()
        prop.database_name = 'odmdb'
        prop.db_user = 'tester'
        prop.db_password = 'passw0rd'
        prop.server_name = 'localhost'
        prop.db_port = '50000'
        prop.schema = 'odm'
        model.add(prop)
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_db2_datasource.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
    
    def test_output_oracle_datasource(self):
        outputter = XmlOutputter()
        model = Datasource()
        model.id = 'jdbc/resdatasource'
        model.jndi = 'jdbc/resdatasource'
        model.jdbc_driver_ref = 'oracle-driver'
        
        prop = OracleProp()
        prop.database_name = 'odmdb'
        prop.db_user = 'tester'
        prop.db_password = 'passw0rd'
        prop.server_name = 'localhost'
        prop.db_port = '1521'
        model.add(prop)
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_oracle_datasource.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_application(self):
        outputter = XmlOutputter()
        model = Application()
        model.id = 'teamserver'
        model.location = '${server.config.dir}/apps/teamserver.war'
        model.name = 'teamserver'
        model.type = 'war'
        
        security_role = SecurityRole()
        security_role.name = 'rtsAdministrator'
        security_role.add_groups(['rtsAdministrator', 'test_group'])
        model.add_security_role(security_role)
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_application.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_output_key_store(self):
        outputter = XmlOutputter()
        model = KeyStore()
        model.id = 'defaultKeyStore'
        model.password = 'tester'
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_key_store.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_build_managed_executor_srvice(self):
        outputter = XmlOutputter()
        model = ManagedExecutorService()
        model.jndi_name = 'concurrent/drExecutorService'
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_managed_executor_service.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
    def test_build_ssl(self):
        outputter = XmlOutputter()
        model = SSL()
        model.id = 'test_ssl'
        model.key_store_ref = 'key_store'
        model.ssl_protocol = 'SSLv3'
        
        expect = os.path.join(os.path.dirname(__file__), 'resources', 'data', 'expect_ssl.txt') 
        self.assertEqual(self._read_from_file(expect), outputter.output(model))
        
        
class TestElementModel(unittest.TestCase):
    
    def _server_model(self):
        server = ServerModel()
        server.attributes = {'desc':'test_desc'}
        
        feature_manager = FeatureManager() 
        feature_manager.add_features(['test1', 'test2'])
        server.add(feature_manager)
        
        return server
        
    def test_get_set(self):
        server = self._server_model()
        self.assertEqual('test_desc', server.get('desc'))
        
        server.set('desc', 'test')
        self.assertEqual('test', server.get('desc'))
        
    def test_find(self):
        server = self._server_model()
        feature_manager = server.find(FeatureManager)
        
        self.assertEqual(['test1', 'test2'], feature_manager.list_features())
        
    def test_find_all(self):
        server = self._server_model()
        feature_manager = server.find(FeatureManager)
        
        features = feature_manager.find_all(Feature)
        self.assertEqual(2, len(features))
        self.assertEqual('test1', features[0].value)
        self.assertEqual('test2', features[1].value)