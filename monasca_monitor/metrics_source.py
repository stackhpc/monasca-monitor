# Copyright (c) 2019 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import socket
import sys
import time

from keystoneauth1 import loading, session
from keystoneclient import discover
from monascaclient import client
from oslo_config import cfg

_APP_NAME = 'monasca-monitor'
_CFG_AUTH_SECTION = 'keystone_auth'
_HOSTNAME = socket.gethostname()

monasca_client = cfg.OptGroup(name='monasca_client')
monasca_client_opts = [
    cfg.StrOpt("endpoint_type", default="publicURL"),
    cfg.StrOpt("region_name", default="RegionOne"),
]

CONF = cfg.CONF
CONF.register_group(monasca_client)
CONF.register_opts(monasca_client_opts, group=monasca_client)


class MetricSource():

    def __init__(self):
        CONF(sys.argv[1:],
             project=_APP_NAME)
        loading.register_auth_conf_options(CONF, _CFG_AUTH_SECTION)

        self.sess = self._get_keystone_session()
        self.monasca_client = MetricSource._get_monasca_client(self.sess)

    def _get_keystone_session(self,
                              keystone_timeout=10,
                              ca_file=None,
                              insecure=True):
        auth = loading.load_auth_from_conf_options(CONF,
                                                   _CFG_AUTH_SECTION)
        return session.Session(auth=auth,
                               app_name=_APP_NAME,
                               timeout=keystone_timeout,
                               verify=not insecure,
                               cert=ca_file)

    @staticmethod
    def _get_monasca_client(sess):
        disc = discover.Discover(session=sess)
        ks = disc.create_client(sess=sess)
        ks.auth_ref = sess.auth.get_auth_ref(session=sess)

        catalog = ks.auth_ref.service_catalog
        endpoint = catalog.url_for(
            service_type='monitoring',
            interface=CONF.monasca_client.interface,
            region_name=CONF.monasca_client.region_name)

        return client.Client(
            api_version='2_0',
            endpoint=endpoint,
            session=sess
        )

    @staticmethod
    def _get_heartbeat_value():
        now = datetime.datetime.now()
        return 1 if (now.minute % 2 == 0) else 0

    @staticmethod
    def _send_heartbeat_metric(client):
        kwargs = {
            'jsonbody': [
                {'timestamp': int(time.time() * 1000),
                 'value_meta': None,
                 'dimensions': {'hostname': _HOSTNAME},
                 'value': MetricSource._get_heartbeat_value(),
                 'name': 'monascamonitor.heartbeat'}
            ]
        }
        print('Sending metric: {}'.format(kwargs))
        client.metrics.create(**kwargs)

    def send_metric(self):
        MetricSource._send_heartbeat_metric(self.monasca_client)


def main():
    metricsource = MetricSource()
    while True:
        metricsource.send_metric()
        time.sleep(1)


if __name__ == '__main__':
    sys.exit(main())
