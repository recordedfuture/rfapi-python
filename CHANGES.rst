Changelog
=========

1.4.0 (2017-01-24)
------------------

- Fix exception message formatting bugs.
- Fix paging bug
- New classes HttpError and AuthenticationError that parses the server error
- Add support to not use gzip for transfer.


1.3.0 (2017-01-17)
------------------

- Add warning on incorrect limit when paging.
- New: class InvalidRFQError replaces UnknownQueryTypeError.
- Add feature to set app_version and app_name for tracking.
- Use headers only for paging.
- Some pep8 fixes.
- Minor bug fixes.

1.2.0 (2017-01-09)
------------------

- Add retry logic on read timeouts.
- Fix CSV paging.
- Add option to return QueryResponse objects when paging.


1.1.0 (2017-01-02)
------------------

- Fix __init__.py to export classes. Move exceptions to own file.

1.0.0 (2016-12-21)
------------------

- Move beta to version 1.0.0