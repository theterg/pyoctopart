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
from pprint import pprint


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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
        if new_dict['__class__'] != cls.__name__:
            raise TypeArgumentError('Dict is for class %s, not %s' % (
                new_dict['__class__'], cls.__name__))
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
