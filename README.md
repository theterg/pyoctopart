## pyoctopart

A simple Python client frontend to the Octopart public REST API.

For detailed API documentation, refer to the Octopart API documentation:

 * https://octopart.com/api/docs/v2/rest-api

This is a fork of https://github.com/jbaker0428/Python-Octopart-API

This fork is *incompatible* with Python 2 distributions!

## Install

just do:

    python3 setup.py install

and it'll be available from your python REPL:

    % python3
    >>> from pyoctopart.octopart import Octopart
    >>> o = Octopart.api(apikey="yourapikey")

when the lib will be considered stable enough, I'll upload it to [pipy](https://pypi.python.org/pypi?:action=pkg_edit&name=pyoctopart):

    % pip install pyoctopart

## Develop

if you just want to develop, you can do:

    % buildout

which will download dependencies and deploy a python command in `bin/`:

    % bin/python3
    >>> from pyoctopart.octopart import Octopart
    >>> o = Octopart.api(apikey="yourapikey")
    
You can run regression tests using:

    % bin/test

## Note

### method/argument syntax

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

## Todo

 * [x] switch to python 3
 * [x] create buildout build
 * [x] use function annotations
 * [ ] switch to v3 API
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


