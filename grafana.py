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
    resource_isDefault: "{{ False | bool }}"
    state: present

- name: "Remove InfluxDB datasource"
  grafana:
    server_url: "http://localhost:3000/"
    login_user: "admin"
    login_password: "admin"
    resource: "datasource"
    resource_name: "influxdb"
    state: absent

- name: "Add dashboard"
  grafana:
    server_url: "http://localhost:3000/"
    login_user: "admin"
    login_password: "admin"
    resource: "dashboard"
    resource_json_path: "dashboards/my-dashboard.json"
    state: present

- name: "Remove dashboard"
  grafana:
    server_url: "http://localhost:3000/"
    login_user: "admin"
    login_password: "admin"
    resource: "dashboard"
    resource_name: "my-dashboard"
    state: absent

'''

import requests
import os
from pprint import pprint
import json
import httplib

def get_session(server_url, login_user, login_password):
  session = requests.Session()
  login_post = session.post(
    os.path.join(server_url, 'login'),
    data=json.dumps({
      'user': login_user,
      'password': login_password }),
      headers={'content-type': 'application/json'})
  return session

def datasource_create(server_url, session, resource_name, resource_type, resource_url, database, resource_isDefault=False, resource_access='proxy', json_data=None):
  response = session.post(
    os.path.join(server_url, 'api', 'datasources'),
    data=json.dumps({
      "name": resource_name,
      "type": resource_type,
      "url": 'http://%s' % (resource_url),
      "database": database,
      "isDefault": resource_isDefault,
      "access": resource_access,
      "jsonData": json_data}),
      headers={'content-type': 'application/json'})
  return response

def dashboard_create(server_url, session, dashboard_path):
  # read the dashboard data
  with open(dashboard_path) as dashboard_file:
    dashboard_data = json.load(dashboard_file)

  response = session.post(
    os.path.join(server_url, 'api', 'dashboards', "db"),
    data=json.dumps(dashboard_data),
    headers={'content-type': 'application/json'})
  return response

def datasource_retrieve_id(server_url, session, resource_name):
  response = session.get(
    os.path.join(server_url, 'api', 'datasources', 'id', resource_name),
    data=json.dumps({}),
      headers={'content-type': 'application/json'})
  return response

def datasource_update(server_url, session, resource_name, resource_type, resource_url, database, resource_isDefault=False, resource_access='proxy', json_data=None):
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
      "access": resource_access,
      "jsonData": json_data}),
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

def dashboard_delete(server_url, session, resource_name):
  # use the dashboard name in the wanted format
  resource_name = resource_name.replace(" ", "-").lower()

  response = session.delete(
    os.path.join(server_url, 'api', 'dashboards', 'db', resource_name),
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
            resource=dict(required=True, choices=['datasource', 'dashboard']),
            resource_url=dict(required=False),
            resource_db=dict(required=False),
            resource_json_path=dict(required=False),
            resource_json_data=dict(required=False, type='json', default={}),
            resource_name=dict(required=False),
            resource_type=dict(required=False, default='influxdb'),
            resource_isDefault=dict(required=False, type='bool', default=False),
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
    resource_db = module.params['resource_db']
    resource_json_path = module.params['resource_json_path']
    resource_json_data = json.loads(module.params['resource_json_data'])
    resource_name = module.params['resource_name']
    resource_type = module.params['resource_type']
    resource_isDefault = module.params['resource_isDefault']
    state = module.params['state']

    if not server_url:
      server_url = 'http://%s:%u' % (server_hostname, server_port)

    session = get_session(server_url, login_user, login_password)

    if resource == 'datasource':
      if state == 'present':
        resp = datasource_create(server_url, session, resource_name, resource_type, resource_url, resource_db, resource_isDefault, json_data=resource_json_data)
      elif state == 'latest':
        resp = datasource_update(server_url, session, resource_name, resource_type, resource_url, resource_db, resource_isDefault, json_data=resource_json_data)
      elif state == 'absent':
        resp = datasource_delete(server_url, session, resource_name)
    elif resource == 'dashboard':
      if state == 'present' or state == 'latest':
        resp = dashboard_create(server_url, session, resource_json_path)
      elif state == 'absent':
        resp = dashboard_delete(server_url, session, resource_name)

    # if the request succeed
    if resp.status_code >= 200 and resp.status_code < 300:
        module.exit_json(changed=True, msg=str(resp.content))
    # if the request got unproblematic error
    elif (resp.status_code == httplib.NOT_FOUND and state == 'absent') or (resp.status_code == httplib.CONFLICT and state == 'present'):
        module.exit_json(changed=False, msg=str(resp.content))
    # if the request failed
    else:
        module.fail_json(changed=False, msg=str(resp.content), status_code=resp.status_code)

from ansible.module_utils.basic import *
if __name__ == '__main__':
  main()
