#!/usr/bin/env python
"""
pyoctopart: A simple Python client library to the Octopart public REST API.

author: Bernard `Guyzmo` Pratz <octopart@m0g.net>
author: Joe Baker <jbaker@alum.wpi.edu>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# Linting: most of these are in service of wanting to keep parity between
#   object constructor and API reference
# pylint: disable=star-args, too-many-instance-attributes, too-many-arguments
# pylint: disable=too-many-locals, superfluous-parens

import json
import requests
import pkg_resources

from pprint import pprint

from pyoctopart.util import Curry, select, dict_to_class
from pyoctopart.objects import Part

#from .exceptions import ArgumentMissingError
#from .exceptions import ArgumentInvalidError
from .exceptions import TypeArgumentError
from .exceptions import RangeArgumentError
#from .exceptions import StringLengthError
#from .exceptions import LimitExceededError
from .exceptions import HTML404Error
from .exceptions import HTML503Error
#from .exceptions import NonJsonArgumentError
#from .exceptions import InvalidSortError
#from .exceptions import TooLongListError
from .exceptions import InvalidApiKeyError

__version__ = pkg_resources.require('pyoctopart')[0].version
__author__ = 'Joe Baker <jbaker at alum.wpi.edu>'
__contributors__ = ['Bernard `Guyzmo` Pratz <pyoctopart at m0g dot net>',
                    'Andrew Tergis <theterg at gmail got com>']


select_incls = Curry(select, 'include_')
select_shows = Curry(select, 'show_')
select_hides = Curry(select, 'hide_')


# Octopart API proxy '''

class Octopart(object):

    """A simple client frontend to tho Octopart public REST API.

    For detailed API documentation,
        refer to https://octopart.com/api/docs/v3/rest-api
    """

    api_url = 'http://octopart.com/api/v%d/'
    __slots__ = ['apikey', 'callback', 'pretty_print', 'verbose']

    def __init__(self, apikey=None, callback=None,
            pretty_print=False, verbose=False):
        self.apikey = apikey
        self.callback = callback
        self.pretty_print = pretty_print
        self.verbose = verbose


    def _get_data(self, method, args, payload=None, ver=2):
        """Constructs the URL to pass to _get().

        param method: String containing the method path, such as 'parts/search'.
        param args: Dictionary of arguments to pass to the API method.
        returns: Complete request URL string.
        """
        if payload is None:
            payload = dict()
        req_url = Octopart.api_url % ver + method

        if self.apikey:
            payload['apikey'] = self.apikey
        if self.callback:
            payload['callback'] = self.callback

        for arg, val in args.items():
            if type(val) is bool:
                new_val = int(val)
            elif type(val) is list:
                new_val = json.dumps(val)
            else:
                new_val = val
            payload[arg] = new_val

        req = requests.get(req_url, params=payload)
        if req.status_code == 404:
            raise HTML404Error(args, [], [])
        elif req.status_code == 503:
            raise HTML503Error(args, [], [])

        req = req.json()

        if self.verbose:
            if self.pretty_print:
                pprint(req)
            else:
                print(req)

        if 'message' in req.keys() and req['message'] == 'Invalid API key':
            raise InvalidApiKeyError(self.apikey)

        return req


    # API v3 Methods

    # pylint: disable=invalid-name
    def parts_search(self,
                     q="",
                     start=0,
                     limit=10,
                     sortby="score desc",
                     ):
        ''' https://octopart.com/api/docs/v3/rest-api#endpoints-parts-search'''
        # filter[fields][<fieldname>][]: string = "",
        # filter[queries][]: string = "",
        # facet[fields][<fieldname>][include]: boolean = false,
        # facet[fields][<fieldname>][exclude_filter]: boolean = false,
        # facet[fields][<fieldname>][start]: integer = 0,
        # facet[fields][<fieldname>][limit]: integer = 10,
        # facet[queries][]: string = "",
        # stats[<fieldname>][include]: boolean = false,
        # stats[<fieldname>][exclude_filter]: boolean = false,
        # spec_drilldown[include]: boolean = false,
        # spec_drilldown[exclude_filter]: boolean = false,
        # spec_drilldown[limit]: integer = 10
        method = 'parts/search'

        if not len(q) >= 2:
            raise RangeArgumentError(['q'], [int], [2, float('inf')])
        if limit not in range(0, 101):
            raise RangeArgumentError(['limit'], [int], [0, 100])
        if start not in range(0, 1001):
            raise RangeArgumentError(['limit'], [int], [0, 1000])

        json_obj = self._get_data(method, {
            'q': q, 'limit': limit, 'start': start, 'sortby': sortby},
            ver=3)

        if json_obj:
            return dict_to_class(json_obj)
        else:
            return None

    def parts_match(self,
                    queries,
                    exact_only=False,
                    **show_hide):
        '''
        https://octopart.com/api/docs/v3/rest-api#endpoints-parts-match
        '''

        method = 'parts/match'

        args = {'queries': queries, 'exact_only': exact_only}
        params = {}

        params.update(Part.includes(**select_incls(show_hide)))
        params.update(Part.shows(**select_shows(show_hide)))
        params.update(Part.hides(**select_hides(show_hide)))

        for q in queries:
            if type(q) != dict:
                raise TypeArgumentError(['queries'], ['str'], [])

        json_obj = self._get_data(method, args, params, ver=3)

        # XXX consider using the following?
        # items = [Part.new_from_dict(item) for\
        #  item in json_obj['results']['items']]

        if json_obj:
            return dict_to_class(json_obj)
        else:
            return None

    def parts_get(self, uid):
        '''
        https://octopart.com/api/docs/v3/rest-api#endpoints-parts-get
        '''
        method = 'parts/{:d}'.format(uid)

        json_obj = self._get_data(method, {}, ver=3)

        if json_obj:
            return dict_to_class(json_obj)
        else:
            return None

