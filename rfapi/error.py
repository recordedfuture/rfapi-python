"""Defines a number of errors that can occur."""


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingAuthError(Error):
    """No token was supplied."""

    def __str__(self):
        """Format the error message."""
        return 'no Recorded Future API key or authentication ' \
               'method was provided.'


class RemoteServerError(Error):
    """Thrown when the server encounters errors."""

    pass


class JsonParseError(Error):
    """Thrown when the client cannot parse the content as json."""

    def __init__(self, message, response):
        """Exception while parsing JSON. Add message and response."""
        Error.__init__(self)
        self.message = message
        self.content = response.content
        self.response = response


class InvalidRFQError(Error):
    """Thrown when RFQ is bad"""

    def __init__(self, message, query):
        """Init the error with the query"""
        Error.__init__(self)
        self.message = message
        self.query = query
