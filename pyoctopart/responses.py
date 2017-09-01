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
from pyoctopart.util import Curry, select, dict_to_class, list_to_class
from pyoctopart.objects import Part

#from .exceptions import ArgumentMissingError
#from .exceptions import ArgumentInvalidError
from .exceptions import TypeArgumentError


select_incls = Curry(select, 'include_')
select_shows = Curry(select, 'show_')
select_hides = Curry(select, 'hide_')

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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
