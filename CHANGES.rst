Changelog
=========

2.5.1 (2018-03-25)
------------------

- Fix for not joining Fields params in connect api get_entity request, PR#2. Thanks @rkokkelk.

2.5.0 (2018-02-25)
------------------

- Discontinue documentation for the Raw API Client.


2.4.0 (2018-10-31)
------------------

- Add retries for Gateway (502) and Server Unavailable (503) Errors.
- Added support for disabling SSL verification.
- Added support for fetching demodata for URL and CyberVulnerability types.
- Added support for using checksum when syncing fusion files.
- Bug fix for risklist download retries returning not passing
raw and stream parameters causing bad response type.
- Minor bug fixes.


2.3.0 (2018-03-02)
------------------

- Add support for Fusion calls in ConnectApi
- Bug fix for orderBy assertion in ConnectApi search
- Renaming some arguments for clarification. Possibly breaking.

2.2.0 (2018-02-16)
------------------

- Added support for Alert queries in the Connect API.
- Fix SignatureHashAuth authentication for Connect API.
- Minor improvements and bug fixes.

2.1.0 (No public release)

- Use a request session to reuse tcp connections.


2.0.0 (2017-08-01)
------------------

- Due to Recorded Future API branding conventions, we are changing the names of our two customer facing APIs.
- The *ApiClient* will is now named *RawApiClient* and the *ApiV2Client* is now the *ConnectApiClient*.
- Imports of *ApiClient* and *ApiV2Client* will continue to work, but are deprecated.
- The files *apiv1client.py* and *apiv2client.py* have been renamed to *rawapiclient.py* and *connectapiclient.py* respectively.
- *QueryResponse* classes in *query.py* with ApiV2* names have been renamed, but will continue to work due to aliasing. These are *ApiV2Response* => *ConnectApiResponse*, *ApiV2FileResponse* => *ConnectApiResponse*, and *ApiV2CsvFileResponse* => *ConnectApiCsvFileResponse*.
- Test files have been renamed.
- Added functions to get demo events from the Connect API.

1.5.0 (2017-03-29)
------------------

- Introduces *ApiV2Client* to use with Recorded Future simplified APIv2, and refactors some code into a common parent *BaseApiClient* for both the *ApiClient* and *ApiV2Client*.
- Minor bug fixes

1.4.0 (2017-01-24)
------------------

- Fix exception message formatting bugs.
- Fix paging bug
- New classes *HttpError* and *AuthenticationError* that parses the server error
- Add support to not use gzip for transfer.

1.3.0 (2017-01-17)
------------------

- Add warning on incorrect limit when paging.
- New: class *InvalidRFQError* replaces *UnknownQueryTypeError*.
- Add feature to set *app_version* and *app_name* for tracking.
- Use headers only for paging.
- Some pep8 fixes.
- Minor bug fixes.

1.2.0 (2017-01-09)
------------------

- Add retry logic on read timeouts.
- Fix CSV paging.
- Add option to return *QueryResponse* objects when paging.

1.1.0 (2017-01-02)
------------------

- Fix *__init__.py* to export classes. Move exceptions to own file.

1.0.0 (2016-12-21)
------------------

- Move beta to version 1.0.0