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

from hyperstream.tool import MultiOutputTool
from hyperstream.stream import StreamMetaInstance
from hyperstream.time_interval import TimeInterval


class StreamBroadcaster(MultiOutputTool):
    def __init__(self, output_plate_values):
        super(StreamBroadcaster, self).__init__(output_plate_values=output_plate_values)

    def _execute(self, source, splitting_stream, interval, output_plate):
        if splitting_stream is not None:
            raise NotImplementedError("Splitting stream not supported for this tool")

        # TODO: This factor is currently used to pull out the parameters of a localisation model, and as such does \
        #   use the time interval, but only pulls the last instance in the stream. Will need to change this in \
        #   future instances
        param_doc = source.window(TimeInterval.all_time(), force_calculation=True).last()

        if param_doc is None:
            return

        for vv in self.output_plate_values:
            yield StreamMetaInstance(param_doc, (output_plate.meta_data_id, str(vv)))
