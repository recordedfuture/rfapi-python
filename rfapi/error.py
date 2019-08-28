"""Defines a number of errors that can occur."""


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingAuthError(Error):
    """No token was supplied."""

    def __init__(self, message='No Recorded Future API key or '
                 'authentication method was provided.', *args):
        """Init the error with the query"""
        Error.__init__(self, message % (args))


class RemoteServerError(Error):
    """Thrown when the server encounters errors."""
    pass


class InvalidRFQError(Error):
    """Thrown when RFQ is bad"""

    def __init__(self, message, query):
        """Init the error with the query"""
        Error.__init__(self, message)
        self.query = query


class HttpError(Error):
    """Thrown when http call fails"""

    def __init__(self, message, response):
        """Init the error with the request module response object"""
        Error.__init__(self, message)
        self.response = response

    @property
    def content(self):
        return self.response.content

    @property
    def status_code(self):
        return self.response.status_code


class JsonParseError(HttpError):
    """Thrown when the client cannot parse the content as json."""
    pass


class AuthenticationError(HttpError):
    """Thrown when the client on 401 error."""
    pass
