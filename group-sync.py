#!/usr/bin/env python

from argparse import ArgumentParser
from ldap3 import *
import yaml
import logging
import logging.config
import sys
from sync_target.sonar import SonarGroups

def filter_build(ldap_objectclass, ldap_filter_include):
    """ generate filter from yaml list """
    ldap_filter = "(&({})(|".format(ldap_objectclass)
    for fil in ldap_filter_include:
        ldap_filter = ldap_filter + "({})".format(fil)
    ldap_filter = ldap_filter + "))"
    logger.info("LDAP filter: {}".format(ldap_filter))
    return ldap_filter

def get_ldap_groups(all_groups):
    """ get LDAP groups as simple list """
    ldap_groups = []
    for record in all_groups:
        if record['type'].lower() == 'searchresentry':
            ldap_record = record['attributes']['cn']
            logger.debug("adding {} to the LDAP groups".format(ldap_record))
            ldap_groups.append(ldap_record)
    return ldap_groups

def ldap_search(ldap_filter):
    """ perform ldap search """
    server = Server(cfg['ldap']['url'], get_info=ALL, port=cfg['ldap']['port'], use_ssl = cfg['ldap']['ssl'])
    # create a connection object, and bind with the DN and password
    try: 
        logger.info("connecting to LDAP server")
        conn = Connection(server, cfg['ldap']['binddn'], cfg['ldap']['bindpassword'], auto_bind=True)
        logger.info("connected to LDAP {}".format(cfg['ldap']['url']))
        # define search parameters
        searchParameters = { 'search_base': cfg['ldap']['searchbase'],
                      'search_filter': ldap_filter,
                      'attributes': 'cn',
                      'paged_size': 2000,
                      'generator': False}
        search_results = conn.extend.standard.paged_search(**searchParameters)
        logger.info("received {} entities".format(len(search_results)))
        return search_results
        
    except core.exceptions.LDAPBindError as e:
        # If the LDAP bind failed for reasons such as authentication failure.
        logging.error('LDAP bind failed: ', e) 

parser = ArgumentParser(
    description=""" Synchronize LDAP/AD groups with Sonar """
)

parser.add_argument('--no-dry',
                    help="Actually create/delete groups in Sonar",
                    dest='nodry',
                    default=False,
                    required=False,
                    action='store_true')

parser.add_argument('-c', '--config',
                    help="Path to YAML configuration file",
                    default='config.yml',
                    dest='configfile',
                    required=False)

parser.add_argument('-l', '--log-config',
                    help="Path to YAML logging configuration file",
                    default='logging.yml',
                    dest='logconfigfile',
                    required=False)

args = parser.parse_args()

with open(args.logconfigfile, 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

cfgfile = args.configfile
with open(cfgfile, 'r') as configfile:
    logger.info("loading configuration file {}".format(cfgfile))
    cfg = yaml.safe_load(configfile)

ldap_filter = filter_build(cfg['ldap']['objectclass'], cfg['ldap']['filter_include'])
all_records = ldap_search(ldap_filter)
ldap_groups = get_ldap_groups(all_records)

s = SonarGroups(cfg)
sonar_groups = s.get_groups()

# create existing LDAP groups in Sonar
sonar_groups_create = set(ldap_groups).difference(set(sonar_groups))
logger.info("create {} groups in Sonar".format(len(sonar_groups_create)))
if args.nodry:
    s.create_groups(sonar_groups_create)

sonar_groups = s.get_groups()

# delete inexistent LDAP groups in Sonar
sonar_groups_delete = set(sonar_groups).difference(set(ldap_groups))
logger.info("delete {} groups in Sonar".format(len(sonar_groups_delete)))
if args.nodry:
    s.delete_groups(list(sonar_groups_delete))
