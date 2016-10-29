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

from hyperstream.tool import SelectorTool
from hyperstream.stream import StreamMetaInstance


class IndexOf(SelectorTool):
    """
    This tool selects a single stream from a node, and places it on the appropriate plate
    """
    def __init__(self, index, selector_meta_data):
        super(IndexOf, self).__init__(index=index, selector_meta_data=selector_meta_data)
        self.index = index

    def _execute(self, sources, interval):

        for source in sources:
            if (self.selector_meta_data, self.index) in source.stream_id.meta_data:
                return map(lambda x: StreamMetaInstance(x, source.stream_id.meta_data), source.window(interval))

        raise IndexError("Index {} not found in sources".format(self.index))
