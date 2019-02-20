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

import cgi
import sys

from oslo_config import cfg
from prometheus_client import Counter
from prometheus_client.twisted import MetricsResource
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

_APP_NAME = 'monasca-monitor'
_HEARTBEAT = Counter(
    'monasca_monitor_heartbeat',
    'Monasca system level heartbeat')

heartbeat_group = cfg.OptGroup(name='heartbeat')
opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0'),
    cfg.PortOpt('bind_port', default=8000),
]

CONF = cfg.CONF
CONF.register_group(heartbeat_group)
CONF.register_opts(opts, group=heartbeat_group)


class HeartBeatResource(Resource):

    def render_POST(self, request):
        _HEARTBEAT.inc()
        recv = "Received: {}\n".format(cgi.escape(request.content.read()))
        print(recv)
        return recv


class HeartBeat():

    def __init__(self):
        CONF(sys.argv[1:],
             project=_APP_NAME)

    def run(self):
        root = Resource()
        root.putChild(b'metrics', MetricsResource())
        root.putChild(b'heartbeat', HeartBeatResource())
        factory = Site(root)
        reactor.listenTCP(CONF.heartbeat.bind_port,
                          factory,
                          interface=CONF.heartbeat.bind_host)
        reactor.run()


def main():
    heartbeat = HeartBeat()
    heartbeat.run()


if __name__ == '__main__':
    sys.exit(main())
