#!/usr/bin/env python

# Linting: most of these are in service of wanting to keep parity between
#   object constructor and API reference
# pylint: disable=star-args, too-many-instance-attributes, too-many-arguments
# pylint: disable=too-many-locals, superfluous-parens
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

import copy
import json
import requests
import pkg_resources
import inspect

from pprint import pprint

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

# Utility features

class curry:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw_copy = self.kwargs.copy()
            kw_copy.update(kwargs)
        else:
            kw_copy = kwargs or self.kwargs

        return self.fun(*(self.pending + args), **kw_copy)

def dict_to_class(obj, cls):
    ''' Check if obj is an instance of cls, instantiate it otherwise '''
    if not isinstance(obj, cls):
        return cls.new_from_dict(obj)
    return obj

def list_to_class(objects, cls):
    ''' Given a list of dicts, instantiate them each as cls '''
    ret = []
    for obj in objects:
        obj = dict_to_class(obj, cls)
        ret.append(obj)
    return ret

def select(param, d):
    return {k: v for k, v in d.items() if param in k}

select_incls=curry(select, 'include_')
select_shows=curry(select, 'show_')
select_hides=curry(select, 'hide_')


# Octopart Data maps

class Asset(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-asset '''
    def __init__(self, url, mimetype, **kwargs):
        args = copy.deepcopy(kwargs)
        self.url = url
        self.mimetype = mimetype
        self.metadata = args.get('metadata')

    @classmethod
    def new_from_dict(cls, asset_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(asset_dict)
        url = new_dict.pop('url')
        mimetype = new_dict.pop('mimetype')
        new = cls(url, mimetype, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.url != resource.get('url'):
                return False
            if self.mimetype != resource.get('mimetype'):
                return False
            if self.metadata != resource.get('metadata'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, Asset):
            try:
                if self.url != other.url:
                    return False
                if self.mimetype != other.mimetype:
                    return False
                if self.metadata != other.metadata:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.url, self.mimetype, self.metadata))

    def __str__(self):
        return '%s mimetype %s @ %s' % (self.__class__.__name__,
                self.mimetype, self.url)

class Attribution(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-attribution '''
    def __init__(self, sources, first_acquired):
        self.sources = sources
        self.first_acquired = first_acquired

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['sources'], new_dict['acquired'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.sources != resource.get('sources'):
                return False
            if self.first_acquired != resource.get('first_acquired'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.sources != other.sources:
                    return False
                if self.first_acquired != other.first_acquired:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.sources, self.first_acquired))

    def __str__(self):
        return '%s with %d sources @ %s' % (self.__class__.__name__,
                len(self.sources), self.first_acquired)

class Brand(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-brand '''
    def __init__(self, uid, name, homepage):
        self.uid = uid
        self.name = name
        self.homepage_url = homepage

    @classmethod
    def new_from_dict(cls, brand_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(brand_dict['uid'], brand_dict['name'],
                brand_dict['homepage_url'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""

        if isinstance(resource, dict) and resource.get('__class__') == 'Brand':
            if self.uid != resource.get('uid'):
                return False
            if self.name != resource.get('name'):
                return False
            if self.homepage_url != resource.get('homepage_url'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    return False
                if self.name != other.name:
                    return False
                if self.homepage_url != other.homepage_url:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.name, self.homepage_url))

    def __str__(self):
        return '%s %s (%s) @ %s' % (self.__class__.__name__,
                self.name, self.uid, self.homepage_url)

class BrokerListing(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-brokerlisting
    '''
    def __init__(self, seller, listing_url, octopart_rfq_url):
        self.seller = dict_to_class(seller, Seller)
        self.listing_url = listing_url
        self.octopart_rfq_url = octopart_rfq_url

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['seller'], new_dict['listing_url'],
                new_dict['octopart_rfq_url'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.seller != resource.get('seller'):
                return False
            if self.listing_url != resource.get('listing_url'):
                return False
            if self.octopart_rfq_url != resource.get('octopart_rfq_url'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.seller != other.seller:
                    return False
                if self.listing_url != other.listing_url:
                    return False
                if self.octopart_rfq_url != other.octopart_rfq_url:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.seller, self.listing_url,
            self.octopart_rfq_url))

    def __str__(self):
        return '%s %s @ %s' % (self.__class__.__name__,
                str(self.seller), self.listing_url)

class CADModel(Asset):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-cadmodel '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        url = new_dict.pop('url')
        mimetype = new_dict.pop('mimetype')
        new = cls(url, mimetype, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.url != resource.get('url'):
                return False
            if self.mimetype != resource.get('mimetype'):
                return False
            if self.attribution != resource.get('attribution'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.url != other.url:
                    return False
                if self.mimetype != other.mimetype:
                    return False
                if self.attribution != other.attribution:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.url, self.mimetype, self.attribution))

    def __str__(self):
        return super(self.__class__, self).__str__()

class Category(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-category '''

    def __init__(self, uid, name, parent_uid, children_uids, ancestor_uids,
                 ancestor_names, num_parts, **kwargs):
        args = copy.deepcopy(kwargs)
        self.uid = uid
        self.name = name
        self.parent_uid = parent_uid
        self.children_uids = children_uids
        self.ancestor_uids = ancestor_uids
        self.ancestor_names = ancestor_names
        self.num_parts = num_parts
        self.imagesets = args.get('imagesets', [])

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        uid = new_dict.pop('uid')
        name = new_dict.pop('name')
        parent_uid = new_dict.pop('parent_uid')
        children_uids = new_dict.pop('children_uids')
        ancestor_uids = new_dict.pop('ancestor_uids')
        ancestor_names = new_dict.pop('ancestor_names')
        num_parts = new_dict.pop('num_parts')
        new = cls(uid, name, parent_uid, children_uids, ancestor_uids,
                ancestor_names, num_parts, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON Category resource"""

        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.uid != resource.get('uid'):
                ret = False
            if self.name != resource.get('name'):
                ret = False
            if self.parent_uid != resource.get('parent_uid'):
                ret = False
            if sorted(self.children_uids) != sorted(
                    resource.get('children_uids', [])):
                ret = False
            if sorted(self.ancestor_uids) != sorted(
                    resource.get('ancestor_uids', [])):
                ret = False
            if sorted(self.ancestor_names) != sorted(
                    resource.get('ancestor_names', [])):
                ret = False
            if self.num_parts != resource.get('num_parts'):
                ret = False
            if sorted(self.imagesets) != sorted(resource.get('imagesets', [])):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    ret = False
                if self.name != other.name:
                    ret = False
                if self.parent_uid != other.parent_uid:
                    ret = False
                if sorted(self.children_uids) != sorted(other.children_uids):
                    ret = False
                if sorted(self.ancestor_uids) != sorted(other.ancestor_uids):
                    ret = False
                if sorted(self.ancestor_names) != sorted(other.ancestor_names):
                    ret = False
                if self.num_parts != other.num_parts:
                    ret = False
                if sorted(self.imagesets) != sorted(other.imagesets):
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.name, self.parent_uid,
            self.children_uids, self.ancestor_uids, self.ancestor_names,
            self.num_parts, self.imagesets))

    def __str__(self):
        return '%s %s (%s) containing %d parts, %d children' % (
                self.__class__.__name__, self.name, self.uid, self.num_parts,
                len(self.children_uids))

class ComplianceDocument(Asset):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-compliancedocument
    '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.attribution = dict_to_class(args.get('attribution'), Attribution)
        self.subtypes = args.get('subtypes', [])

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        url = new_dict.pop('url')
        mimetype = new_dict.pop('mimetype')
        new = cls(url, mimetype, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.url != resource.get('url'):
                ret = False
            if self.mimetype != resource.get('mimetype'):
                ret = False
            if self.attribution != resource.get('attribution'):
                ret = False
            if self.subtypes != resource.get('subtypes'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.url != other.url:
                    ret = False
                if self.mimetype != other.mimetype:
                    ret = False
                if self.attribution != other.attribution:
                    ret = False
                if self.subtypes != other.subtypes:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.url, self.mimetype, self.attribution,
            self.subtypes))

    def __str__(self):
        return super(self.__class__, self).__str__()

class Datasheet(Asset):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-datasheet '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        url = new_dict.pop('url')
        mimetype = new_dict.pop('mimetype')
        new = cls(url, mimetype, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.url != resource.get('url'):
                return False
            if self.mimetype != resource.get('mimetype'):
                return False
            if self.attribution != resource.get('attribution'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.url != other.url:
                    return False
                if self.mimetype != other.mimetype:
                    return False
                if self.attribution != other.attribution:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.url, self.mimetype, self.attribution))

    def __str__(self):
        return super(self.__class__, self).__str__()

class Description(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-description'''
    def __init__(self, value, attribution):
        self.value = value
        self.attribution = dict_to_class(attribution, Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['value'], new_dict['attribution'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.value != resource.get('value'):
                return False
            if self.attribution != resource.get('attribution'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.value != other.value:
                    return False
                if self.attribution != other.attribution:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.value, self.attribution))

    def __str__(self):
        return '%s %s (%s)' % (self.__class__.__name__,
                self.value, str(self.attribution))

class ExternaLinks(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-externallinks
    '''
    def __init__(self, product_url, freesample_url, evalkit_url):
        self.product_url = product_url
        self.freesample_url = freesample_url
        self.evalkit_url = evalkit_url

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['product_url'], new_dict['freesample_url'],
                new_dict['evalkit_url'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.product_url != resource.get('product_url'):
                return False
            if self.freesample_url != resource.get('freesample_url'):
                return False
            if self.evalkit_url != resource.get('evalkit_url'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.product_url != other.product_url:
                    return False
                if self.freesample_url != other.freesample_url:
                    return False
                if self.evalkit_url != other.evalkit_url:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.product_url, self.freesample_url,
            self.evalkit_url))

    def __str__(self):
        return '%s %s,%s,%s' % (self.__class__.__name__,
                self.product_url, self.freesample_url, self.evalkit_url)

class ImageSet(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-imageset '''
    def __init__(self, swatch_image, small_image, medium_image, large_image,
                 attribution, credit_string, credit_url):
        self.swatch_image = dict_to_class(swatch_image, Asset)
        self.small_image = dict_to_class(small_image, Asset)
        self.medium_image = dict_to_class(medium_image, Asset)
        self.large_image = dict_to_class(large_image, Asset)
        self.attribution = dict_to_class(attribution, Attribution)
        self.credit_string = credit_string
        self.credit_url = credit_url

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['swatch_image'], new_dict['small_image'],
                new_dict['medium_image'], new_dict['large_image'],
                new_dict['attribution'], new_dict['credit_string'],
                new_dict['credit_url'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.swatch_image != resource.get('swatch_image'):
                ret = False
            if self.medium_image != resource.get('medium_image'):
                ret = False
            if self.large_image != resource.get('large_image'):
                ret = False
            if self.attribution != resource.get('attribution'):
                ret = False
            if self.credit_string != resource.get('credit_string'):
                ret = False
            if self.credit_url != resource.get('credit_url'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.swatch_image != other.swatch_image:
                    ret = False
                if self.medium_image != other.medium_image:
                    ret = False
                if self.large_image != other.large_image:
                    ret = False
                if self.attribution != other.attribution:
                    ret = False
                if self.credit_string != other.credit_string:
                    ret = False
                if self.credit_url != other.credit_url:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.swatch_image, self.medium_image,
            self.large_image, self.attribution, self.credit_string,
            self.credit_url))

    def __str__(self):
        return '%s %s by %s' % (self.__class__.__name__,
                self.swatch_image, self.credit_string)

class Manufacturer(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-manufacturer
    '''
    def __init__(self, uid, name, homepage_url):
        self.uid = uid
        self.name = name
        self.homepage_url = homepage_url

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['uid'], new_dict['name'],
                new_dict['homepage_url'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.uid != resource.get('uid'):
                return False
            if self.name != resource.get('name'):
                return False
            if self.homepage_url != resource.get('homepage_url'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    return False
                if self.name != other.name:
                    return False
                if self.homepage_url != other.homepage_url:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.name, self.homepage_url))

    def __str__(self):
        return '%s %s (%s) @ %s' % (self.__class__.__name__,
                self.name, self.uid, self.homepage_url)

class Part(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-part '''
    @classmethod
    def includes(cls,
                 include_short_description=False,
                 include_datasheets=False,
                 include_compliance_documents=False,
                 include_descriptions=False,
                 include_imagesets=False,
                 include_specs=False,
                 include_category_uids=False,
                 include_external_links=False,
                 include_reference_designs=False,
                 include_cad_models=False):
        ''' Enable optional includes for the parts query '''
        args = {'include[]':[]}
        if include_short_description is True:
            args['include[]'] += ['short_description']
        if include_datasheets is True:
            args['include[]'] += ['datasheets']
        if include_compliance_documents is True:
            args['include[]'] += ['compliante_documents']
        if include_descriptions is True:
            args['include[]'] += ['descriptions']
        if include_imagesets is True:
            args['include[]'] += ['imagesets']
        if include_specs is True:
            args['include[]'] += ['specs']
        if include_category_uids is True:
            args['include[]'] += ['category_uids']
        if include_external_links is True:
            args['include[]'] += ['external_links']
        if include_reference_designs is True:
            args['include[]'] += ['reference_designs']
        if include_cad_models is True:
            args['include[]'] += ['cad_models']
        return args

    @classmethod
    def shows(cls,
              show_uid=False,
              show_mpn=False,
              show_manufacturer=False,
              show_brand=False,
              show_octopart_url=False,
              show_external_links=False,
              show_offers=False,
              show_broker_listings=False,
              show_short_description=False,
              show_descriptions=False,
              show_imagesets=False,
              show_compliance_documents=False,
              show_datasheets=False,
              show_reference_designs=False,
              show_cad_models=False,
              show_specs=False,
              show_category_uids=False):
        ''' Enable optional show fields for the parts query '''
        args = {'show[]':[]}
        if show_uid is True:
            args['show[]'] += ['uid']
        if show_mpn is True:
            args['show[]'] += ['mpn']
        if show_manufacturer is True:
            args['show[]'] += ['manufacturer']
        if show_brand is True:
            args['show[]'] += ['brand']
        if show_octopart_url is True:
            args['show[]'] += ['octopart_url']
        if show_offers is True:
            args['show[]'] += ['offers']
        if show_broker_listings is True:
            args['show[]'] += ['broker_listings']
        if show_short_description is True:
            args['show[]'] += ['short_description']
        if show_datasheets is True:
            args['show[]'] += ['datasheets']
        if show_compliance_documents is True:
            args['show[]'] += ['compliante_documents']
        if show_descriptions is True:
            args['show[]'] += ['descriptions']
        if show_imagesets is True:
            args['show[]'] += ['imagesets']
        if show_specs is True:
            args['show[]'] += ['specs']
        if show_category_uids is True:
            args['show[]'] += ['category_uids']
        if show_external_links is True:
            args['show[]'] += ['external_links']
        if show_reference_designs is True:
            args['show[]'] += ['reference_designs']
        if show_cad_models is True:
            args['show[]'] += ['cad_models']
        return args

    @classmethod
    def hides(cls,
              hide_uid=False,
              hide_mpn=False,
              hide_manufacturer=False,
              hide_brand=False,
              hide_octopart_url=False,
              hide_external_links=False,
              hide_offers=False,
              hide_broker_listings=False,
              hide_short_description=False,
              hide_descriptions=False,
              hide_imagesets=False,
              hide_datasheets=False,
              hide_compliance_documents=False,
              hide_reference_designs=False,
              hide_cad_models=False,
              hide_specs=False,
              hide_category_uids=False):
        args = {'hide[]':[]}
        if hide_uid is True:
            args['hide[]'] += ['uid']
        if hide_mpn is True:
            args['hide[]'] += ['mpn']
        if hide_manufacturer is True:
            args['hide[]'] += ['manufacturer']
        if hide_brand is True:
            args['hide[]'] += ['brand']
        if hide_octopart_url is True:
            args['hide[]'] += ['octopart_url']
        if hide_offers is True:
            args['hide[]'] += ['offers']
        if hide_broker_listings is True:
            args['hide[]'] += ['broker_listings']
        if hide_short_description is True:
            args['hide[]'] += ['short_description']
        if hide_datasheets is True:
            args['hide[]'] += ['datasheets']
        if hide_compliance_documents is True:
            args['hide[]'] += ['compliante_documents']
        if hide_descriptions is True:
            args['hide[]'] += ['descriptions']
        if hide_imagesets is True:
            args['hide[]'] += ['imagesets']
        if hide_specs is True:
            args['hide[]'] += ['specs']
        if hide_category_uids is True:
            args['hide[]'] += ['category_uids']
        if hide_external_links is True:
            args['hide[]'] += ['external_links']
        if hide_reference_designs is True:
            args['hide[]'] += ['reference_designs']
        if hide_cad_models is True:
            args['hide[]'] += ['cad_models']
        return args


    @classmethod
    def new_from_dict(cls, part_dict):
        """Constructor for use with JSON resource dictionaries."""

        copied_dict = part_dict.copy()
        uid = copied_dict.pop('uid')
        mpn = copied_dict.pop('mpn')
        manufacturer = copied_dict.pop('manufacturer')
        return cls(uid, mpn, manufacturer, **copied_dict)

    def __init__(self, uid, mpn, manufacturer, **kwargs):
        # If class data is in dictionary format, convert to class instance
        # Otherwise, assume it is already in class format and do nothing
        self.uid = uid
        self.mpn = mpn
        args = copy.deepcopy(kwargs)
        self.manufacturer = dict_to_class(manufacturer, Manufacturer)
        self.brand = dict_to_class(args.get('brand'), Brand)
        self.external_links = args.get('external_links')
        self.offers = list_to_class(args.get('offers', []), PartOffer)
        self.broker_listings = list_to_class(
                args.get('broker_listings', []), BrokerListing)
        self.short_description = args.get('short_description', '')
        self.descriptions = list_to_class(
                args.get('descriptions', []), Description)
        self.imagesets = list_to_class(args.get('imagesets', []), ImageSet)
        self.datasheets = list_to_class(args.get('datasheets', []), Datasheet)
        self.compliance_documents = list_to_class(
                args.get('compliance_documents', []), ComplianceDocument)
        self.reference_designs = list_to_class(
                args.get('reference_designs', []), ReferenceDesign)
        self.cad_models = list_to_class(args.get('cad_models', []), CADModel)
        self.specs = list_to_class(args.get('specs', []), SpecValue)
        self.category_uids = args.get('category_uids', [])
        # Deprecated from V2 -> V3:
        #self.avg_price = args.get('avg_price')
        #self.avg_avail = args.get('avg_avail')
        #self.market_status = args.get('market_status')
        #self.num_suppliers = args.get('num_suppliers')
        #self.num_authsuppliers = args.get('num_authsuppliers')
        #self.images = args.get('images', [])
        #self.hyperlinks = args.get('hyperlinks', {})

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    ret = False
                if self.mpn != other.mpn:
                    ret = False
                if self.manufacturer != other.manufacturer:
                    ret = False
                if self.brand != other.brand:
                    ret = False
                if self.external_links != other.external_links:
                    ret = False
                if self.offers != other.offers:
                    ret = False
                if self.broker_listings != other.broker_listings:
                    ret = False
                if self.short_description != other.short_description:
                    ret = False
                if self.descriptions != other.descriptions:
                    ret = False
                if self.imagesets != other.imagesets:
                    ret = False
                if self.datasheets != other.datasheets:
                    ret = False
                if self.compliance_documents != other.compliance_documents:
                    ret = False
                if self.reference_designs != other.reference_designs:
                    ret = False
                if self.cad_models != other.cad_models:
                    ret = False
                if self.specs != other.specs:
                    ret = False
                if self.category_uids != other.category_uids:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.mpn, self.manufacturer,
            self.brand, self.external_links, self.offers, self.broker_listings,
            self.short_description, self.descriptions, self.imagesets,
            self.datasheets, self.compliance_documents, self.reference_designs,
            self.cad_models, self.specs, self.category_uids))

    def __str__(self):
        return '%s %s %s (%s)' % (self.__class__.__name__,
                self.manufacturer.name, self.mpn, self.uid)

class PartOffer(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-partoffer '''
    def __init__(self, sku, seller, eligible_region, product_url,
            octopart_rfq_url, prices, in_stock_quantity, on_order_quantity,
            on_order_eta, factory_lead_days, factory_order_multiple,
            order_multiple, moq, packaging, is_authorized, last_updated):
        self.sku = sku
        self.seller = dict_to_class(seller, Seller)
        self.eligible_region = eligible_region
        self.product_url = product_url
        self.octopart_rfq_url = octopart_rfq_url
        self.prices = prices
        self.in_stock_quantity = in_stock_quantity
        self.on_order_quantity = on_order_quantity
        self.on_order_eta = on_order_eta
        self.factory_lead_days = factory_lead_days
        self.factory_order_multiple = factory_order_multiple
        self.order_multiple = order_multiple
        self.moq = moq
        self.packaging = packaging
        self.is_authorized = is_authorized
        self.last_updated = last_updated

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['sku'], new_dict['seller'],
                new_dict['eligible_region'], new_dict['product_url'],
                new_dict['octopart_rfq_url'], new_dict['prices'],
                new_dict['in_stock_quantity'], new_dict['on_order_quantity'],
                new_dict['on_order_eta'], new_dict['factory_lead_days'],
                new_dict['factory_order_multiple'], new_dict['order_multiple'],
                new_dict['moq'], new_dict['packaging'],
                new_dict['is_authorized'], new_dict['last_updated'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.sku != resource.get('sku'):
                ret = False
            if self.seller != resource.get('seller'):
                ret = False
            if self.eligible_region != resource.get('eligible_region'):
                ret = False
            if self.product_url != resource.get('product_url'):
                ret = False
            if self.octopart_rfq_url != resource.get('octopart_rfq_url'):
                ret = False
            if self.prices != resource.get('prices'):
                ret = False
            if self.in_stock_quantity != resource.get('in_stock_quantity'):
                ret = False
            if self.on_order_quantity != resource.get('on_order_quantity'):
                ret = False
            if self.on_order_eta != resource.get('on_order_eta'):
                ret = False
            if self.factory_lead_days != resource.get('factory_lead_days'):
                ret = False
            if self.factory_order_multiple != resource.get('factory_order_multiple'):
                ret = False
            if self.order_multiple != resource.get('order_multiple'):
                ret = False
            if self.moq != resource.get('moq'):
                ret = False
            if self.packaging != resource.get('packaging'):
                ret = False
            if self.is_authorized != resource.get('is_authorized'):
                ret = False
            if self.last_updated != resource.get('last_updated'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.sku != other.sku:
                    ret = False
                if self.seller != other.seller:
                    ret = False
                if self.eligible_region != other.eligible_region:
                    ret = False
                if self.product_url != other.product_url:
                    ret = False
                if self.octopart_rfq_url != other.octopart_rfq_url:
                    ret = False
                if self.prices != other.prices:
                    ret = False
                if self.in_stock_quantity != other.in_stock_quantity:
                    ret = False
                if self.on_order_quantity != other.on_order_quantity:
                    ret = False
                if self.on_order_eta != other.on_order_eta:
                    ret = False
                if self.factory_lead_days != other.factory_lead_days:
                    ret = False
                if self.factory_order_multiple != other.factory_order_multiple:
                    ret = False
                if self.order_multiple != other.order_multiple:
                    ret = False
                if self.moq != other.moq:
                    ret = False
                if self.packaging != other.packaging:
                    ret = False
                if self.is_authorized != other.is_authorized:
                    ret = False
                if self.last_updated != other.last_updated:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.sku, self.seller,
            self.eligible_region, self.product_url, self.octopart_rfq_url,
            self.prices, self.in_stock_quantity, self.on_order_quantity,
            self.on_order_eta, self.factory_lead_days,
            self.factory_order_multiple, self.order_multiple, self.moq,
            self.packaging, self.is_authorized, self.last_updated))

    def __str__(self):
        # Attempt to find the maximum and minimum price
        # To avoid making a smart decision about currency type, pick the first!
        minval = -1.0
        maxval = -1.0
        unit = ""
        if len(self.prices) > 0 and len(self.prices[self.prices.keys()[0]]) > 0:
            unit = self.prices.keys()[0]
            minval = float(self.prices[unit][-1][1])
            maxval = float(self.prices[unit][0][1])

        if minval == maxval:
            return '%s from %s for %s: %f %s with %d avail'% (
                    self.__class__.__name__, self.seller.name, self.sku,
                    minval, unit, self.in_stock_quantity)
        return '%s from %s for %s: %f-%f %s with %d avail' % (
                self.__class__.__name__, self.seller.name, self.sku,
                minval, maxval, unit, self.in_stock_quantity)

class SpecValue(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-specvalue '''
    def __init__(self, value, display_value, **kwargs):
        args = copy.deepcopy(kwargs)
        self.value = value
        self.display_value = display_value
        self.min_value = args.get('min_value')
        self.max_value = args.get('max_value')
        self.metadata = args.get('metadata')
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        value = new_dict.pop('value')
        display_value = new_dict.pop('display_value')
        new = cls(value, display_value, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.value != resource.get('value'):
                ret = False
            if self.display_value != resource.get('display_value'):
                ret = False
            if self.min_value != resource.get('min_value'):
                ret = False
            if self.max_value != resource.get('max_value'):
                ret = False
            if self.metadata != resource.get('metadata'):
                ret = False
            if self.attribution != resource.get('attribution'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.value != other.value:
                    ret = False
                if self.display_value != other.display_value:
                    ret = False
                if self.min_value != other.min_value:
                    ret = False
                if self.max_value != other.max_value:
                    ret = False
                if self.metadata != other.metadata:
                    ret = False
                if self.attribution != other.attribution:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.value, self.display_value,
            self.min_value, self.max_value, self.metadata, self.attribution))

    def __str__(self):
        if self.min_value or self.max_value is None:
            return '%s %s (%s)' % (self.__class__.__name__,
                    self.display_value, str(self.attribution))
        return '%s %s (%s-%s) (%s)' % (self.__class__.__name__,
                self.display_value, self.min_value, self.max_value,
                str(self.attribution))

class ReferenceDesign(Asset):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-referencedesign
    '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.title = args.get('title')
        self.description = args.get('description')
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        url = new_dict.pop('url')
        mimetype = new_dict.pop('mimetype')
        new = cls(url, mimetype, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.url != resource.get('url'):
                ret = False
            if self.mimetype != resource.get('mimetype'):
                ret = False
            if self.attribution != resource.get('attribution'):
                ret = False
            if self.description != resource.get('description'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.url != other.url:
                    ret = False
                if self.mimetype != other.mimetype:
                    ret = False
                if self.attribution != other.attribution:
                    ret = False
                if self.description != other.description:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.url, self.mimetype, self.attribution,
            self.description))

    def __str__(self):
        return super(self.__class__, self).__str__()

class Seller(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-seller '''
    def __init__(self, uid, name, homepage_url, display_flag, has_ecommerce):
        self.uid = uid
        self.name = name
        self.homepage_url = homepage_url
        self.display_flag = display_flag
        self.has_ecommerce = has_ecommerce

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['uid'], new_dict['name'],
                new_dict['homepage_url'], new_dict['display_flag'],
                new_dict['has_ecommerce'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.uid != resource.get('uid'):
                ret = False
            if self.name != resource.get('name'):
                ret = False
            if self.homepage_url != resource.get('homepage_url'):
                ret = False
            if self.display_flag != resource.get('display_flag'):
                ret = False
            if self.has_ecommerce != resource.get('has_ecommerce'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    ret = False
                if self.name != other.name:
                    ret = False
                if self.homepage_url != other.homepage_url:
                    ret = False
                if self.display_flag != other.display_flag:
                    ret = False
                if self.has_ecommerce != other.has_ecommerce:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.name, self.homepage_url,
            self.display_flag, self.has_ecommerce))

    def __str__(self):
        return '%s %s (%s) @ %s' % (self.__class__.__name__,
                self.name, self.uid, self.homepage_url)

class Source(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-source '''
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['uid'], new_dict['name'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.uid != resource.get('uid'):
                return False
            if self.name != resource.get('name'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.uid != other.uid:
                    return False
                if self.name != other.name:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.uid, self.name))

    def __str__(self):
        return '%s %s (%s)' % (self.__class__.__name__,
                self.name, self.uid)

class SpecMetadata(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-specmetadata
    '''
    def __init__(self, key, name, datatype, unit):
        self.key = key
        self.name = name
        if not inspect.isclass(datatype):
            if datatype == 'string':
                datatype = str
            elif datatype == 'integer':
                datatype = int
            elif datatype == 'decimal':
                datatype = float
        self.datatype = datatype
        self.unit = dict_to_class(unit, UnitOfMeasurement)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['key'], new_dict['name'],
                new_dict['datatype'], new_dict['unit'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.key != resource.get('key'):
                ret = False
            if self.name != resource.get('name'):
                ret = False
            if self.datatype != resource.get('datatype'):
                ret = False
            if self.unit != resource.get('unit'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.key != other.key:
                    ret = False
                if self.name != other.name:
                    ret = False
                if self.datatype != other.datatype:
                    ret = False
                if self.unit != other.unit:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.key, self.name, self.datatype,
            self.unit))

    def __str__(self):
        return '%s %s %s %s' % (self.__class__.__name__,
                self.name, self.unit.name, str(self.datatype))

class UnitOfMeasurement(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#object-schemas-unitofmeasurement
    '''
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['name'], new_dict['symbol'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.name != resource.get('name'):
                return False
            if self.symbol != resource.get('symbol'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.name != other.name:
                    return False
                if self.symbol != other.symbol:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.name, self.symbol))

    def __str__(self):
        return '%s %s (%s)' % (self.__class__.__name__,
                self.symbol, self.name)

# Response Schemas

class PartsMatchRequest(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-partsmatchrequest
    '''
    def __init__(self, queries, exact_only):
        self.queries = list_to_class(queries, PartsMatchQuery)
        self.exact_only = exact_only

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['queries'], new_dict['exact_only'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.queries != resource.get('queries'):
                return False
            if self.exact_only != resource.get('exact_only'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.queries != other.queries:
                    return False
                if self.exact_only != other.exact_only:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.queries, self.exact_only))

    def __str__(self):
        return '%s with %d queries, exact_only %s' % (self.__class__.__name__,
                len(self.queries), str(self.exact_only))

class PartsMatchQuery(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-partsmatchquery
    '''
    # pylint: disable=invalid-name
    def __init__(self, q, mpn, brand, sku, seller, mpn_or_sku,
            start, limit, reference):
        self.q = q
        self.mpn = mpn
        self.brand = brand
        self.sku = sku
        self.seller = seller
        self.mpn_or_sku = mpn_or_sku
        self.start = start
        self.limit = limit
        self.reference = reference

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['q'], new_dict['mpn'],
                new_dict['brand'], new_dict['sku'],
                new_dict['seller'], new_dict['mpn_or_sku'],
                new_dict['start'], new_dict['limit'],
                new_dict['reference'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.q != resource.get('q'):
                ret = False
            if self.mpn != resource.get('mpn'):
                ret = False
            if self.brand != resource.get('brand'):
                ret = False
            if self.sku != resource.get('sku'):
                ret = False
            if self.seller != resource.get('seller'):
                ret = False
            if self.mpn_or_sku != resource.get('mpn_or_sku'):
                ret = False
            if self.start != resource.get('start'):
                ret = False
            if self.limit != resource.get('limit'):
                ret = False
            if self.reference != resource.get('reference'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.q != other.q:
                    ret = False
                if self.mpn != other.mpn:
                    ret = False
                if self.brand != other.brand:
                    ret = False
                if self.sku != other.sku:
                    ret = False
                if self.seller != other.seller:
                    ret = False
                if self.mpn_or_sku != other.mpn_or_sku:
                    ret = False
                if self.start != other.start:
                    ret = False
                if self.limit != other.limit:
                    ret = False
                if self.reference != other.reference:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.q, self.mpn, self.brand, self.sku,
            self.seller, self.mpn_or_sku, self.start, self.limit,
            self.reference))

    def __str__(self):
        ret = ""
        if self.reference is not None and self.reference is not "":
            ret += " ref="+self.reference
        if self.q is not None and self.q is not "":
            ret += " query="+self.q
        if self.mpn is not None and self.mpn is not "":
            ret += " mpn="+self.mpn
        if self.brand is not None and self.brand is not "":
            ret += " brand="+self.brand
        if self.sku is not None and self.sku is not "":
            ret += " sku="+self.sku
        if self.seller is not None and self.seller is not "":
            ret += " seller="+self.seller
        if self.mpn_or_sku is not None and self.mpn_or_sku is not "":
            ret += " mpn_or_sku="+self.mpn_or_sku
        if self.start is not None:
            ret += " start="+str(self.start)
        if self.limit is not None:
            ret += " limit="+str(self.limit)
        return '%s %s' % (self.__class__.__name__, ret)

class PartsMatchResponse(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-partsmatchresponse
    '''
    def __init__(self, request, results, msec):
        self.request = dict_to_class(request, PartsMatchRequest)
        self.results = list_to_class(results, PartsMatchResult)
        self.msec = msec

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['request'], new_dict['results'],
                new_dict['msec'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.request != resource.get('request'):
                return False
            if self.results != resource.get('results'):
                return False
            if self.msec != resource.get('msec'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.request != other.request:
                    return False
                if self.results != other.results:
                    return False
                if self.msec != other.msec:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.request, self.results, self.msec))

    def __str__(self):
        return '%s completed in %d ms, %d results' % (
                self.__class__.__name__, self.msec, len(self.results))

class PartsMatchResult(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-partsmatchresult
    '''
    def __init__(self, items, hits, **kwargs):
        args = copy.deepcopy(kwargs)
        self.items = list_to_class(items, Part)
        self.hits = hits
        self.reference = args.get('reference')
        self.error = args.get('error')

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        items = new_dict.pop('items')
        hits = new_dict.pop('hits')
        new = cls(items, hits, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.items != resource.get('items'):
                ret = False
            if self.hits != resource.get('hits'):
                ret = False
            if self.reference != resource.get('reference'):
                ret = False
            if self.error != resource.get('error'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.items != other.items:
                    ret = False
                if self.hits != other.hits:
                    ret = False
                if self.reference != other.reference:
                    ret = False
                if self.error != other.error:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.items, self.hits, self.reference,
            self.error))

    def __str__(self):
        if self.error is not None:
            return '%s containing %d items' % (
                    self.__class__.__name__, self.hits)
        return '%s error %s' % (
                self.__class__.__name__, self.error)

class SearchRequest(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-searchrequest
    '''
    # pylint: disable=invalid-name
    def __init__(self, q, start, limit, sortby, **kwargs):
        args = copy.deepcopy(kwargs)
        self.q = q
        self.start = start
        self.limit = limit
        self.sortby = sortby
        self.filter = args.get('filter')
        self.facet = args.get('facet')
        self.stats = args.get('stats')

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        q = new_dict.pop('q')
        start = new_dict.pop('start')
        limit = new_dict.pop('limit')
        sortby = new_dict.pop('sortby')
        new = cls(q, start, limit, sortby, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.q != resource.get('q'):
                ret = False
            if self.start != resource.get('start'):
                ret = False
            if self.limit != resource.get('limit'):
                ret = False
            if self.sortby != resource.get('sortby'):
                ret = False
            if self.filter != resource.get('filter'):
                ret = False
            if self.facet != resource.get('facet'):
                ret = False
            if self.stats != resource.get('stats'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.q != other.q:
                    ret = False
                if self.start != other.start:
                    ret = False
                if self.limit != other.limit:
                    ret = False
                if self.sortby != other.sortby:
                    ret = False
                if self.filter != other.filter:
                    ret = False
                if self.facet != other.facet:
                    ret = False
                if self.stats != other.stats:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.q, self.start, self.limit,
            self.sortby, self.filter, self.facet, self.stats))

    def __str__(self):
        return '%s: %s' % (
                self.__class__.__name__, str(self.q))

class SearchResponse(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-searchresponse
    '''
    def __init__(self, request, results, hits, msec, **kwargs):
        args = copy.deepcopy(kwargs)
        self.request = dict_to_class(request, SearchRequest)
        self.results = list_to_class(results, SearchResult)
        self.hits = hits
        self.msec = msec
        self.facet_results = args.get('facet_results')
        # XXX This doesn't appear to be a SearchFacetResult!
        # Unsure of which object in the schema to use...
        #self.facet_results = list_to_class(
        #        args.get('facet_results'), SearchFacetResult)
        self.stats_results = list_to_class(
                args.get('stats_results'), SearchStatsResult)
        self.spec_metadata = args.get('spec_metadata')

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new_dict = copy.deepcopy(new_dict)
        request = new_dict.pop('request')
        results = new_dict.pop('results')
        hits = new_dict.pop('hits')
        msec = new_dict.pop('msec')
        new = cls(request, results, hits, msec, **new_dict)
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.request != resource.get('request'):
                ret = False
            if self.results != resource.get('results'):
                ret = False
            if self.hits != resource.get('hits'):
                ret = False
            if self.msec != resource.get('msec'):
                ret = False
            if self.facet_results != resource.get('facet_results'):
                ret = False
            if self.stats_results != resource.get('stats_results'):
                ret = False
            if self.spec_metadata != resource.get('spec_metadata'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.request != other.request:
                    ret = False
                if self.results != other.results:
                    ret = False
                if self.hits != other.hits:
                    ret = False
                if self.msec != other.msec:
                    ret = False
                if self.facet_results != other.facet_results:
                    ret = False
                if self.stats_results != other.stats_results:
                    ret = False
                if self.spec_metadata != other.spec_metadata:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.request, self.results, self.hits,
            self.msec, self.facet_results, self.stats_results,
            self.spec_metadata))

    def __str__(self):
        return '%s completed in %d ms, %d hits' % (
                self.__class__.__name__, self.msec, self.hits)

class SearchResult(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-searchresult
    '''
    def __init__(self, item):
        # XXX HACK: We need to implement dynamic object instantiation
        # This could be any type of object.
        self.item = dict_to_class(item, Part)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['item'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.item != resource.get('item'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.item != other.item:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.item))

    def __str__(self):
        return self.item.__str__()


class SearchFacetResult(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-searchfacetresult
    '''
    def __init__(self, facets, missing, spec_drilldown_rank):
        self.facets = facets
        self.missing = missing
        self.spec_drilldown_rank = spec_drilldown_rank

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['facets'], new_dict['missing'],
                new_dict['spec_drilldown_rank'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.facets != resource.get('facets'):
                return False
            if self.missing != resource.get('missing'):
                return False
            if self.spec_drilldown_rank != resource.get('spec_drilldown_rank'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.facets != other.facets:
                    return False
                if self.missing != other.missing:
                    return False
                if self.spec_drilldown_rank != other.spec_drilldown_rank:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.facets, self.missing,
            self.spec_drilldown_rank))

    def __str__(self):
        return '%s with %d facets, %d missing, rank %d' % (
                self.__class__.__name__, len(self.facets), self.missing,
                self.spec_drilldown_rank)

class SearchStatsResult(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#response-schemas-searchstatsresult
    '''
    def __init__(self, min, max, mean, stddev, count, missing, spec_drilldown_rank):
        self.min = min
        self.max = max
        self.mean = mean
        self.stddev = stddev
        self.count = count
        self.missing = missing
        self.spec_drilldown_rank = spec_drilldown_rank

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['min'], new_dict['max'],
                new_dict['mean'], new_dict['stddev'],
                new_dict['count'], new_dict['missing'],
                new_dict['spec_drilldown_rank'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        ret = True
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.min != resource.get('min'):
                ret = False
            if self.max != resource.get('max'):
                ret = False
            if self.mean != resource.get('mean'):
                ret = False
            if self.stddev != resource.get('stddev'):
                ret = False
            if self.count != resource.get('count'):
                ret = False
            if self.missing != resource.get('missing'):
                ret = False
            if self.spec_drilldown_rank != resource.get('spec_drilldown_rank'):
                ret = False
        else:
            ret = False
        return ret

    def __eq__(self, other):
        ret = True
        if isinstance(other, self.__class__):
            try:
                if self.min != other.min:
                    ret = False
                if self.max != other.max:
                    ret = False
                if self.mean != other.mean:
                    ret = False
                if self.stddev != other.stddev:
                    ret = False
                if self.count != other.count:
                    ret = False
                if self.missing != other.missing:
                    ret = False
                if self.spec_drilldown_rank != other.spec_drilldown_rank:
                    ret = False
            except AttributeError:
                ret = False
        else:
            ret = False
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.min, self.max, self.mean,
            self.stddev, self.count, self.missing, self.spec_drilldown_rank))

    def __str__(self):
        return '%s %d/%d results: mean %d, min %d, max %d, stddev %d' % (
                self.__class__.__name__, self.count, self.count+self.missing,
                self.mean, self.min, self.max, self.stddev)

# Error schemas

class ClientErrorResponse(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#error-schemas-clienterrorresponse
    '''
    def __init__(self, message):
        self.message = message

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['message'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.message != resource.get('message'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.message != other.message:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.message))

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.message)

class ServerErrorResponse(object):
    '''
    https://octopart.com/api/docs/v3/rest-api#error-schemas-servererrorresponse
    '''
    def __init__(self, message):
        self.message = message

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        new = cls(new_dict['message'])
        return new

    def equals_json(self, resource):
        """Checks the object for data equivalence to a JSON resource."""
        if isinstance(resource, dict) and\
                resource.get('__class__') == self.__class__.__name__:
            if self.message != resource.get('message'):
                return False
        else:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                if self.message != other.message:
                    return False
            except AttributeError:
                return False
        else:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.message))

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.message)

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
            return json_obj, json_obj['results']
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
            return json_obj, json_obj['results']
        else:
            return None

    def parts_get(self, uid):
        '''
        https://octopart.com/api/docs/v3/rest-api#endpoints-parts-get
        '''
        method = 'parts/{:d}'.format(uid)

        json_obj = self._get_data(method, {}, ver=3)

        if json_obj:
            return json_obj, json_obj['results']
        else:
            return None

