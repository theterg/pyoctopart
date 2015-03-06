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
            """
            Compares two offers.
            class_offer: An offer from an OctopartPart instance.
            json_offer: An offer from a JSON Part resource.
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
            """
            Compares two specs.
            class_spec: A spec from an OctopartPart instance.
            json_spec: A spec from a JSON Part resource.
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

    For detailed API documentation, refer to https://octopart.com/api/docs/v2/rest-api.
    """

    api_url = 'http://octopart.com/api/v2/'
    __slots__ = ["apikey", "callback", "pretty_print"]

    def __init__(self, apikey=None, callback=None, pretty_print=False):
        self.apikey = apikey
        self.callback = callback
        self.pretty_print = pretty_print

    def parts_suggest(self,
                      q: str,
                      limit: int = None):
        """Suggest a part search query string.

        Optimized for speed (useful for auto-complete features).

        returns A pair containing:
        - The raw JSON result dictionary.
        - A list of manufacturer part number strings.
        If no JSON object is found without an Exception being raised, returns None.
        """

        method = 'parts/suggest'

        if not q >= 2:
            raise OctopartRangeArgumentError(['q'], [int], [2,float('inf')])
        if limit not in range(0,10):
            raise OctopartRangeArgumentError(['limit'], [int], [0,10])

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

        returns a list of (part uid, manufacturer displayname, mpn) tuples.
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

        returns A pair containing:
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

        returns A pair containing:
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

        returns A pair containing:
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
            'optimize.return.stubs' :                  optimize_return_stubs,
            'optimize.hide.datasheets' :               optimize_hide_datasheets,
            'optimize.hide.descriptions' :             optimize_hide_descriptions,
            'optimize.hide.images' :                   optimize_hide_images,
            'optimize.hide.hide_offers' :              optimize_hide_hide_offers,
            'optimize.hide.hide_unauthorized_offers' : optimize_hide_hide_unauthorized_offers,
            'optimize.hide.specs' :                    optimize_hide_specs,
        }

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

