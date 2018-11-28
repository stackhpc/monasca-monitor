import cgi

from prometheus_client import Counter
from prometheus_client.twisted import MetricsResource
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site


_HEARTBEAT = Counter(
    'monasca_monitor_heartbeat',
    'Monasca system level heartbeat')


class HeartBeatResource(Resource):

    def render_POST(self, request):
        _HEARTBEAT.inc()
        recv = "Received: {}\n".format(cgi.escape(request.content.read()))
        print(recv)
        return recv


class HeartBeat():
    def __init__(self, twisted_port=8000):
        self.twisted_port = twisted_port

    def run(self):
        root = Resource()
        root.putChild(b'metrics', MetricsResource())
        root.putChild(b'heartbeat', HeartBeatResource())
        factory = Site(root)
        reactor.listenTCP(self.twisted_port, factory)
        reactor.run()


if __name__ == '__main__':
    heartbeat = HeartBeat()
    heartbeat.run()
