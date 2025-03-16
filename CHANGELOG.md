# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-03-16

### Added

- direct links to regexes for easier sharing and integration.
- added logo for the project.

### Changed

- icons updated to make the interface more intuitive.
- make interface more responsive.

## [1.1.0] - 2025-01-21

### Added

- link to official website "https://openregex.com" in web interface
- regex output and highlight connection in web interface
- regex CheatSheet in web interface
- debug information in web interface

### Changed

- reorganize code for `*.js` and `*.css` files
- reorder colors group in web interface
- black theme for web interface

### Fixed

- error in web-browser console for `*.js` files

## [1.0.0] - 2025-01-10

### Added

- Worker and thread setup in Dockerfile for Gunicorn
- `robots.txt` file for web-crawling bots
- Metadata to HTML
- Docker Hub link in web interface

### Changed

- `style.css` for better UI

### Removed

- Python version information on web interface
- Unused include libraries from `CppRegex.cpp`
- `timeout_wrapper()` from `CppRegex.cpp`

## [0.1.0-dev] - 2025-01-07

initial release

### Added

- Initial release
- Web-interface
- Python re - Engine
- Python regex - Engine
- Java regex - Engine
- C++ regex - Engine
