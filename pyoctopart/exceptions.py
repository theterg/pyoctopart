#!/usr/bin/env python

class OctopartException(Exception):
    """Various errors that can be raised by the Octopart API."""
    __slots__ = ["arguments", "arg_types", "arg_ranges", "code"]
    def __init__(self, args, arg_types, arg_ranges, error_message):
        self.arguments = args
        self.arg_types = arg_types
        self.arg_ranges = arg_ranges
        self.message = error_message

    def __str__(self):
        args = ' '.join(('\nPassed arguments:', str(self.arguments)))
        argt = ' '.join(('\nArgument types:', str(self.arg_types)))
        argr = ' '.join(('\nArgument ranges:', str(self.arg_ranges)))
        string = self.message + args + argt + argr
        return string

class OctopartArgumentMissingError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Required argument missing from method call.')

class OctopartArgumentInvalidError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Passed an invalid argument for this method.')

class OctopartTypeArgumentError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Argument type mismatch.')

class OctopartRangeArgumentError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Numeric argument value out of valid range.')

class OctopartStringLengthError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'String argument outside of allowed length.')

class OctopartLimitExceededError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Value of (start+limit) in a bom/match line argument exceeds 100.')

class Octopart404Error(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Unexpected HTTP Error 404.')

class Octopart503Error(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Unexpected HTTP Error 503.')

class OctopartNonJsonArgumentError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Argument is not a JSON-encoded list of pairs.')

class OctopartInvalidSortError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'Invalid sort order. Valid sort order strings are "asc" and "desc".')

class OctopartTooLongListError(OctopartException):
    def __init__(self, args, arg_types, arg_ranges):
        super(self, OctopartException).__init__(
            args,
            arg_types,
            arg_ranges,
            'List argument outside of allowed length.')



