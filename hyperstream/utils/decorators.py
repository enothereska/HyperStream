"""
The MIT License (MIT)
Copyright (c) 2014-2017 University of Bristol

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
import time
import logging


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        logging.info('func:{} args:[{}, {}] took: {:2.4f} sec'.format(f.__name__, args, kw, te - ts))
        return result

    return timed


def check_output_format(expected_formats):
    """
    Decorator for stream outputs that checks the format of the outputs after modifiers have been applied
    :param expected_formats: The expected output formats
    :type expected_formats: tuple, set
    :return: the decorator
    """
    def output_format_decorator(func):
        def func_wrapper(*args, **kwargs):
            self = args[0]
            if self.output_format not in expected_formats:
                raise ValueError("expected output format {}, got {}".format('doc_gen', self.output_format))
            return func(*args, **kwargs)
        return func_wrapper
    return output_format_decorator