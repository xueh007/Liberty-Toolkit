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
import shutil

from serverxml import Builder, FeatureManager, XmlOutputter, BasicRegistry, User, Group, HttpEndpoint, JdbcDriver, Library, \
    Fileset, Datasource, DB2JCCProp, OracleProp, Application, SecurityRole, ManagedExecutorService


class AdminTask(object):
    
    def __init__(self, liberty_server):
        self._liberty_server = liberty_server
        
        builder = Builder()
        self._server_model = builder.build(self._liberty_server.get_server_xml())
    
    def save(self):
        outputter = XmlOutputter()
        with open(self._liberty_server.get_server_xml(), 'w') as f:
            f.write(outputter.output(self._server_model))
    
    def add_features(self, features):
        feature_manager = self._server_model.find(FeatureManager)
        if feature_manager is None:
            feature_manager = FeatureManager()
            self._server_model.add(feature_manager)
            
        feature_manager.add_features(features)
    
    def modify_http_endpoints(self, http_port, https_port):
        http_endpoints = self._server_model.find(HttpEndpoint)
        if http_endpoints is None:
            http_endpoints = HttpEndpoint()
            http_endpoints.id = 'defaultHttpEndpoint'
            http_endpoints.host = '*'
            self._server_model.add(http_endpoints)
            
        http_endpoints.http_port = http_port
        http_endpoints.https_port = https_port
    
    def create_basic_registry(self, id_, realm_name):
        basic_register = self._server_model.find(BasicRegistry)
        if basic_register is None:
            basic_registry = BasicRegistry()
            basic_registry.id = id_
            basic_registry.realm = realm_name
            self._server_model.add(basic_registry)
        
    def create_user(self, username, password):
        basic_register = self._server_model.find(BasicRegistry)
        members = []
        for member in basic_register.find_all(User):
            members.append(member.name)

        if username not in members:
            user = User()
            user.name = username
            user.password = password
            basic_register.add(user)
    
    def create_group(self, group_name):
        basic_register = self._server_model.find(BasicRegistry)
        groups = []
        for group in basic_register.find_all(Group):
            groups.append(group.name)
        
        if group_name not in groups:
            new_group = Group()
            new_group.name = group_name
            basic_register.add(new_group)
    
    def add_user_to_group(self, user, group_name):
        basic_register = self._server_model.find(BasicRegistry)
        if basic_register is None:
            raise LibertyAdminTaskException('Can not find basicRegistry element in server.xml.')
    
        groups = basic_register.find_all(Group)
        for group in groups:
            if group.name == group_name:
                group.add_members([user])
    
    def create_jdbc_driver(self, jdbc_driver_id, driver_path):
        jdbc_driver = JdbcDriver()
        jdbc_driver.id = jdbc_driver_id
        jdbc_driver.library_ref = 'jdbcLib'
        self._server_model.add(jdbc_driver)
        
        lib = Library()
        lib.id = 'jdbcLib'
        jdbc_driver.add(lib)
        
        fileset = Fileset()
        fileset.dir = driver_path
        fileset.includes = '*.jar'
        lib.add(fileset)
    
    def create_db2_datasource(self, jndi_name, jdbc_driver_id, db_name, db_user, db_pwd, db_host, db_port, schema=None, isolation_level=None):
        datasource = self._create_datasource(jndi_name, jdbc_driver_id, isolation_level)
        
        prop = DB2JCCProp()
        prop.database_name = db_name
        prop.db_user = db_user
        prop.db_password = db_pwd
        prop.server_name = db_host
        prop.db_port = db_port
        if schema:
            prop.schema = schema
        
        datasource.add(prop)
    
    def create_oracle_datasource(self, jndi_name, jdbc_driver_id, db_name, db_user, db_pwd, db_host, db_port, isolation_level=None):
        datasource = self._create_datasource(jndi_name, jdbc_driver_id, isolation_level)
        
        prop = OracleProp()
        prop.database_name = db_name
        prop.db_user = db_user
        prop.db_password = db_pwd
        prop.server_name = db_host
        prop.db_port = db_port
        
        datasource.add(prop)
    
    def _create_datasource(self, jndi_name, jdbc_driver_id, isolation_level=None):
        datasource = Datasource()
        datasource.id = jndi_name
        datasource.jndi = jndi_name
        datasource.jdbc_driver_ref = jdbc_driver_id
        if isolation_level:
            datasource.isolation_level = isolation_level
        self._server_model.add(datasource)
        
        return datasource
    
    def install_war(self, name, war_path, mapping_roles):
        if not os.path.exists(war_path):
            raise LibertyAdminTaskException('Can not find war application {0} in {1}.'.format(name, war_path))
        
        shutil.copy(war_path, self._liberty_server.get_apps_dir())
        app = Application()
        app.id = name
        app.name = name
        app.type = 'war'
        app.location = '${server.config.dir}/apps/' + name + '.war'
        self._server_model.add(app)
    
        for role in mapping_roles:
            security_role = SecurityRole()
            security_role.name = role
            security_role.add_groups([role])
            app.add_security_role(security_role)
            
    def add_managed_executor_service(self, jndi_name):
        model = ManagedExecutorService()
        model.jndi_name = jndi_name
        self._server_model.add(model) 
        
    def get_ports(self):
        http_endpoints = self._server_model.find(HttpEndpoint)
        return (http_endpoints.http_port, http_endpoints.https_port)
    
    
class LibertyAdminTaskException (Exception):
    pass