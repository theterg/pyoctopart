# pyoctopart

A simple Python client frontend to the Octopart public REST API.

For detailed API documentation, refer to the [Octopart APIv3 documentation](https://octopart.com/api/docs/v3/rest-api)

This is a fork of [guyzmo](https://github.com/guyzmo/pyoctopart)'s work, which is in turn a fork of [Joe Baker](https://github.com/jbaker0428/Python-Octopart-API)'s work.

This fork should be compatible with both python 2 and python 3, at least that is the aim.

## Usage

### Install

just do:

    python setup.py install

and it'll be available from your python REPL:

    % python
    >>> from pyoctopart.octopart import Octopart, SearchResponse
    >>> o = Octopart.api(apikey="yourapikey")
    
As a short example, this will search for all parts that match MPN SN74S74N and will fully recreate a structure of APIv3 objects (WIP):

    >>> response = o.parts_search('SN74S74N')
    >>> for result in response.results:
    >>> print str(result)
    >>>     for offer in result.item.offers:
    >>>         print "\t"+str(offer)
    
    Part Texas Instruments SN74S74NSR (721abb1d3046addd)
        PartOffer from Digi-Key for SN74S74NSR-ND: 0.742500 USD with 0 avail
        PartOffer from Avnet for SN74S74NSR: 0.690090-0.798260 USD with 0 avail
        PartOffer from Quest for SN74S74NSR: -1.000000  with 0 avail
    Part Texas Instruments SN74S74NS (88de411ca1685719)
        PartOffer from Rochester Electronics for SN74S74NS: 1.470000-1.810000 USD with 7900 avail
        PartOffer from Avnet for SN74S74NS: 1.254710-1.451380 USD with 0 avail
    Part Texas Instruments SN74S74NSLE (46798f4fc68b99be)
        PartOffer from Rochester Electronics for SN74S74NSLE: 0.250000-0.310000 USD with 1000 avail
        PartOffer from Avnet for SN74S74NSLE: 0.426600-0.493470 USD with 0 avail
    Part Texas Instruments SN74S74NSRG4 (4bbb82dd2598947c)
    Part Texas Instruments SN74S74NSRE4 (3eacf7ab7857e16b)
    Part Texas Instruments SN74S74NSL (2f72e68b83a4f0b5)

when the lib will be considered stable enough, I'll upload it to [pipy](https://pypi.python.org/pypi?:action=pkg_edit&name=pyoctopart):

    % pip install pyoctopart

### Develop

if you just want to develop, you can do:

    % buildout

which will download dependencies and deploy a python command in `bin/`:

    % bin/python3
    >>> from pyoctopart.octopart import Octopart
    >>> o = Octopart.api(apikey="yourapikey")
    
You can run regression tests using:

    % bin/test

## Notes

### API v3 conversion

All objects have been ported over the API v3 - Support for API v2 has been discontinuied.

### method/argument syntax

A number of arguments in the v3 API are using syntax that are not compatible with
python's syntax, such as `include[]=datasheets`. To enforce argument's type checking
and stay compatible with the API, the arguments are converted as booleans replacing
the assignment with an underscore, making it `include_datasheets`, so for the `Part`
model you have the following matches:

### includes

        include_short_description     → include[]=short_description
        include_datasheets            → include[]=datasheets
        include_compliance_documents  → include[]=compliante_documents
        include_descriptions          → include[]=descriptions
        include_imagesets             → include[]=imagesets
        include_specs                 → include[]=specs
        include_category_uids         → include[]=category_uids
        include_external_links        → include[]=external_links
        include_reference_designs     → include[]=reference_designs
        include_cad_models            → include[]=cad_models

### Shows

        show_uid                      → show[]=uid
        show_mpn                      → show[]=mpn
        show_manufacturer             → show[]=manufacturer
        show_brand                    → show[]=brand
        show_octopart_url             → show[]=octopart_url
        show_offers                   → show[]=offers
        show_broker_listings          → show[]=broker_listings
        show_short_description        → show[]=short_description
        show_datasheets               → show[]=datasheets
        show_compliance_documents     → show[]=compliante_documents
        show_descriptions             → show[]=descriptions
        show_imagesets                → show[]=imagesets
        show_specs                    → show[]=specs
        show_category_uids            → show[]=category_uids
        show_external_links           → show[]=external_links
        show_reference_designs        → show[]=reference_designs
        show_cad_models               → show[]=cad_models

### Hides

        hide_uid                      → hide[]=uid
        hide_mpn                      → hide[]=mpn
        hide_manufacturer             → hide[]=manufacturer
        hide_brand                    → hide[]=brand
        hide_octopart_url             → hide[]=octopart_url
        hide_offers                   → hide[]=offers
        hide_broker_listings          → hide[]=broker_listings
        hide_short_description        → hide[]=short_description
        hide_datasheets               → hide[]=datasheets
        hide_compliance_documents     → hide[]=compliante_documents
        hide_descriptions             → hide[]=descriptions
        hide_imagesets                → hide[]=imagesets
        hide_specs                    → hide[]=specs
        hide_category_uids            → hide[]=category_uids
        hide_external_links           → hide[]=external_links
        hide_reference_designs        → hide[]=reference_designs
        hide_cad_models               → hide[]=cad_models

As a reference, check the [include/show/hide directives sections of the manual][0].

[0]:https://octopart.com/api/docs/v3/rest-api#include-directives

## Authors

 * Forked by Andrew Tergis <theterg at gmail dot com>
 * Forked by Bernard `Guyzmo` Pratz <octopart at m0g.net>
 * Originally authored by Joe Baker <jbaker at alum.wpi.edu>

## License

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


