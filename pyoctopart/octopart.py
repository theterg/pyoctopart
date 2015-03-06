#!/usr/bin/env python
"""
A simple Python client library to the Octopart public REST API.

@author: Bernard `Guyzmo` Pratz <octopart@m0g.net>
@author: Joe Baker <jbaker@alum.wpi.edu>

@license:
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

__version__ = "0.6.0"
__author__ = "Joe Baker <jbaker@alum.wpi.edu>"
__contributors__ = ["Bernard Pratz <pyoctopart@m0g.net>"]

import copy
import urllib.parse
import requests
from requests import HTTPError
import json
from types import *
import datetime

from .exceptions import OctopartArgumentMissingError, \
                        OctopartArgumentInvalidError, \
                        OctopartTypeArgumentError, \
                        OctopartRangeArgumentError, \
                        OctopartStringLengthError, \
                        OctopartLimitExceededError, \
                        Octopart404Error, \
                        Octopart503Error, \
                        OctopartNonJsonArgumentError, \
                        OctopartInvalidSortError, \
                        OctopartTooLongListError

class OctopartBrand(object):
    def __init__(self, id, dispname, homepage):
        self._id = id
        self.displayname = dispname
        self.homepage_url = homepage

    @classmethod
    def new_from_dict(cls, brand_dict):
        new = cls(brand_dict['id'], brand_dict['displayname'], brand_dict['homepage_url'])
        return new

    @property
    def id(self):
        return self._id

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON Brand resource."""

        if isinstance(resource, dict) and resource.get('__class__') == 'Brand':
            if self.id != resource.get('id'):
                return False
            if self.displayname != resource.get('displayname'):
                return False
            if self.homepage_url != resource.get('homepage_url'):
                return False
        else:
            return False
        return True

    def __eq__(self, b):
        if isinstance(b, OctopartBrand):
            try:
                if self.id != b.id:
                    return False
                if self.displayname != b.displayname:
                    return False
                if self.homepage_url != b.homepage_url:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, b):
        return not self.__eq__(b)

    def __hash__(self):
        return (hash(self.__class__), hash(self.id))

    def __str__(self):
        return ''.join(('Brand ', str(self.id), ': ', self.displayname, ' (', self.homepage_url, ')'))

class OctopartCategory(object):

    @classmethod
    def new_from_dict(cls, category_dict):
        new_dict = copy.deepcopy(category_dict)
        new = cls(new_dict['id'], new_dict['parent_id'], new_dict['nodename'], \
                            new_dict['images'], new_dict['children_ids'], new_dict['ancestor_ids'], \
                            new_dict.get('ancestors', []), new_dict['num_parts'])
        return new

    def __init__(self, id, parent_id, nodename, images, children_ids, ancestor_ids, ancestors, num_parts):
        self._id = id
        self.parent_id = parent_id
        self.nodename = nodename
        self.images = images    # List of dicts of URLs
        self.children_ids = children_ids    # List of child node ids
        self.ancestor_ids = ancestor_ids    # Sorted list of ancestor node ids (immediate parent first)
        self.ancestors = ancestors    # Sorted list of category objects
        self.num_parts = num_parts

    @property
    def id(self):
        return self._id

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON Category resource."""

        if isinstance(resource, dict) and resource.get('__class__') == 'Category':
            if self.id != resource.get('id'):
                return False
            if self.parent_id != resource.get('parent_id'):
                return False
            if self.nodename != resource.get('nodename'):
                return False
            if sorted(self.images) != sorted(resource.get('images')):
                return False
            if sorted(self.children_ids) != sorted(resource.get('children_ids')):
                return False
            if sorted(self.ancestor_ids) != sorted(resource.get('ancestor_ids')):
                return False
            if set(self.ancestors) != set(resource.get('ancestors', [])):
                return False
            if self.num_parts != resource.get('num_parts'):
                return False
        else:
            return False
        return True

    def __eq__(self, c):
        if isinstance(c, OctopartCategory):
            try:
                if self.id != c.id:
                    return False
                if self.parent_id != c.parent_id:
                    return False
                if self.nodename != c.nodename:
                    return False
                if sorted(self.images != c.images):
                    return False
                if sorted(self.children_ids) != sorted(c.children_ids):
                    return False
                if sorted(self.ancestor_ids) != sorted(c.ancestor_ids):
                    return False
                if set(self.ancestors) != set(c.ancestors):
                    return False
                if self.num_parts != c.num_parts:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, c):
        return not self.__eq__(c)

    def __hash__(self):
        return (hash(self.__class__), hash(self.id))

    def __str__(self):
        return ''.join(('Category ', str(self.id), ': ', self.nodename))

class OctopartPart(object):

    @classmethod
    def new_from_dict(cls, part_dict):
        """Constructor for use with JSON resource dictionaries."""

        copied_dict = part_dict.copy()
        uid = copied_dict.pop('uid')
        mpn = copied_dict.pop('mpn')
        manufacturer = copied_dict.pop('manufacturer')
        detail_url = copied_dict.pop('detail_url')
        return cls(uid, mpn, manufacturer, detail_url, **copied_dict)

    def __init__(self, uid, mpn, manufacturer, detail_url, **kwargs):
        # If class data is in dictionary format, convert everything to class instances
        # Otherwise, assume it is already in class format and do nothing
        args = copy.deepcopy(kwargs)
        if type(manufacturer) is dict:
            manufacturer = OctopartBrand.new_from_dict(copy.deepcopy(manufacturer))
        for offer in args.get('offers', []):
            if type(offer['supplier']) is dict:
                offer['supplier'] = OctopartBrand.new_from_dict(offer['supplier'])
            # Convert ISO 8601 datetime strings to datetime objects
            if 'update_ts' in offer:
                # Strip 'Z' UTC notation that can't be parsed
                if offer['update_ts'][-1] == 'Z':
                    offer['update_ts'] = offer['update_ts'][0:-1]
                offer['update_ts'] = datetime.datetime.strptime(offer['update_ts'], '%Y-%m-%dT%H:%M:%S')

        for spec in args.get('specs', []):
            if type(spec['attribute']) is dict:
                spec['attribute'] = OctopartPartAttribute.new_from_dict(spec['attribute'])

        self._uid = uid
        self._mpn = mpn
        self.manufacturer = manufacturer
        self.detail_url = detail_url
        self.avg_price = args.get('avg_price')
        self.avg_avail = args.get('avg_avail')
        self.market_status = args.get('market_status')
        self.num_suppliers = args.get('num_suppliers')
        self.num_authsuppliers = args.get('num_authsuppliers')
        self.short_description = args.get('short_description', '')
        self.category_ids = args.get('category_ids', [])
        self.images = args.get('images', [])
        self.datasheets = args.get('datasheets', [])
        self.descriptions = args.get('descriptions', [])
        self.hyperlinks = args.get('hyperlinks', {})
        self.offers = args.get('offers', [])
        self.specs = args.get('specs', [])

    @property
    def uid(self):
        return self._uid

    @property
    def mpn(self):
        return self._mpn

    def get_authorized_offers(self):
        return [o for o in self.offers if o['is_authorized'] is True]

    def get_unauthorized_offers(self):
        return [o for o in self.offers if o['is_authorized'] is False]

    def equals_json(self, resource, hide_datasheets=False, hide_descriptions=False, hide_images=False, \
                hide_offers=False, hide_unauthorized_offers=False, hide_specs=False):
        """Checks the object for data equivalence to a JSON Part resource."""

        def compare_offers(class_offer, json_offer):
            """Compares two offers.

            @param class_offer: An offer from an OctopartPart instance.
            @param json_offer: An offer from a JSON Part resource.
            """

            class_attribs = (class_offer['sku'], class_offer['avail'], class_offer['prices'], \
                            class_offer['is_authorized'], class_offer.get('clickthrough_url'), \
                            class_offer.get('buynow_url'), class_offer.get('sendrfq_url'))
            json_attribs = (json_offer['sku'], json_offer['avail'], json_offer['prices'], \
                            json_offer['is_authorized'], json_offer.get('clickthrough_url'), \
                            json_offer.get('buynow_url'), json_offer.get('sendrfq_url'))
            if class_attribs != json_attribs:
                return False
            if not class_offer['supplier'].equals_json(json_offer['supplier']):
                return False
            return True

        def compare_specs(class_spec, json_spec):
            """Compares two specs.

            @param class_spec: A spec from an OctopartPart instance.
            @param json_spec: A spec from a JSON Part resource.
            """

            if not class_spec['attribute'].equals_json(json_spec['attribute']):
                return False
            if sorted(class_spec['values']) != sorted(json_spec['values']):
                return False
            return True

        if isinstance(resource, dict) and resource.get('__class__') == 'Part':
            if self.uid != resource.get('uid'):
                return False
            if self.mpn != resource.get('mpn'):
                return False
            if not self.manufacturer.equals_json(resource.get('manufacturer')):
                return False
            if self.detail_url != resource.get('detail_url'):
                return False
            if self.avg_price != resource.get('avg_price'):
                return False
            if self.avg_avail != resource.get('avg_avail'):
                return False
            if self.market_status != resource.get('market_status'):
                return False
            if self.num_suppliers != resource.get('num_suppliers'):
                return False
            if self.num_authsuppliers != resource.get('num_authsuppliers'):
                return False
            if self.short_description != resource.get('short_description', ''):
                return False
            if sorted(self.category_ids) != sorted(resource.get('category_ids', [])):
                return False
            if hide_images is False and sorted(self.images) != sorted(resource.get('images', [])):
                return False
            if hide_datasheets is False and sorted(self.datasheets) != sorted(resource.get('datasheets', [])):
                return False
            if hide_descriptions is False and sorted(self.descriptions) != sorted(resource.get('descriptions', [])):
                return False
            if self.hyperlinks != resource.get('hyperlinks', {}):
                return False
            if hide_offers is False:
                checked_offers = []
                if hide_unauthorized_offers:
                    checked_offers = sorted(self.get_unauthorized_offers())
                else:
                    checked_offers = sorted(self.offers)
                for offer in checked_offers:
                    truth = [compare_offers(offer, other) for other in sorted(resource.get('offers', []))]
                    if True not in truth:
                        return False
            if not hide_specs:
                for spec in sorted(self.specs):
                    truth = [compare_specs(spec, other) for other in sorted(resource.get('specs', []))]
                    if True not in truth:
                        return False
        else:
            return False
        return True

    def __eq__(self, p):
        if isinstance(p, OctopartPart):
            try:
                if self.uid != p.uid:
                    return False
                if self.mpn != p.mpn:
                    return False
                if self.manufacturer != p.manufacturer:
                    return False
                if self.detail_url != p.detail_url:
                    return False
                if self.avg_price != p.avg_price:
                    return False
                if self.avg_avail != p.avg_avail:
                    return False
                if self.market_status != p.market_status:
                    return False
                if self.num_suppliers != p.num_suppliers:
                    return False
                if self.num_authsuppliers != p.num_authsuppliers:
                    return False
                if self.short_description != p.short_description:
                    return False
                if self.category_ids != p.category_ids:
                    return False
                if self.images != p.images:
                    return False
                if self.datasheets != p.datasheets:
                    return False
                if self.descriptions != p.descriptions:
                    return False
                if self.hyperlinks != p.hyperlinks:
                    return False
                if self.offers != p.offers:
                    return False
                if self.specs != p.specs:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, p):
        return not self.__eq__(p)

    def __hash__(self):
        return (hash(self.__class__), hash(self.uid), hash(self.mpn))

    def __str__(self):
        return ''.join(('Part ', str(self.uid), ': ', str(self.manufacturer), ' ', self.mpn))

class OctopartPartAttribute(object):
    TYPE_TEXT = 'text'
    TYPE_NUMBER = 'number'

    @classmethod
    def new_from_dict(cls, attribute_dict):
        new = cls(attribute_dict['fieldname'], attribute_dict['displayname'], attribute_dict['type'], attribute_dict.get('metadata', {}))
        return new

    def __init__(self, fieldname, displayname, attribute_type, metadata):
        self._fieldname = fieldname
        self.displayname = displayname
        self.type = attribute_type
        self.metadata = metadata

    @property
    def fieldname(self):
        return self._fieldname

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON PartAttribute resource."""

        if isinstance(resource, dict) and resource.get('__class__') == 'PartAttribute':
            if self.fieldname != resource.get('fieldname'):
                return False
            if self.displayname != resource.get('displayname'):
                return False
            if self.type != resource.get('type'):
                return False
            if self.metadata != resource.get('metadata', {}):
                return False
        else:
            return False
        return True

    def __eq__(self, pa):
        if isinstance(pa, OctopartPartAttribute):
            try:
                if self.fieldname != pa.fieldname:
                    return False
                if self.displayname != pa.displayname:
                    return False
                if self.type != pa.type:
                    return False
                if self.metadata != pa.metadata:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, pa):
        return not self.__eq__(pa)

    def __hash__(self):
        return (hash(self.__class__), hash(self.fieldname))

    def __str__(self):
        if self.type == 'number':
            return ''.join((self.displayname, 'attribute: ', self.metadata['datatype'], ' (', self.metadata['unit']['name'], ')'))
        elif self.type == 'text':
            return ''.join((self.displayname, 'attribute: ', self.type))
        else:    # Note: 'else' is not a valid state in the API resource definition
            return self.displayname

class Octopart(object):

    """A simple client frontend to tho Octopart public REST API.

    For detailed API documentation, refer to http://octopart.com/api/documentation.
    """

    api_url = 'http://octopart.com/api/v2/'
    __slots__ = ["apikey", "callback", "pretty_print"]

    def __init__(self, apikey=None, callback=None, pretty_print=False):
        self.apikey = apikey
        self.callback = callback
        self.pretty_print = pretty_print

    def _validate_args(self, args, arg_types, arg_ranges):
        """ Checks method arguments for syntax errors.

        @param args: Dictionary of argumets to check
        @param arg_types: Dictionary which contains the correct data type for each argument.
        @param arg_ranges: Dictionary which contains range() calls for any numeric arguments with a limited range.
        Can also be used to constrain string argument length. For string arguments, contains a (min, max) pair.
        @raise OctopartException: If any syntax errors are found.
        """

        valid_args = frozenset(list(arg_types.keys()))
        args_set = set(args.keys())

        if args_set.issubset(valid_args) is False:
            raise OctopartArgumentInvalidError(args, arg_types, arg_ranges)
        for key in args_set:
            if arg_types[key] is str:
                if isinstance(args[key], str) is False:
                    raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            elif type(arg_types[key]) is tuple:    # Tuple of types
                if type(args[key]) not in arg_types[key]:
                    raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            else:
                if type(args[key]) is not arg_types[key]:
                    raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            if key in list(arg_ranges.keys()):
                if arg_types[key] in (int, float):
                    if args[key] < arg_ranges[key][0] or args[key] > arg_ranges[key][1]:
                        raise OctopartRangeArgumentError(args, arg_types, arg_ranges)
                elif len(args[key]) < arg_ranges[key][0] or len(args[key]) > arg_ranges[key][1]:
                    if arg_types[key] is str:
                        raise OctopartStringLengthError(args, arg_types, arg_ranges)
                    elif arg_types[key] is list:
                        raise OctopartTooLongListError(args, arg_types, arg_ranges, 11)
        if len(args_set) != len(list(args.keys())):
            raise OctopartTypeArgumentError(args, arg_types, arg_ranges)

    def _get_data(self, method, args):
        """Constructs the URL to pass to _get().

        TODO: replace this method with a requests get method build!

        @param method: String containing the method path, such as "parts/search".
        @param args: Dictionary of arguments to pass to the API method.
        @return: Complete request URL string.
        """
        req_url = Octopart.api_url + method

        payload=dict()
        if self.apikey:
            payload['apikey'] = self.apikey
        if self.callback:
            payload['callback'] = self.callback
        if self.pretty_print:
            payload['pretty_print'] = self.pretty_print

        for arg, val in args.items():
            if type(val) is bool:
                v = int(val)
            elif type(val) is list:
                v = json.dumps(val)
            else:
                v = val
            payload[arg] = v

        r = requests.get(req_url, params=payload)
        r.raise_for_status()
        return r.json()

    def _translate_periods(self, args):
        """Translates Python-friendly keyword arguments to valid Octopart API arguments.

        Several Octopart API arguments contain a period in their name.
        Unfortunately, trying to unpack a keyword argument in a Python function with
        a period in the argument name will cause a syntax code:
        'keyword can't be an expression'

        Therefore, the Python API methods expect an underscore in place of the
        periods in the argument names. This method replaces those underscores with
        periods for passing to the private class methods, which do not attempt
        to unpack the arguments dict.

        @param args: Unpackable keyword arguments dict from a public API call.
        @return Translated keyword arguments dict.
        """

        translation = {'drilldown_include' : 'drilldown.include', \
                    'drilldown_fieldname' : 'drilldown.fieldname', \
                    'drilldown_facets_prefix' : 'drilldown.facets.prefix', \
                    'drilldown_facets_start' : 'drilldown.facets.start', \
                    'drilldown_facets_limit' : 'drilldown.facets.limit', \
                    'drilldown_facets_sortby' : 'drilldown.facets.sortby', \
                    'drilldown_facets_include_hits' : 'drilldown.facets.include_hits', \
                    'optimize_return_stubs' : 'optimize.return_stubs', \
                    'optimize_hide_datasheets' : 'optimize.hide_datasheets', \
                    'optimize_hide_descriptions' : 'optimize.hide_descriptions', \
                    'optimize_hide_images' : 'optimize.hide_images', \
                    'optimize_hide_hide_offers' : 'optimize.hide_hide_offers', \
                    'optimize_hide_hide_unauthorized_offers' : 'optimize.hide_hide_unauthorized_offers', \
                    'optimize_hide_specs' : 'optimize.hide_specs'}

        for key in args:
            # Handle any list/dict arguments which may contain more arguments within
            if type(args[key]) is dict:
                args[key] = self._translate_periods(args[key])
            elif type(args[key]) is list:
                for a in args[key]:
                    if type(a) is dict:
                        a = self._translate_periods(a)

            if key in translation:
                args[translation[key]] = args.pop(key)

        return args

    def _categories_get_args(self, id: int):
        """Validate and format arguments passed to categories_get().

        @return: Dictionary of valid arguments to pass to _make_url().
        @raise OctopartException: Raised if invalid argument syntax is passed in.
        """

        arg_types = {'id': (int,)}
        arg_ranges = {}
        args = {'id' : id}
        self._validate_args(args, arg_types, arg_ranges)

        return args

    def categories_get(self, id):
        """Fetch a category object by its id.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -An OctopartCategory object.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'categories/get'
        args = self._categories_get_args(id)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                return None
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        if json_obj:
            return json_obj, OctopartCategory.new_from_dict(json_obj)
        else:
            return None

    def categories_get_multi(self, ids: list) -> tuple:
        """Fetch multiple category objects by their ids.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of OctopartCategory objects.
        If no JSON object is found without an Exception being raised, returns None.
        """
        method = 'categories/get_multi'

        # XXX to be changed with PEP-0484 integration
        # type checking
        args = {'ids': ids}
        for id in ids:
            if type(id) not in (int,):
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)

        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, arg_types, arg_ranges)
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e

        if json_obj:
            return json_obj, [OctopartCategory.new_from_dict(category) for category in json_obj]
        else:
            return None

    def categories_search(self, q: str,
                          start: int = None,
                          limit: int = None,
                          ancestor_id: int = None, **kwargs):
        """Execute search over all result objects.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of (OctopartCategory, highlight_text) pairs for each result.
        If no JSON object is found without an Exception being raised, returns None.
        """
        method = 'categories/search'
        args = {
            'q': q,
            'start': start,
            'limit': limit,
            'ancestor_id': ancestor_id,
        }
        args.update(kwargs)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, [], [])
            elif e.code == 503:
                raise Octopart503Error(args, [], [])
            else:
                raise e
        if json_obj:
            results = [(OctopartCategory.new_from_dict(result['item']), result['highlight']) for result in json_obj['results']]
            return json_obj, results
        else:
            return None

    def parts_get(self,
                  uid: str,
                  optimize_hide_datasheets: bool = False,
                  optimize_hide_descriptions: bool = False,
                  optimize_hide_images: bool = False,
                  optimize_hide_hide_offers: bool = False,
                  optimize_hide_hide_unauthorized_offers: bool = False,
                  optimize_hide_specs: bool = False):
        """Fetch a part object by its id.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -An OctopartPart object.
        If no JSON object is found without an Exception being raised, returns None.
        """
        method = 'parts/get'
        args = {
            'uid'                                     : uid,
            'optimize_hide_datasheets'                : optimize_hide_datasheets,
            'optimize_hide_descriptions'              : optimize_hide_descriptions,
            'optimize_hide_images'                    : optimize_hide_images,
            'optimize_hide_hide_offers'               : optimize_hide_hide_offers,
            'optimize_hide_hide_unauthorized_offers'  : optimize_hide_hide_unauthorized_offers,
            'optimize_hide_specs'                     : optimize_hide_specs
        }
        args = self._translate_periods(args)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                return None
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        if json_obj:
            return json_obj, OctopartPart.new_from_dict(json_obj)
        else:
            return None

    def parts_get_multi(self, uids: list,
                        optimize_hide_datasheets: bool = False,
                        optimize_hide_descriptions: bool = False,
                        optimize_hide_images: bool = False,
                        optimize_hide_hide_offers: bool = False,
                        optimize_hide_hide_unauthorized_offers: bool = False,
                        optimize_hide_specs: bool = False):
        """Fetch multiple part objects by their ids.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of OctopartPart objects.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'parts/get_multi'
        for id in uids:
            if type(id) not in (int,):
                raise OctopartTypeArgumentError(args, [], [])
        args = {
            'uids'                                    : uids,
            'optimize_hide_datasheets'                : optimize_hide_datasheets,
            'optimize_hide_descriptions'              : optimize_hide_descriptions,
            'optimize_hide_images'                    : optimize_hide_images,
            'optimize_hide_hide_offers'               : optimize_hide_hide_offers,
            'optimize_hide_hide_unauthorized_offers'  : optimize_hide_hide_unauthorized_offers,
            'optimize_hide_specs'                     : optimize_hide_specs
        }
        args = self._translate_periods(args)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, arg_types, arg_ranges)
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        if json_obj:
            return json_obj, [OctopartPart.new_from_dict(part) for part in json_obj]
        else:
            return None

    def _parts_search_args(self, args):
        """Validate and format arguments passed to parts_search().

        @return: Dictionary of valid arguments to pass to _make_url().
        @raise OctopartException: Raised if invalid argument syntax is passed in.
        """

        arg_types = {'q': str, \
                    'start' : int, \
                    'limit' : int, \
                    'filters' : list, \
                    'rangedfilters' : list, \
                    'sortby' : list, \
                    'drilldown.include' : bool, \
                    'drilldown.fieldname' : str, \
                    'drilldown.facets.prefix' : str, \
                    'drilldown.facets.start' : int, \
                    'drilldown.facets.limit' : int, \
                    'drilldown.facets.sortby' : str, \
                    'drilldown.facets.include_hits' : bool, \
                    'optimize.hide_datasheets' : bool, \
                    'optimize.hide_descriptions' : bool, \
                    'optimize.hide_images' : bool, \
                    'optimize.hide_hide_offers' : bool, \
                    'optimize.hide_hide_unauthorized_offers' : bool, \
                    'optimize.hide_specs' : bool}
        arg_ranges = {'start' : (0, 1000), \
                    'limit' : (0, 100), \
                    'drilldown.facets.start' : (0, 1000), \
                    'drilldown.facets.limit' : (0, 100)}

        args = self._translate_periods(args)
        # Method-specific checks not covered by validate_args:
        for filter in args.get('filters', []):
            if len(filter) != 2:
                raise OctopartNonJsonArgumentError(args, arg_types, arg_ranges)
            if isinstance(filter[0], str) is False:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            if type(filter[1]) is not list:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)

        for filter in args.get('rangedfilters', []):
            if len(filter) != 2:
                raise OctopartNonJsonArgumentError(args, arg_types, arg_ranges)
            if isinstance(filter[0], str) is False:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            if type(filter[1]) is not list:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            for r in filter[1]:
                if len(r) != 2:
                    raise OctopartNonJsonArgumentError(args, arg_types, arg_ranges)
                for limit in r:
                    if type(limit) not in (int, float, type(None)):
                        raise OctopartTypeArgumentError(args, arg_types, arg_ranges)

        for order in args.get('sortby', []):
            if len(order) != 2:
                raise OctopartNonJsonArgumentError(args, arg_types, arg_ranges)
            if isinstance(order[0], str) is False:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            if isinstance(order[1], str) is False:
                raise OctopartTypeArgumentError(args, arg_types, arg_ranges)
            if order[1] not in ('asc', 'desc'):
                raise OctopartInvalidSortError(args, arg_types, arg_ranges,)


        self._validate_args(args, arg_types, arg_ranges)

        return args


    def parts_search(self, **kwargs):
        """Execute a search over all result objects.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of (OctopartPart, highlight_text) pairs for each result.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'parts/search'
        args = self._parts_search_args(kwargs)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, arg_types, arg_ranges)
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        if json_obj:
            results = [tuple((OctopartPart.new_from_dict(result['item']), result['highlight'])) for result in json_obj['results']]
            return json_obj, results
        else:
            return None

    def _parts_suggest_args(self, q, args):
        """Validate and format arguments passed to parts_suggest().

        @return: Dictionary of valid arguments to pass to _make_url().
        @raise OctopartException: Raised if invalid argument syntax is passed in.
        """

        arg_types = {'q': str, 'limit' : int}
        arg_ranges = {'q': (2, float("inf")), 'limit' : (0, 10)}
        args['q'] = q
        self._validate_args(args, arg_types, arg_ranges)

        return args


    def parts_suggest(self, q, **kwargs):
        """Suggest a part search query string.

        Optimized for speed (useful for auto-complete features).
        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of manufacturer part number strings.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'parts/suggest'
        args = self._parts_suggest_args(q, kwargs)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, arg_types, arg_ranges)
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        if json_obj:
            return json_obj, json_obj['results']
        else:
            return None

    def parts_match(self, manufacturer_name: str, mpn: str):
        """Match (manufacturer name, mpn) to part uid.

        @return: a list of (part uid, manufacturer displayname, mpn) tuples.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'parts/match'
        args = {
            'mpn': mpn,
            'manufacturer_name': manufacturer_name
        }
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, [], [])
            elif e.code == 503:
                raise Octopart503Error(args, [], [])
            else:
                raise e
        if json_obj:
            return json_obj
        else:
            return None

    def partattributes_get(self, fieldname: str):
        """Fetch a PartAttribute object by its fieldname.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -An OctopartPartAttribute object.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'partattributes/get'
        args = {
            'fieldname': fieldname
        }
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                return None
            elif e.code == 503:
                raise Octopart503Error(args, [], [])
            else:
                raise e
        if json_obj:
            return json_obj, OctopartPartAttribute.new_from_dict(json_obj)
        else:
            return None

    def partattributes_get_multi(self, fieldnames: list):
        """Fetch multiple PartAttribute objects by their fieldnames.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of OctopartPartAttribute objects.
        If no JSON object is found without an Exception being raised, returns None.
        """
        method = 'partattributes/get_multi'
        for name in fieldnames:
            if isinstance(name, str) is False:
                raise OctopartTypeArgumentError(args, [], [])

        args = {
            'fieldnames': fieldnames
        }
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, [], [])
            elif e.code == 503:
                raise Octopart503Error(args, [], [])
            else:
                raise e
        if json_obj:
            return json_obj, [OctopartPartAttribute.new_from_dict(attrib) for attrib in json_obj]
        else:
            return None

    def bom_match(self,
                  lines: list,
                  optimize_return_stubs : bool = False,
                  optimize_hide_datasheets : bool = False,
                  optimize_hide_descriptions : bool = False,
                  optimize_hide_images : bool = False,
                  optimize_hide_hide_offers : bool = False,
                  optimize_hide_hide_unauthorized_offers : bool = False,
                  optimize_hide_specs : bool = False):
        """Match a list of part numbers to Octopart part objects.

        @return: A pair containing:
            -The raw JSON result dictionary.
            -A list of dicts containing:
                -A list of OctopartParts.
                -A reference string.
                -A status string.
                -Optionally, the number of search hits.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'bom/match'

        def check_line(q: str,
                       mpn : str = None,
                       manufacturer : str = None,
                       sku : str = None,
                       supplier : str = None,
                       mpn_or_sku : str = None,
                       start : int = 0,
                       limit : int = 0,
                       reference : str = None):
            if limit < 0 and limit > 20:
                raise OctopartArgumentMissingError([], [], [])

        for line in lines:
            check_line(line)

        args = {
            'lines': lines,
            'optimize_return_stubs' :                  optimize_return_stubs,
            'optimize_hide_datasheets' :               optimize_hide_datasheets,
            'optimize_hide_descriptions' :             optimize_hide_descriptions,
            'optimize_hide_images' :                   optimize_hide_images,
            'optimize_hide_hide_offers' :              optimize_hide_hide_offers,
            'optimize_hide_hide_unauthorized_offers' : optimize_hide_hide_unauthorized_offers,
            'optimize_hide_specs' :                    optimize_hide_specs,
        }

        args = self._translate_periods(args)
        try:
            json_obj = self._get_data(method, args)
        except HTTPError as e:
            if e.code == 404:
                raise Octopart404Error(args, arg_types, arg_ranges)
            elif e.code == 503:
                raise Octopart503Error(args, arg_types, arg_ranges)
            else:
                raise e
        results = []
        if json_obj:
            for result in json_obj['results']:
                items = [OctopartPart.new_from_dict(item) for item in result['items']]
                new_result = {'items' : items, 'reference' : result.get('reference', ''), 'status' : result['status']}
                if result.get('hits') is not None:
                    new_result['hits'] = result.get('hits')
                results.append(new_result)

            return json_obj, results
        else:
            return None

