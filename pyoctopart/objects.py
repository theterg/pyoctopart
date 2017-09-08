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

import copy
import inspect
from pyoctopart.util import Curry, select
from pyoctopart.util import dict_to_class,list_to_class, api_object
from .exceptions import TypeArgumentError


select_incls = Curry(select, 'include_')
select_shows = Curry(select, 'show_')
select_hides = Curry(select, 'hide_')


# Octopart Data maps

@api_object
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
        if asset_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                asset_dict['__class__'], cls.__name__))
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

@api_object
class Attribution(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-attribution '''
    def __init__(self, sources, first_acquired):
        self.sources = sources
        self.first_acquired = first_acquired

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
class Brand(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-brand '''
    def __init__(self, uid, name, homepage):
        self.uid = uid
        self.name = name
        self.homepage_url = homepage

    @classmethod
    def new_from_dict(cls, brand_dict):
        """Constructor for use with JSON resource dictionaries."""
        if brand_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                brand_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
class CADModel(Asset):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-cadmodel '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
class Datasheet(Asset):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-datasheet '''
    def __init__(self, url, mimetype, **kwargs):
        super(self.__class__, self).__init__(url, mimetype, **kwargs)
        args = copy.deepcopy(kwargs)
        self.attribution = dict_to_class(args.get('attribution'), Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
class Description(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-description'''
    def __init__(self, value, attribution):
        self.value = value
        self.attribution = dict_to_class(attribution, Attribution)

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if part_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                part_dict['__class__'], cls.__name__))

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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
class Source(object):
    ''' https://octopart.com/api/docs/v3/rest-api#object-schemas-source '''
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

    @classmethod
    def new_from_dict(cls, new_dict):
        """Constructor for use with JSON resource dictionaries."""
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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

@api_object
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
