# Authors:
#     Endi S. Dewata <edewata@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (C) 2018 Red Hat, Inc.
# All rights reserved.
#

from __future__ import absolute_import
from __future__ import print_function
import getopt
import logging
import sys

import pki.cli
import pki.nssdb
import pki.server
import pki.server.cli.nuxwdog


class HTTPCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPCLI, self).__init__(
            'http', 'HTTP management commands')

        self.add_module(HTTPConnectorCLI())


class HTTPConnectorCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorCLI, self).__init__(
            'connector', 'HTTP connector management commands')

        self.add_module(HTTPConnectorAddCLI())
        self.add_module(HTTPConnectorDeleteCLI())
        self.add_module(HTTPConnectorFindCLI())
        self.add_module(HTTPConnectorModCLI())
        self.add_module(HTTPConnectorShowCLI())

        self.add_module(SSLHostCLI())
        self.add_module(SSLCertCLI())

    @staticmethod
    def print_param(element, name, label):

        value = element.get(name)
        if value:
            print('  %s: %s' % (label, value))

    @staticmethod
    def set_param(element, name, value):

        if value is None:
            return

        if value:  # non-empty
            element.set(name, value)

        else:
            element.attrib.pop(name)

    @staticmethod
    def print_connector(connector):

        HTTPConnectorCLI.print_param(connector, 'name', 'Connector ID')
        HTTPConnectorCLI.print_param(connector, 'port', 'Port')
        HTTPConnectorCLI.print_param(connector, 'protocol', 'Protocol')
        HTTPConnectorCLI.print_param(connector, 'scheme', 'Scheme')
        HTTPConnectorCLI.print_param(connector, 'secure', 'Secure')
        HTTPConnectorCLI.print_param(connector, 'SSLEnabled', 'SSL Enabled')

        HTTPConnectorCLI.print_param(connector, 'sslImplementationName', 'SSL Implementation')

        HTTPConnectorCLI.print_param(connector, 'sslVersionRangeStream',
                                     'SSL Version Range Stream')
        HTTPConnectorCLI.print_param(connector, 'sslVersionRangeDatagram',
                                     'SSL Version Range Datagram')
        HTTPConnectorCLI.print_param(connector, 'sslRangeCiphers', 'SSL Range Ciphers')

        HTTPConnectorCLI.print_param(connector, 'certdbDir', 'NSS Database Directory')
        HTTPConnectorCLI.print_param(connector, 'passwordClass', 'NSS Password Class')
        HTTPConnectorCLI.print_param(connector, 'passwordFile', 'NSS Password File')
        HTTPConnectorCLI.print_param(connector, 'serverCertNickFile', 'Server Cert Nickname File')

        HTTPConnectorCLI.print_param(connector, 'keystoreFile', 'Keystore File')
        HTTPConnectorCLI.print_param(connector, 'keystorePassFile', 'Keystore Password File')

        HTTPConnectorCLI.print_param(connector, 'trustManagerClassName', 'Trust Manager')


class HTTPConnectorAddCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorAddCLI, self).__init__('add', 'Add connector')

    def print_help(self):
        print('Usage: pki-server http-connector-add [OPTIONS] <connector ID>')
        print()
        print('  -i, --instance <instance ID>              Instance ID (default: pki-tomcat).')
        print('      --port <port>                         Port number.')
        print('      --protocol <protocol>                 Protocol.')
        print('      --scheme <scheme>                     Scheme.')
        print('      --secure <true|false>                 Secure.')
        print('      --sslEnabled <true|false>             SSL enabled.')
        print('  -v, --verbose                             Run in verbose mode.')
        print('      --debug                               Run in debug mode.')
        print('      --help                                Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'port=', 'protocol=', 'scheme=', 'secure=', 'sslEnabled=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'
        port = None
        protocol = None
        scheme = None
        secure = None
        sslEnabled = None

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o == '--port':
                port = a

            elif o == '--protocol':
                protocol = a

            elif o == '--scheme':
                scheme = a

            elif o == '--secure':
                secure = a

            elif o == '--sslEnabled':
                sslEnabled = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) != 1:
            print('ERROR: Missing connector ID')
            self.print_help()
            sys.exit(1)

        if port is None:
            print('ERROR: Missing port number')
            self.print_help()
            sys.exit(1)

        name = args[0]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        if name in connectors:
            print('ERROR: Connector already exists: %s' % name)
            sys.exit(1)

        connector = server_config.create_connector(name)

        HTTPConnectorCLI.set_param(connector, 'port', port)
        HTTPConnectorCLI.set_param(connector, 'protocol', protocol)
        HTTPConnectorCLI.set_param(connector, 'scheme', scheme)
        HTTPConnectorCLI.set_param(connector, 'secure', secure)
        HTTPConnectorCLI.set_param(connector, 'SSLEnabled', sslEnabled)

        server_config.save()

        HTTPConnectorCLI.print_connector(connector)


class HTTPConnectorDeleteCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorDeleteCLI, self).__init__('del', 'Delete connector')

    def print_help(self):
        print('Usage: pki-server http-connector-del [OPTIONS] <connector ID>')
        print()
        print('  -i, --instance <instance ID>    Instance ID (default: pki-tomcat).')
        print('  -v, --verbose                   Run in verbose mode.')
        print('      --debug                     Run in debug mode.')
        print('      --help                      Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) != 1:
            print('ERROR: Missing connector ID')
            self.print_help()
            sys.exit(1)

        name = args[0]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: Invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        server_config.remove_connector(name)
        server_config.save()


class HTTPConnectorFindCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorFindCLI, self).__init__('find', 'Find connectors')

    def print_help(self):
        print('Usage: pki-server http-connector-find [OPTIONS]')
        print()
        print('  -i, --instance <instance ID>    Instance ID (default: pki-tomcat).')
        print('  -v, --verbose                   Run in verbose mode.')
        print('      --debug                     Run in debug mode.')
        print('      --help                      Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, _ = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: Invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        self.print_message('%s entries matched' % len(connectors))

        first = True
        for name in connectors:

            if first:
                first = False
            else:
                print()

            connector = connectors[name]
            HTTPConnectorCLI.print_connector(connector)


class HTTPConnectorShowCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorShowCLI, self).__init__('show', 'Show connector')

    def print_help(self):
        print('Usage: pki-server http-connector-show [OPTIONS] <connector ID>')
        print()
        print('  -i, --instance <instance ID>    Instance ID (default: pki-tomcat).')
        print('  -v, --verbose                   Run in verbose mode.')
        print('      --debug                     Run in debug mode.')
        print('      --help                      Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) != 1:
            print('ERROR: Missing connector ID')
            self.print_help()
            sys.exit(1)

        name = args[0]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: Invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        if name not in connectors:
            print('ERROR: Connector not found: %s' % name)
            sys.exit(1)

        connector = connectors[name]
        HTTPConnectorCLI.print_connector(connector)


class HTTPConnectorModCLI(pki.cli.CLI):

    def __init__(self):
        super(HTTPConnectorModCLI, self).__init__('mod', 'Modify connector')

    def print_help(self):
        print('Usage: pki-server http-connector-mod [OPTIONS] <connector ID>')
        print()
        print('  -i, --instance <instance ID>              Instance ID (default: pki-tomcat).')
        print('      --type <type>                         Connector type: JSS (default), JSSE.')
        print('      --nss-database-dir <dir>              NSS database directory.')
        print('      --nss-password-file <file>            NSS password file.')
        print('      --keystore-file <file>                Key store file.')
        print('      --keystore-password-file <file>       Key store password file.')
        print('      --server-cert-nickname-file <file>    Server certificate nickname file.')
        print('  -v, --verbose                             Run in verbose mode.')
        print('      --debug                               Run in debug mode.')
        print('      --help                                Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=', 'type=',
                'nss-database-dir=', 'nss-password-file=',
                'keystore-file=', 'keystore-password-file=',
                'server-cert-nickname-file=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'
        connector_type = 'JSS'
        nss_database_dir = None
        nss_password_file = None
        keystore_file = None
        keystore_password_file = None
        server_cert_nickname_file = None

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o == '--type':
                connector_type = a

            elif o == '--nss-database-dir':
                nss_database_dir = a

            elif o == '--nss-password-file':
                nss_password_file = a

            elif o == '--keystore-file':
                keystore_file = a

            elif o == '--keystore-password-file':
                keystore_password_file = a

            elif o == '--server-cert-nickname-file':
                server_cert_nickname_file = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) != 1:
            print('ERROR: Missing connector ID')
            self.print_help()
            sys.exit(1)

        name = args[0]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        if name not in connectors:
            print('ERROR: Connector not found: %s' % name)
            sys.exit(1)

        connector = connectors[name]

        HTTPConnectorCLI.set_param(connector, 'certdbDir', nss_database_dir)
        HTTPConnectorCLI.set_param(connector, 'passwordClass',
                                   'org.apache.tomcat.util.net.jss.PlainPasswordFile')
        HTTPConnectorCLI.set_param(connector, 'passwordFile', nss_password_file)
        HTTPConnectorCLI.set_param(connector, 'serverCertNickFile', server_cert_nickname_file)

        if connector_type == 'JSS':

            connector.set(
                'protocol',
                'org.apache.coyote.http11.Http11Protocol')

            connector.set(
                'sslImplementationName',
                'org.apache.tomcat.util.net.jss.JSSImplementation')

            connector.attrib.pop('keystoreType', None)
            connector.attrib.pop('keystoreFile', None)
            connector.attrib.pop('keystorePassFile', None)
            connector.attrib.pop('keyAlias', None)

            connector.attrib.pop('trustManagerClassName', None)

        elif connector_type == 'JSSE':

            connector.set(
                'protocol',
                'org.dogtagpki.tomcat.Http11NioProtocol')

            connector.attrib.pop('sslImplementationName', None)

            HTTPConnectorCLI.set_param(connector, 'keystoreType', 'pkcs12')
            HTTPConnectorCLI.set_param(connector, 'keystoreFile', keystore_file)
            HTTPConnectorCLI.set_param(connector, 'keystorePassFile', keystore_password_file)
            HTTPConnectorCLI.set_param(connector, 'keyAlias', 'sslserver')

            HTTPConnectorCLI.set_param(connector, 'trustManagerClassName',
                                       'org.dogtagpki.tomcat.PKITrustManager')

        else:
            raise Exception('Invalid connector type: %s' % connector_type)

        server_config.save()

        HTTPConnectorCLI.print_connector(connector)


class SSLHostCLI(pki.cli.CLI):

    def __init__(self):
        super(SSLHostCLI, self).__init__(
            'host', 'SSL host configuration management commands')

        self.add_module(SSLHostFindLI())

    @staticmethod
    def print_sslhost(sslhost):

        hostName = sslhost.get('hostName', '_default_')
        print('  Hostname: %s' % hostName)

        HTTPConnectorCLI.print_param(
            sslhost, 'sslProtocol', 'SSL Protocol')
        HTTPConnectorCLI.print_param(
            sslhost, 'certificateVerification', 'Certificate Verification')
        HTTPConnectorCLI.print_param(
            sslhost, 'trustManagerClassName', 'Trust Manager')


class SSLHostFindLI(pki.cli.CLI):

    def __init__(self):
        super(SSLHostFindLI, self).__init__('find', 'Find SSL host configurations')

    def print_help(self):
        print('Usage: pki-server http-connector-host-find [OPTIONS] <connector ID>')
        print()
        print('  -i, --instance <instance ID>    Instance ID (default: pki-tomcat).')
        print('  -v, --verbose                   Run in verbose mode.')
        print('      --debug                     Run in debug mode.')
        print('      --help                      Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) < 1:
            raise Exception('Missing connector ID')

        connector_name = args[0]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: Invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        if connector_name not in connectors:
            raise Exception('Invalid connector ID: %s' % connector_name)

        connector = connectors[connector_name]

        sslhosts = list(connector.iter('SSLHostConfig'))
        self.print_message('%s entries matched' % len(sslhosts))

        first = True
        for sslhost in sslhosts:

            if first:
                first = False
            else:
                print()

            SSLHostCLI.print_sslhost(sslhost)


class SSLCertCLI(pki.cli.CLI):

    def __init__(self):
        super(SSLCertCLI, self).__init__(
            'cert', 'SSL certificate configuration management commands')

        self.add_module(SSLCertFindLI())

    @staticmethod
    def print_sslcert(sslcert):

        certType = sslcert.get('type', 'UNDEFINED')
        print('  Type: %s' % certType)

        HTTPConnectorCLI.print_param(
            sslcert, 'certificateFile', 'Certificate File')
        HTTPConnectorCLI.print_param(
            sslcert, 'certificateKeyFile', 'Key File')
        HTTPConnectorCLI.print_param(
            sslcert, 'certificateKeyAlias', 'Key Alias')
        HTTPConnectorCLI.print_param(
            sslcert, 'certificateKeystoreType', 'Keystore Type')
        HTTPConnectorCLI.print_param(
            sslcert, 'certificateKeystoreProvider', 'Keystore Provider')
        HTTPConnectorCLI.print_param(
            sslcert, 'certificateKeystoreFile', 'Keystore File')


class SSLCertFindLI(pki.cli.CLI):

    def __init__(self):
        super(SSLCertFindLI, self).__init__('find', 'Find SSL certificate configurations')

    def print_help(self):
        print('Usage: pki-server http-connector-cert-find '
              '[OPTIONS] <connector ID> <hostname>')
        print()
        print('  -i, --instance <instance ID>    Instance ID (default: pki-tomcat).')
        print('  -v, --verbose                   Run in verbose mode.')
        print('      --debug                     Run in debug mode.')
        print('      --help                      Show help message.')
        print()

    def execute(self, argv):

        logging.basicConfig(format='%(levelname)s: %(message)s')

        try:
            opts, args = getopt.gnu_getopt(argv, 'i:v', [
                'instance=',
                'verbose', 'debug', 'help'])

        except getopt.GetoptError as e:
            print('ERROR: %s' % e)
            self.print_help()
            sys.exit(1)

        instance_name = 'pki-tomcat'

        for o, a in opts:
            if o in ('-i', '--instance'):
                instance_name = a

            elif o in ('-v', '--verbose'):
                logging.getLogger().setLevel(logging.INFO)

            elif o == '--debug':
                logging.getLogger().setLevel(logging.DEBUG)

            elif o == '--help':
                self.print_help()
                sys.exit()

            else:
                print('ERROR: Unknown option: %s' % o)
                self.print_help()
                sys.exit(1)

        if len(args) < 1:
            raise Exception('Missing connector ID')

        connector_name = args[0]

        if len(args) < 2:
            raise Exception('Missing SSL hostname')

        hostname = args[1]

        instance = pki.server.PKIServerFactory.create(instance_name)

        if not instance.is_valid():
            print('ERROR: Invalid instance: %s' % instance_name)
            sys.exit(1)

        instance.load()

        server_config = instance.get_server_config()
        connectors = server_config.get_connectors()

        if connector_name not in connectors:
            raise Exception('Invalid connector ID: %s' % connector_name)

        connector = connectors[connector_name]

        sslhosts = list(connector.iter('SSLHostConfig'))
        sslhost = None

        logging.debug('SSL Hosts:')
        for s in sslhosts:
            h = s.get('hostName', '_default_')
            logging.debug('- %s', h)
            if h == hostname:
                sslhost = s
                break

        if sslhost is None:
            raise Exception('Invalid SSL hostname: %s' % hostname)

        sslcerts = list(sslhost.iter('Certificate'))
        self.print_message('%s entries matched' % len(sslcerts))

        first = True
        for sslcert in sslcerts:

            if first:
                first = False
            else:
                print()

            SSLCertCLI.print_sslcert(sslcert)
