# pyoctopart

A simple Python client frontend to the Octopart public REST API.

For detailed API documentation, refer to the [Octopart APIv2 documentation](https://octopart.com/api/docs/v2/rest-api)

This is a fork of [Joe Baker](https://github.com/jbaker0428/Python-Octopart-API)'s work, and this fork is *incompatible* with Python 2 distributions!

You'll find the sources of this project over https://github.com/guyzmo/pyoctopart

## Usage

### Install

just do:

    python3 setup.py install

and it'll be available from your python REPL:

    % python3
    >>> from pyoctopart.octopart import Octopart
    >>> o = Octopart.api(apikey="yourapikey")

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

At the time being only three methods have been switched to the new API:

    parts_search()
    parts_match()
    parts_get()

And the tests will need to be updated. Those methods are the only one being used
in the [`pyparts`][1] project, though.

[1]:https://github.com/guyzmo/pyparts

### method/argument syntax (for API v3)

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

### method/argument syntax (for API v2)

There are a number of arguments in the Octopart API documentation which contain 
periods in their names. When passing these arguments from Python, substitute an
underscore for any periods.

Similarly, substitute underscores for backslashes in method names.

For example:

    >>> o = Octopart()
    >>> o.parts_get(1881614252472, optimize.hide_datasheets=True)
    SyntaxError: keyword can't be an expression

    Instead, pass the argument as:
    >>> o.parts_get(1881614252472, optimize_hide_datasheets=True)

The library will perform the translation internally.

### Roadmap

 * [x] switch to python 3
 * [x] create buildout build
 * [x] use function annotations
 * [o] switch to v3 API
 * [ ] improve and fix tests

## Authors

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


