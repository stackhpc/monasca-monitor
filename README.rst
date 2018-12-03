===============
Monasca Monitor
===============

.. image:: https://travis-ci.org/stackhpc/monmon.svg?branch=master
   :target: https://travis-ci.org/stackhpc/monmon

A proof of concept system-level monitor for Monasca.

Performs a continuous system level test on a live Monasca deployment by
perodically sending probe metrics to the Monasca API. The probe metrics
are used to trigger an alarm, which fires a notification back to this
service. The alarm notification events received by `monasca-monitor` are
then made available to Prometheus to scrape. Prometheus can then be
configured to alert a user if the notification events fail to arrive.

Future work
-----------

> Automatic alarm creation

> Automatic notification creation

> Config file which supports endpoint definition

> Better error handling

Instructions
------------

Install monasca monitor into a Python virtualenv, for example:

.. code:: shell

    virtualenv monasca-monitor
    source monasca-monitor/bin/activate
    pip install .

Source OpenStack credentials containing the OpenStack user which will
be used to post metrics to the Monasca API, and the OpenStack Project
and Domain which the metrics will be stored in. For example:

.. code:: shell

    source ~/admin-openrc.sh

Run the metrics source (it is recommended to do this in a screen
session or similar):

.. code:: shell

    python metrics_source.py

Run the heart beat generator (this processes notifications from Monasca
and makes them available to Prometheus):

.. code:: shell

    python heartbeat.py

Configure Prometheus to scrape the endpoint (by default `localhost:8000`).
