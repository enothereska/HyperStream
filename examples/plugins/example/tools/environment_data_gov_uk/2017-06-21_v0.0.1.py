# The MIT License (MIT)
# Copyright (c) 2014-2017 University of Bristol
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from datetime import datetime
from datetime import datetime, timedelta

from hyperstream import Tool, StreamInstance, StreamInstanceCollection
from hyperstream.utils import check_input_stream_count
from hyperstream.utils import UTC

from dateutil.parser import parse

import urllib
import urllib2
import json

# this uses Environment Agency flood and river level data from the real-time
# data API (Beta)
# For questions on the APIs please contact data.info@environment-agency.gov.uk,
# a forum for announcements and discussion is under consideration.
class EnvironmentDataGovUk(Tool):
    def __init__(self, station):
        self.station = station
        super(EnvironmentDataGovUk, self).__init__()

    @check_input_stream_count(0)
    def _execute(self, sources, alignment_stream, interval):
        startdate = interval[0].strftime("%Y-%m-%d")
        enddate = interval[1].strftime("%Y-%m-%d")

        url = "https://environment.data.gov.uk/flood-monitoring/id/stations/{}/readings".format(self.station)
        values = {'startdate' : startdate,
                  'enddate' : enddate}
        url_parameters = urllib.urlencode(values)

        full_url = url + '?' + url_parameters
        response = urllib2.urlopen(full_url)
        data = json.load(response)

        for item in data['items']:
            dt = parse(item.get('dateTime'))
            if dt in interval:
                value = float(item.get('value'))
                yield StreamInstance(dt, value)
