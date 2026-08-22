# Changelog of Frontend

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-08-22
### Added
- show worker communication schema version in engine panel
- add JSON export and import of personal storage

### Fixed
- pass non-ASCII subject text unmodified to regex engines

### Changed
- remove unused monolithic SubjectEditor component

## [2.1.1] - 2026-05-06

### Fixed
- implement dynamic runtime injection for ROBOTS_META via Nginx entrypoint

## [2.1.0] - 2026-05-04

### Changed

- Optimize tooltip finding and improve performance in pattern editor components
- Update terms modal component logic
- refactor the architecture so engines define flag metadata dynamically

### Added

- implement robust regex token parsing and syntax highlighting
- implement terms of service and cookie policy compliance flow

## [2.0.1] - 2026-05-04

### Fixed

- prevent scrollbar flash by setting initial tooltip position to fixed

## [2.0.0] - 2026-05-03

### Fixed

- allow vertical scrolling on mobile by replacing fixed height and overflow-hidden with min-h-screen

### Changed

- Improve pattern header view for better organization of flags icons
- Improve readability of AI assistant chat rendering including pipeline and header bar
- update header responsiveness to wrap engine and cheat sheet below logo on tablet view

### Added

- Implement AI chat title generation in the store
- Persistent chat history feature for the AI assistant

## [2.0.0.beta] - 2026-04-30

- Initial release as a separate component.
