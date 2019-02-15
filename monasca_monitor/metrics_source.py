import datetime
import os
import socket
import time

from keystoneauth1 import identity, session
from keystoneclient import discover
from monascaclient import client


_HOSTNAME = socket.gethostname()


class MetricSource():

    def __init__(self):
        self.sess = MetricSource._get_keystone_session()
        self.monasca_client = MetricSource._get_monasca_client(self.sess)

    @staticmethod
    def _get_keystone_session(keystone_timeout=10,
                              ca_file=None,
                              insecure=True):
        auth = identity.Password(
            auth_url=os.environ.get('OS_AUTH_URL'),
            username=os.environ.get('OS_USERNAME'),
            password=os.environ.get('OS_PASSWORD'),
            user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME'),
            project_id=os.environ.get('OS_PROJECT_ID'),
            project_name=os.environ.get('OS_PROJECT_NAME'),
            project_domain_id=os.environ.get('OS_USER_DOMAIN_ID'),
            project_domain_name=os.environ.get('OS_USER_DOMAIN_NAME'),
            reauthenticate=True
        )
        return session.Session(auth=auth,
                               app_name='monascamonitor',
                               app_version='0.1',
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
            interface='internal',
            region_name='RegionOne')

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
                {'timestamp': time.time() * 1000,
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


if __name__ == '__main__':
    metricsource = MetricSource()
    while True:
        metricsource.send_metric()
        time.sleep(1)
