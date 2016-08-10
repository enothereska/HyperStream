"""
The MIT License (MIT)
Copyright (c) 2014-2016 University of Bristol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from collections import WorkflowCollection, ToolCollection, StreamCollection
from client import Client


class OnlineEngine(object):
    def __init__(self, sphere_connector, hyperstream_config):
        self.sphere_connector = sphere_connector
        self.config = hyperstream_config
        self.client = Client(self.config.mongo)

        self.tools = ToolCollection(self.config.tool_path)
        self.streams = StreamCollection(self.tools)
        self.workflows = WorkflowCollection()

    def execute(self):
        self.workflows.execute_all(self.sphere_connector)