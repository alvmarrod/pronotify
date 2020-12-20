
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.0.5] - 2020-10-??
 
### Added

- Load new movements and consolidate them capability completed.

## [0.0.4] - 2020-10-12
 
### Added

- Added basic testing for `yamlconfig`.
- Added basic testing for `database`.
- Added basic testing for `analysis`.
- Added scaffolding for testing `process`.
- Added pytest to [requirements](./requirements.txt) file.

### Changed

- Updated `generate_base_config` function to make use of `save_config` function.

## [0.0.3] - 2020-10-08
 
### Added

- Change version to `0.0.3`
- Added basic files and functions to work with sqlite3 databases for consolidated data
- Added basic files and functions to work with configuration using YAML
- Added [requirements](./requirements.txt) file

## [0.0.2] - 2020-10-04
 
### Added

- Change version to `0.0.2`
- Recognise columns with date values
- Menu to control the app behaviour
- Added platform control for output cleaning
   
### Changed

- Moved previous main steps to new proccesses block
- Moved `load_movements` to processes block
- Moved load data option from main args to menu option
 
### Fixed

- Changed default CSV reading encoding to `utf-8`

## [0.0.1] - 2020-09-30
 
### Added

- Added this changelog
- Added [version](./version.txt) file