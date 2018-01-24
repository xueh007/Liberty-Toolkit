#
# IBM Confidential
# OCO Source Materials
# 5725-B69
# Copyright IBM Corp. 2015
# The source code for this program is not published or otherwise
# divested of its trade secrets, irrespective of what has
# been deposited with the U.S Copyright Office.
#

import copy
import inspect
import string
import sys
from xml.etree import ElementTree


class Builder():

    def build(self, xml_file):
        root = ElementTree.parse(xml_file).getroot()
        self._element_mapping = self._get_mapping()
        
        return self._build_tree(root)
    
    def _build_tree(self, element):
        tag = element.tag
        model = self._element_mapping.get(tag, lambda: None)()
        model.attributes = element.attrib
        model.value = element.text
        for child in element.getchildren():
            model.add(self._build_tree(child))
         
        return model

    def _get_mapping(self):
        element_mapping = {}
        clsmembers = inspect.getmembers(sys.modules[self.__module__], lambda member: inspect.isclass(member))
        for _, clz in clsmembers:
            if ElementModel in inspect.getmro(clz):
                element_mapping[clz.ELEMENT_NAME] = clz
                
        return element_mapping
    

class XmlOutputter(object):
    
    def __init__(self):
        self._indent = 0
        self._content = []
    
    def _add_indent(self, num=4):
        self._indent += num
        
    def _remove_indent(self, num=4):
        if self._indent - num >= 0:
            self._indent -= num
    
    def _println(self, s):
        self._content.append(' ' * self._indent + s)
    
    def _get_content(self):
        return string.join(self._content, '\n')
            
    def _output_element(self, model):
        if model.has_children():
            self._println('<{0}{1}>'.format(model.get_element_name(), self._output_attributes(model.attributes)))
            self._add_indent()
            for child in model.children():
                self._output_element(child)
            self._remove_indent()
            self._println('</{0}>'.format(model.get_element_name()))
            
        elif model.value:
            self._println('<{0}{1}>{2}</{0}>'.format(model.get_element_name(), self._output_attributes(model.attributes), model.value))

        else:
            self._println('<{0}{1} />'.format(model.get_element_name(), self._output_attributes(model.attributes)))
            
    def _output_attributes(self, attrib):
        attrs_dict = copy.copy(attrib)
        result = '' 
        
        if attrs_dict.has_key('id'):
            result += ' id="{0}"'.format(attrs_dict.pop('id'))
    
        for (k, v) in sorted(attrs_dict.iteritems(), key=lambda d:d[0]):
            result += ' {0}="{1}"'.format(k, v)
        
        return result
    
    def output(self, model):
        self._output_element(model)
        return self._get_content()
    

class ElementModel(object):
    
    ELEMENT_NAME = ''
    ID_KEY = 'id'
    
    def __init__(self):
        self._children = []
        
        self.attributes = {}
        self.value = None
    
    @property
    def id(self):
        return self.get(HttpEndpoint.ID_KEY)
    
    @id.setter
    def id(self, id_):
        self.set(HttpEndpoint.ID_KEY, id_)
    
    def add(self, model):
        self._children.append(model)
    
    def children(self):
        return self._children
    
    def has_children(self):
        if len(self._children) > 0:
            return True
        return False
    
    def remove(self, model):
        if model in self._children:
            self._children.remove(model)
            
    def get(self, key):
        if self.attributes.has_key(key):
            return self.attributes[key]
    
    def set(self, key, value):
        self.attributes[key] = value
        
    def get_element_name(self):
        return self.__class__.ELEMENT_NAME
    
    def find(self, model_clazz):
        for child in self.children():
            if child.__class__ == model_clazz:
                return child
            
    def find_all(self, model_clazz):
        result = []
        for child in self.children():
            if child.__class__ == model_clazz:
                result.append(child)
                
        return result
    

class ServerModel(ElementModel):
    
    ELEMENT_NAME = 'server'
    DESC_KEY = 'description'
    
    @property
    def desc(self):
        return self.get(ServerModel.DESC_KEY)
    
    @desc.setter
    def desc(self, desc):
        self.set(ServerModel.DESC_KEY, desc)


class FeatureManager(ElementModel):
    
    ELEMENT_NAME = 'featureManager'
    
    def list_features(self):
        result = []
        for child in self.children():
            result.append(child.value)
            
        return result
    
    def add_features(self, features):
        for name in features:
            if name not in self.list_features():
                feature = Feature()
                feature.value = name
                self.add(feature)
            
    
class Feature(ElementModel):
    
    ELEMENT_NAME = 'feature'


class HttpEndpoint(ElementModel):
    
    ELEMENT_NAME = 'httpEndpoint'
    
    HOST_KEY = 'host'
    HTTP_PORT_KEY = 'httpPort'
    HTTPS_PORT_KEY = 'httpsPort'
        
    @property
    def host(self):
        return self.get(HttpEndpoint.HOST_KEY)
    
    @host.setter
    def host(self, host):
        self.set(HttpEndpoint.HOST_KEY, host)
        
    @property
    def http_port(self):
        return self.get(HttpEndpoint.HTTP_PORT_KEY)
    
    @http_port.setter
    def http_port(self, port):
        self.set(HttpEndpoint.HTTP_PORT_KEY, port)
        
    @property
    def https_port(self):
        return self.get(HttpEndpoint.HTTPS_PORT_KEY)
    
    @https_port.setter
    def https_port(self, port):
        self.set(HttpEndpoint.HTTPS_PORT_KEY, port)
        
    
class BasicRegistry(ElementModel):
    
    ELEMENT_NAME = 'basicRegistry'
    REALM_KEY = 'realm'
    
    @property
    def realm(self):
        return self.get(BasicRegistry.REALM_KEY)
    
    @realm.setter
    def realm(self, realm_name):
        self.set(BasicRegistry.REALM_KEY, realm_name)
    
        
class User(ElementModel):
    
    ELEMENT_NAME = 'user'
    NAME_KEY = 'name'
    PASSWORD_KEY = 'password'
    
    @property
    def name(self):
        return self.get(User.NAME_KEY)
    
    @name.setter
    def name(self, name):
        self.set(User.NAME_KEY, name)
        
    @property
    def password(self):
        return self.get(User.PASSWORD_KEY)
    
    @password.setter
    def password(self, pwd):
        self.set(User.PASSWORD_KEY, pwd)

    
class Group(ElementModel):
    
    ELEMENT_NAME = 'group'
    NAME_KEY = 'name'
    
    @property
    def name(self):
        return self.get(Group.NAME_KEY)
    
    @name.setter
    def name(self, name):
        self.set(Group.NAME_KEY, name)
        
    def list_members(self):
        result = []
        for child in self.children():
            result.append(child.name)
        
        return result
        
    def add_members(self, members):
        for name in members:
            if name not in self.list_members():
                member = Member()
                member.name = name
                self.add(member)


class Member(ElementModel):
    
    ELEMENT_NAME = 'member'
    NAME_KEY = 'name'
    
    @property
    def name(self):
        return self.get(Member.NAME_KEY)
    
    @name.setter
    def name(self, name):
        self.set(Member.NAME_KEY, name)
        
        
class Library(ElementModel):
    
    ELEMENT_NAME = 'library'
    

class Fileset(ElementModel):
    
    ELEMENT_NAME = 'fileset'
    DIR_KEY = 'dir'
    INCLUDES_KEY = 'includes'
    
    @property
    def dir(self):
        return self.get(Fileset.DIR_KEY)
    
    @dir.setter
    def dir(self, dir_):
        self.set(Fileset.DIR_KEY, dir_)
        
    @property
    def includes(self):
        return self.get(Fileset.INCLUDES_KEY)
    
    @includes.setter
    def includes(self, includes):
        self.set(Fileset.INCLUDES_KEY, includes)
        
        
class JdbcDriver(ElementModel):
    
    ELEMENT_NAME = 'jdbcDriver'
    LIBRARY_REF_KEY = 'libraryRef'
    
    @property
    def library_ref(self):
        return self.get(JdbcDriver.LIBRARY_REF_KEY)
    
    @library_ref.setter
    def library_ref(self, ref):
        self.set(JdbcDriver.LIBRARY_REF_KEY, ref)
        
        
class Datasource(ElementModel):
    
    ELEMENT_NAME = 'dataSource'
    JNDI_KEY = 'jndiName'
    JDBC_DRIVER_REF_KEY = 'jdbcDriverRef'
    ISOLATION_LEVEL_KEY = 'isolationLevel'
    
    @property
    def jndi(self):
        return self.get(Datasource.JNDI_KEY)
    
    @jndi.setter
    def jndi(self, jndi_name):
        self.set(Datasource.JNDI_KEY, jndi_name)
        
    @property
    def jdbc_driver_ref(self):
        return self.get(Datasource.JDBC_DRIVER_REF_KEY)
    
    @jdbc_driver_ref.setter
    def jdbc_driver_ref(self, ref):
        self.set(Datasource.JDBC_DRIVER_REF_KEY, ref)
        
    @property
    def isolation_level(self):
        return self.get(Datasource.ISOLATION_LEVEL_KEY)
    
    @isolation_level.setter
    def isolation_level(self, value):
        self.set(Datasource.ISOLATION_LEVEL_KEY, value)
    
    
class DatasourceProp(ElementModel):    
    
    ELEMENT_NAME = 'properties'
    DATABASE_NAME_KEY = 'databaseName'
    SERVER_NAME_KEY = 'serverName'
    PORT_KEY = 'portNumber'
    USER_KEY = 'user'
    PASSWORD_KEY = 'password'

    @property
    def database_name(self):
        return self.get(DatasourceProp.DATABASE_NAME_KEY)
    
    @database_name.setter
    def database_name(self, name):
        self.set(DatasourceProp.DATABASE_NAME_KEY, name)
    
    @property
    def server_name(self):
        return self.get(DatasourceProp.SERVER_NAME_KEY)
    
    @server_name.setter
    def server_name(self, name):
        self.set(DatasourceProp.SERVER_NAME_KEY, name)
        
    @property
    def db_port(self):
        return self.get(DatasourceProp.PORT_KEY)
    
    @db_port.setter
    def db_port(self, port_num):
        self.set(DatasourceProp.PORT_KEY, port_num)
        
    @property
    def db_user(self):
        return self.get(DatasourceProp.USER_KEY)
    
    @db_user.setter
    def db_user(self, name):
        self.set(DatasourceProp.USER_KEY, name)
        
    @property
    def db_password(self):
        return self.get(DatasourceProp.PASSWORD_KEY)
    
    @db_password.setter
    def db_password(self, pwd):
        self.set(DatasourceProp.PASSWORD_KEY, pwd)
        
        
class DB2JCCProp(DatasourceProp):
    
    ELEMENT_NAME = 'properties.db2.jcc'
    SCHEMA_KEY = 'currentSchema'
        
    @property
    def schema(self):
        return self.get(DB2JCCProp.SCHEMA_KEY)
    
    @schema.setter
    def schema(self, name):
        self.set(DB2JCCProp.SCHEMA_KEY, name)
    
    
class OracleProp(DatasourceProp):
    
    ELEMENT_NAME = 'properties.oracle'


class Application(ElementModel):
    
    ELEMENT_NAME = 'application'
    NAME_KEY = 'name'
    TYPE_KEY = 'type'
    LOCATION_KEY = 'location'
    
    @property
    def name(self):
        return self.get(Application.NAME_KEY) 
    
    @name.setter
    def name(self, app_name):
        self.set(Application.NAME_KEY, app_name)
        
    @property
    def type(self):
        return self.get(Application.TYPE_KEY) 
    
    @type.setter
    def type(self, app_type):
        self.set(Application.TYPE_KEY, app_type)
        
    @property
    def location(self):
        return self.get(Application.LOCATION_KEY) 
    
    @location.setter
    def location(self, app_location):
        self.set(Application.LOCATION_KEY, app_location)
    
    def add_security_role(self, role):
        app_bnd = self.find(ApplicationBnd)
        if app_bnd is None:
            app_bnd = ApplicationBnd()
            self.add(app_bnd)
            
        app_bnd.add(role) 
    
    
class ApplicationBnd(ElementModel):
    
    ELEMENT_NAME = 'application-bnd'
    
    
class SecurityRole(ElementModel):
    
    ELEMENT_NAME = 'security-role'
    NAME_KEY = 'name'
    
    @property
    def name(self):
        return self.get(SecurityRole.NAME_KEY)
    
    @name.setter
    def name(self, value):
        self.set(SecurityRole.NAME_KEY, value)
        
    def add_groups(self, groups):
        for name in groups:
            group = Group()
            group.name = name
            self.add(group)
            
    def add_users(self, users):
        for name in users:
            user = User()
            user.name = name
            self.add(user)
            

class SSL(ElementModel):
    
    ELEMENT_NAME = 'ssl'
    KEY_STORE_REF_KEY = 'keyStoreRef'
    SSL_PROTOCOL_KEY = 'sslProtocol'              

    @property
    def key_store_ref(self):
        return self.get(SSL.KEY_STORE_REF_KEY)
    
    @key_store_ref.setter
    def key_store_ref(self, value):
        self.set(SSL.KEY_STORE_REF_KEY, value)
        
    @property
    def ssl_protocol(self):
        return self.get(SSL.SSL_PROTOCOL_KEY)
    
    @ssl_protocol.setter
    def ssl_protocol(self, value):
        self.set(SSL.SSL_PROTOCOL_KEY, value)
        
    
class KeyStore(ElementModel):
    
    ELEMENT_NAME = 'keyStore'
    PASSWORD_KEY = 'password'
    
    @property
    def password(self):
        return self.get(KeyStore.PASSWORD_KEY)
    
    @password.setter
    def password(self, pwd):
        self.set(KeyStore.PASSWORD_KEY, pwd)
        
        
class ManagedExecutorService(ElementModel):
    
    ELEMENT_NAME = 'managedExecutorService'
    JNDI_NAME_KEY = 'jndiName'
    
    @property
    def jndi_name(self):
        return self.get(ManagedExecutorService.JNDI_NAME_KEY)
    
    @jndi_name.setter
    def jndi_name(self, name):
        self.set(ManagedExecutorService.JNDI_NAME_KEY, name)