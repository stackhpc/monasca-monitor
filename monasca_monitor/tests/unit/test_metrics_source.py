# Copyright (c) 2018 StackHPC Ltd.
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

import unittest
from datetime import datetime

import mock

import monasca_monitor.metrics_source as metrics_source


class TestMetricsSource(unittest.TestCase):

    @mock.patch('monasca_monitor.metrics_source.datetime.datetime')
    def test_get_heartbeat_value_odd(self, mock_datetime):
        mock_datetime.now = mock.Mock(return_value=datetime(
            year=2018, month=01, day=01, minute=1))
        value = metrics_source.MetricSource._get_heartbeat_value()
        self.assertEqual(0, value)

    @mock.patch('monasca_monitor.metrics_source.datetime.datetime')
    def test_get_heartbeat_value_even(self, mock_datetime):
        mock_datetime.now = mock.Mock(return_value=datetime(
            year=2018, month=01, day=01, minute=58))
        value = metrics_source.MetricSource._get_heartbeat_value()
        self.assertEqual(1, value)

    @mock.patch('monasca_monitor.metrics_source.datetime.datetime')
    def test_get_heartbeat_value_zero(self, mock_datetime):
        mock_datetime.now = mock.Mock(return_value=datetime(
            year=2018, month=01, day=01, minute=0))
        value = metrics_source.MetricSource._get_heartbeat_value()
        self.assertEqual(1, value)
