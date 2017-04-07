# ansible-module-grafana
Grafana Ansible module

This module helps operating Grafana from Ansible

Example:

```
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
```

```bash
#!/bin/bash

apt install grafana-server
```
