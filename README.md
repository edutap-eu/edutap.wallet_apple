# edutap.wallet_apple

<p style="text-align:center;">

![PyPI - Version](https://img.shields.io/pypi/v/edutap.wallet_apple?logo=python)
[![CI Tests](https://github.com/edutap-eu/edutap.wallet_apple/actions/workflows/tests.yaml/badge.svg)](https://github.com/edutap-eu/edutap.wallet_apple/actions/workflows/tests.yaml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/edutap-eu/edutap.wallet_apple/main.svg)](https://results.pre-commit.ci/latest/github/edutap-eu/edutap.wallet_apple/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub Repo stars](https://img.shields.io/github/stars/edutap-eu/edutap.wallet_apple)

</p>

This package provides a Python API and web server endpoints to create and update official Apple Wallet Passes.

This package provides

-  an API and models for the creation of Apple pass files (.pkpass)
-  infrastructure to sign pass files with an Apples certificate.
-  Initial pass delivery with save link creation and a matching FastAPI endpoint.
-  Support for the update process of passes
  - using Apple push notifications and
  - providing an update information endpoint (FastAPI)
  - providing an pass delivery endpoint for fetching updated passes.
-  abstract/pluggable data providers are defined to fetch data on pass-delivery or -update.

## Documentation

Read the [complete edutap.wallet_apple documentation](https://docs.edutap.eu/packages/edutap_wallet_apple/index.html) to get started.

## Source Code

The sources are in a GIT DVCS with its main branches at the [GitHub edutap-eu/edutap.wallet_google repository](https://github.com/edutap-eu/edutap.wallet_google) .

We are looking forward to see many issue reports, forks and pull requests to make the package even better.

## Credits

- Initiated and initially financed by [LMU München](https://www.lmu.de).
- Further development was financially supported by [Hochschule München](https://hm.edu/).
- inspired by the work of the [devartis/passbook](https://github.com/devartis/passbook) Python library.

Contributors:

- Alexander Loechel (LMU)
- Philipp Auersperg-Castell (BlueDynamics Alliance)
- Jens Klein (BlueDynamics Alliance)
- Robert Niederreiter (BlueDynamics Alliance)

## License

The code is copyright by eduTAP - EUGLOH Working Package - Campus Life and contributors.

It is licensed under the [EUROPEAN UNION PUBLIC LICENCE v. 1.2](https://opensource.org/license/eupl-1-2/), a free and OpenSource software license.
