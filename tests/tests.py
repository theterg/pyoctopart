"""
NOTE: Running this unit test generates 24 API requests.
"""

import os
import unittest
import requests
import json

import logging
log = logging.getLogger('test_pyoctopart')

from nose.tools import istest
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_dict_equal
from nose.tools import assert_list_equal
from nose.tools import assert_raises
from nose.tools import raises

import pyoctopart.octopart
from pyoctopart.octopart import *

class DataEquivalenceTest(unittest.TestCase):

    def setUp(self):
        self.api = Octopart(apikey='92bdca1b')

    def test_categories_get(self):
        categories_get_ref = requests.get('http://octopart.com/api/v2/categories/get?id=4174&apikey=92bdca1b').json()
        json_obj, category = self.api.categories_get(4174)
        assert json_obj is not None
        assert json_obj == categories_get_ref
        assert isinstance(category, OctopartCategory)
        assert(category.equals_json(categories_get_ref))

    def test_categories_get_multi(self):
        categories_get_multi_ref = requests.get('http://octopart.com/api/v2/categories/get_multi?ids=[4215,4174,4780]&apikey=92bdca1b').json()
        json_obj, categories = self.api.categories_get_multi([4215,4174,4780])
        assert json_obj is not None
        assert json_obj == categories_get_multi_ref
        for category in categories:
            assert isinstance(category, OctopartCategory)
            truth = [category.equals_json(x) for x in categories_get_multi_ref]
            assert True in truth
            assert truth.count(True) == 1

    def test_categories_search(self):
        categories_search_ref = requests.get('http://octopart.com/api/v2/categories/search?q=resistor&apikey=92bdca1b').json()
        json_obj, categories = self.api.categories_search(q='resistor')
        assert json_obj is not None
        assert json_obj == categories_search_ref
        for category in categories:
            assert isinstance(category[0], OctopartCategory)
            truth = [category[0].equals_json(x['item']) for x in categories_search_ref['results']]
            assert True in truth
            assert truth.count(True) == 1

    def test_parts_get(self):
        parts_get_ref = requests.get('http://octopart.com/api/v2/parts/get?uid=39619421&apikey=92bdca1b').json()
        json_obj, part = self.api.parts_get(39619421)
        assert json_obj is not None
        #assert_dict_equal(json_obj, parts_get_ref) # XXX
        assert isinstance(part, OctopartPart)
        #assert(part.equals_json(parts_get_ref)) # XXX

    def test_parts_get_multi(self):
        parts_get_multi_ref = requests.get('http://octopart.com/api/v2/parts/get_multi?uids=[39619421,29035751,31119928]&apikey=92bdca1b').json()
        json_obj, parts = self.api.parts_get_multi([39619421,29035751,31119928])
        assert json_obj is not None
        #assert_dict_equal(json_obj, parts_get_multi_ref) # XXX
        for part in parts:
            assert isinstance(part, OctopartPart)
            #truth = [part.equals_json(p) for p in parts_get_multi_ref] # XXX
            #assert True in truth
            #assert truth.count(True) == 1

    def test_parts_search(self):
        parts_search_ref = requests.get('http://octopart.com/api/v2/parts/search?q=resistor&limit=10&apikey=92bdca1b').json()
        json_obj, parts = self.api.parts_search(q='resistor', limit=10)
        assert json_obj is not None
        #assert_dict_equal(json_obj, parts_search_ref) # XXX
        for part, highlight in parts:
            assert isinstance(part, OctopartPart)
            assert True in [highlight == r['highlight'] for r in parts_search_ref['results']]
            #truth = [part.equals_json(r['item']) for r in parts_search_ref['results']] # XXX
            # assert True in truth
            # assert truth.count(True) == 1

    def test_parts_suggest(self):
        parts_suggest_ref = requests.get('http://octopart.com/api/v2/parts/suggest?q=sn74f&limit=3&apikey=92bdca1b').json()
        json_obj, results = self.api.parts_suggest(q='sn74f', limit=3)
        assert json_obj is not None
        del json_obj['time']
        del parts_suggest_ref['time']
        assert_dict_equal(json_obj, parts_suggest_ref)
        assert json_obj['results'] == results

    def test_parts_match(self):
        parts_match_ref = requests.get('http://octopart.com/api/v2/parts/match', params=dict(manufacturer_name='texas instruments',
                                                                                             mpn='SN74LS240',
                                                                                             apikey='92bdca1b')).json()
        json_obj = self.api.parts_match(manufacturer_name='texas instruments', mpn='SN74LS240')
        print(type(json_obj), type(parts_match_ref))
        assert json_obj is not None
        assert_list_equal(json_obj, parts_match_ref)

    def test_partattributes_get(self):
        partattributes_get_ref = requests.get('http://octopart.com/api/v2/partattributes/get?fieldname=capacitance&apikey=92bdca1b').json()
        json_obj, attrib = self.api.partattributes_get('capacitance')
        assert json_obj is not None
        assert json_obj == partattributes_get_ref
        assert isinstance(attrib, OctopartPartAttribute)
        assert attrib.equals_json(json_obj) # XXX

    def test_partattributes_get_multi(self):
        partattributes_get_multi_ref = requests.get('http://octopart.com/api/v2/partattributes/get_multi?fieldnames=["capacitance","resistance"]&apikey=92bdca1b').json()
        json_obj, attribs = self.api.partattributes_get_multi(['capacitance', 'resistance'])
        assert json_obj is not None
        assert json_obj == partattributes_get_multi_ref
        for attrib in attribs:
            assert isinstance(attrib, OctopartPartAttribute)
            assert True in [attrib.equals_json(a) for a in json_obj]

    def test_bom_match(self):
        bom_match_ref = requests.get('http://octopart.com/api/v2/bom/match',
                                     params={'lines': json.dumps([
                                         {'mpn': 'SN74LS240N',  'manufacturer': 'Texas Instruments'},
                                         {'mpn': 'RB-220-07A R','manufacturer': 'C&K Components'}
                                     ]), 'apikey': '92bdca1b'}
                                     ).json()
        json_obj, results = self.api.bom_match(lines=[
            {'mpn':'SN74LS240N', 'manufacturer':'Texas Instruments'},
            {'mpn':'RB-220-07A R','manufacturer':'C&K Components'}
        ])
        assert json_obj is not None
    #    assert_dict_equal(json_obj, bom_match_ref)

        for result in results:
            if result.get('hits') is not None:    # Not in API docs, but exists
                assert result['hits'] == len(result['items'])
            assert result['status'] == json_obj['results'][results.index(result)]['status']
            assert result['reference'] == json_obj['results'][results.index(result)]['reference']
            for part in result['items']:
                assert isinstance(part, OctopartPart)
                #assert part.equals_json(json_obj['results'][results.index(result)]['items'][result['items'].index(part)]) # XXX

    def test_brand(self):
        brand = OctopartBrand(459, "Digi-Key", "http://www.digikey.com")

if __name__ == '__main__':
    unittest.main()

