# The MIT License (MIT) # Copyright (c) 2014-2017 University of Bristol
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

from base_channel import BaseChannel
from ..stream import Stream, StreamInstance
from ..time_interval import TimeIntervals
from ..utils import MIN_DATE
from ..errors import StreamNotFoundError, StreamAlreadyExistsError

import logging


class MemoryChannel(BaseChannel):
    def __init__(self, channel_id):
        super(MemoryChannel, self).__init__(channel_id=channel_id, can_calc=True, can_create=True)
        self.max_stream_id = 0
        self.data = dict()
    
    def create_stream(self, stream_id):
        """
        Must be overridden by deriving classes, must create the stream according to the tool and return its unique
        identifier stream_id
        """
        if stream_id in self.streams:
            raise StreamAlreadyExistsError("Stream with id '{}' already exists".format(stream_id))
        
        # TODO: Want to be able to define the streams in the database
        stream = Stream(channel=self, stream_id=stream_id)
        
        self.streams[stream_id] = stream
        self.data[stream_id] = []
        return stream

    def clear_stream(self, stream_id):
        if stream_id not in self.streams:
            raise StreamNotFoundError(stream_id)
        self.data[stream_id] = []

    def delete_stream(self, stream_id):
        if stream_id not in self.streams:
            raise StreamNotFoundError(stream_id)
        del self.streams[stream_id]
        del self.data[stream_id]

    def update_streams(self, up_to_timestamp):
        raise NotImplementedError
    
    def check_calculation_times(self):
        pass

    def get_results(self, stream, time_interval):
        """
        Calculates/receives the documents in the stream interval determined by the stream
        :param stream: The stream reference
        :param time_interval: The time interval
        :return: The sorted data items
        """
        return sorted((d for d in self.data[stream.stream_id] if d.timestamp in time_interval),
                      key=lambda d: d.timestamp)

    def get_stream_writer(self, stream):
        def writer(document_collection):
            # TODO from niall: I added this type check to fix bug with the Apply tool. \
            #   please verify that it does not interfere with other code
            if stream.stream_id not in self.data:
                raise RuntimeError("Data slot does not exist for {}, perhaps create_stream was not used?"
                                   .format(stream))
            if isinstance(document_collection, StreamInstance):
                self.data[stream.stream_id].append(document_collection)
            elif isinstance(document_collection, list):
                self.data[stream.stream_id].extend(document_collection)
            else:
                raise ValueError('Expected: [StreamInstance, list<StreamInstance>], got {}. '
                                 .format(type(document_collection)))
        
        return writer


class ReadOnlyMemoryChannel(BaseChannel):
    """
    An abstract channel with a read-only set of memory-based streams.
    By default it is constructed empty with the last update at MIN_DATE.
    New streams and documents within streams are created with the update(up_to_timestamp) method,
    which ensures that the channel is up to date until up_to_timestamp.
    No documents nor streams are ever deleted.
    Any deriving class must override update_streams(up_to_timestamp) which must update self.streams to be calculated
    until up_to_timestamp exactly.
    The data structure self.streams is a dict of streams indexed by stream_id, each stream is a list of tuples
    (timestamp,data), in no specific order.
    Names and identifiers are the same in this channel.
    """
    
    def __init__(self, channel_id, up_to_timestamp=MIN_DATE):
        # TODO: should the up_to_timestamp parameter be up to datetime.max?
        super(ReadOnlyMemoryChannel, self).__init__(channel_id=channel_id, can_calc=False, can_create=False)
        self.up_to_timestamp = MIN_DATE
        if up_to_timestamp > MIN_DATE:
            self.update_streams(up_to_timestamp)
            self.update_state(up_to_timestamp)
    
    def create_stream(self, stream_id):
        raise RuntimeError("Read-only channel")
    
    def get_stream_writer(self, stream):
        raise RuntimeError("Read-only channel")
    
    # def str_stream(self, stream_id):
    #     return 'externally defined, memory-based, read-only stream'
    
    def update_streams(self, up_to_timestamp):
        """
        Deriving classes must override this function
        """
        raise NotImplementedError
    
    def update_state(self, up_to_timestamp):
        """
        Call this function to ensure that the channel is up to date at the time of timestamp.
        I.e., all the streams that have been created before or at that timestamp are calculated exactly until
        up_to_timestamp.
        """
        # for stream_id in self.streams:
        #     self.streams[stream_id].calculated_intervals = TimeIntervals([(MIN_DATE, up_to_timestamp)])
        for stream in self.streams:
            stream.calculated_intervals = TimeIntervals([(MIN_DATE, up_to_timestamp)])
        self.up_to_timestamp = up_to_timestamp
    
    def get_results(self, stream, time_interval):
        raise NotImplementedError
        # # start = relative_time_interval.start
        # # end = relative_time_interval.end
        # # if isinstance(start, timedelta) or isinstance(end, timedelta):
        # #     raise ValueError('Cannot calculate a relative stream')
        # # if end > self.up_to_timestamp:
        # #     raise ValueError(
        # #         'The stream is not available after ' + str(self.up_to_timestamp) + ' and cannot be calculated')
        # result = []
        # for (tool_info, data) in self.streams[stream.stream_id]:
        #     if start < tool_info.timestamp <= end:
        #         result.append(StreamInstance(tool_info.timestamp, data))
        # return sorted(result, key=lambda x: x.timestamp)
