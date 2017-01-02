class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class MissingAuthError(Error):
    """No token was supplied."""

    def __str__(self):
        """Format the error message."""
        return 'no Recorded Future API key or authentication ' \
               'method was provided.'


class UnknownQueryTypeError(Error):
    """The query type could not be identified."""

    def __init__(self, msg=''):
        """Setup the exception.

        Keyword arguments:
        msg: a message that will be added to the exception.
        """
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        """Format the error message."""
        return "Unable to page query. %s" % self.msg


class RemoteServerError(Error):
    """Thrown when the server encounters errors"""
    pass


class JsonParseError(Error):
    """Thrown when the client cannot parse the content as json"""
    def __init__(self, message, content):
        self.message = message
        self.content = content
