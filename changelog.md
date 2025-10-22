
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.0] - 2025-10-??

### Added

- Added support for `pc-koubou` as new vendor.
- Implemented `product` class for proper data structuring.

### Changed

- Improved Readme formatting.
- Updated and added type hints.
- Improved code style to follow PEP-8 guidelines.
- Fixed dependency versions in `requirements.txt`.
- Improved function docstrings.
- Updated emojis due to emoji deprecation of aliases.
- Added `slowcon` parameter to `_get_web_through_chromedriver` function to handle slow connections.
- Updated `selenium` usage to match latest version, deprecated `executable_path` parameter removed.
- Added `funcname` to logging format.

### Fixed

- Fixed parsing for all supported vendors to match latest website changes.
- Deleted sleep on page load, as `driver.get` already waits for full page load.

### Deleted

- Chromedriver binary files removed from repository, now `selenium` will handle downloading them automatically.

## [0.0.5] - 2021-08-06

### Added

- Added `darwin` to expected architectures to be executed in, so:
  - UI adapts.
  - `Chromedriver` file looked for is binary or `.exe`

### Changed

- Modified how `PCComponentes` availability is checked.
  - This is still an issue since the website is served by Cloudfare.

## [0.0.4] - 2021-08-05

### Added

- Supports `NeoByte` website as new vendor.

### Changed

- Improved visibility of groups using emojis.

## [0.0.3] - 2020-12-24

### Added

- Added capability to run specific Chromium browser instead of default Chrome, which remains as default.

### Changed

- `Vendor` print replaced by `price`.

## [0.0.2] - 2020-12-23

### Added

- Supports `pccomponentes` website as new vendor.
- Adds selenium and chromedriver as requirements to support web JS rendering.

## [0.0.1] - 2020-12-21

### Added

- Base changelog description matching this project.
- Supports add/remove products to memory and DB.
- Supports specifying a group for each product.
- Supports added `coolmod` as only vendor supported right now.
