#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Salo Shpigelman <SaloShp@gmail.com> (c) 2016
#

DOCUMENTATION = '''
---
'''

EXAMPLES = '''
---

- name: "Add InfluxDB datasource"
  grafana:
    server_url: "http://localhost:3000/"
    login_user: "admin"
    login_password: "admin"
    resource: "datasource"
    resource_url: "localhost:8086"
    resource_name: "influxdb"
    resource_type: "influxdb"
    state: present

- name: "Remove InfluxDB datasource"
  grafana:
    server_url: "http://localhost:3000/"
    login_user: "admin"
    login_password: "admin"
    resource: "datasource"
    resource_name: "influxdb"
    state: absent
'''

import requests
import os
from pprint import pprint
import json

def get_session(server_url, login_user, login_password):
  session = requests.Session()
  login_post = session.post(
    os.path.join(server_url, 'login'),
    data=json.dumps({
      'user': login_user,
      'password': login_password }),
      headers={'content-type': 'application/json'})
  return session

def datasource_create(server_url, session, resource_name, resource_type, resource_url, database, resource_isDefault=False, resource_access='proxy'):
  response = session.post(
    os.path.join(server_url, 'api', 'datasources'),
    data=json.dumps({
      "name": resource_name,
      "type": resource_type,
      "url": 'http://%s' % (resource_url),
      "database": database,
      "isDefault": resource_isDefault,
      "access": resource_access}),
      headers={'content-type': 'application/json'})
  return response

def datasource_retrieve_id(server_url, session, resource_name):
  response = session.get(
    os.path.join(server_url, 'api', 'datasources', 'id', resource_name),
    data=json.dumps({}),
      headers={'content-type': 'application/json'})
  return response

def datasource_update(server_url, session, resource_name, resource_type, resource_url, database, resource_isDefault=False, resource_access='proxy'):
  response = datasource_retrieve_id(server_url, session, resource_name)
  try:
    resource_id = json.loads(response.content)['id']
  except KeyError, e:
    return response

  response = session.put(
    os.path.join(server_url, 'api', 'datasources', str(resource_id)),
    data=json.dumps({
      "name": resource_name,
      "type": resource_type,
      "url": 'http://%s' % (resource_url),
      "database": database,
      "isDefault": resource_isDefault,
      "access": resource_access}),
      headers={'content-type': 'application/json'})
  return response

def datasource_delete(server_url, session, resource_name):
  response = datasource_retrieve_id(server_url, session, resource_name)
  try:
    resource_id = json.loads(response.content)['id']
  except KeyError, e:
    return response

  response = session.delete(
    os.path.join(server_url, 'api', 'datasources', str(resource_id)),
    data=json.dumps({}),
      headers={'content-type': 'application/json'})
  return response

def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=False),
            server_hostname=dict(required=False, default='localhost'),
            server_port=dict(required=False, default=3000),
            login_user=dict(required=True),
            login_password=dict(required=True),
            resource=dict(required=True),
            resource_url=dict(required=False),
            resource_name=dict(required=True),
            resource_type=dict(required=False, default='influxdb'),
            state=dict(default='present', choices=['present', 'latest', 'absent']),
        ),
        supports_check_mode=True
    )

    server_url = module.params['server_url']
    server_hostname = module.params['server_hostname']
    server_port = module.params['server_port']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    resource = module.params['resource']
    resource_url = module.params['resource_url']
    resource_name = module.params['resource_name']
    resource_type = module.params['resource_type']
    state = module.params['state']

    if not server_url:
      server_url = 'http://%s:%u' % (server_hostname, server_port)

    session = get_session(server_url, login_user, login_password)

    if state == 'present':
      if resource == 'datasource':
        resp = datasource_create(server_url, session, resource_name, resource_type, resource_url, 'metrics', True)

        if resp.status_code >= 200 and resp.status_code < 300:
            module.exit_json(changed=True, msg=str(resp.content))
        else:
            module.fail_json(changed=False, msg=str(resp.content), status_code=resp.status_code)

    if state == 'latest':
      if resource == 'datasource':
        resp = datasource_update(server_url, session, resource_name, resource_type, resource_url, 'metrics', True)

        if resp.status_code >= 200 and resp.status_code < 300:
            module.exit_json(changed=True, msg=str(resp.content))
        else:
            module.fail_json(changed=False, msg=str(resp.content), status_code=resp.status_code)

    elif state == 'absent':
      if resource == 'datasource':
        resp = datasource_delete(server_url, session, resource_name)
        if resp.status_code >= 200 and resp.status_code < 300:
            module.exit_json(changed=True, msg=str(resp.content))
        elif resp.status_code == 404:
            module.exit_json(changed=False, msg=str(resp.content))
        else:
            module.fail_json(changed=False, msg=str(resp.content), status_code=resp.status_code)

from ansible.module_utils.basic import *
main()
