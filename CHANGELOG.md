# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-03-13

### Added

- Added a richer admin extension surface with `ModelAdmin`, `AdminAction`, `DetailPanel`, and `DashboardCard`
- Added model-level permissions for `view`, `create`, `edit`, `delete`, and `export`
- Added request-aware row scoping hooks for tenant-aware or role-aware admin views
- Added bulk actions and a custom action execution endpoint
- Added relationship search APIs for large foreign-key datasets
- Added JSON field rendering support and detail panel rendering on record pages
- Added `ROADMAP.md`, `SUPPORT.md`, migration notes, integrations docs, FAQ-style docs, and LLM-readable docs indexes

### Changed

- Refreshed the Matrix UI shell with stronger visual identity, better typography, command-hint affordances, and a more polished operator experience
- Repositioned the project around FastAPI + async SQLAlchemy instead of generic admin breadth
- Updated docs and README to reflect the actual shipped API and current product direction
- Updated docs metadata and navigation for GitHub Pages and broader discoverability
- Bumped the package version to `1.1.0`

### Fixed

- Fixed test collection so the suite runs cleanly instead of failing during discovery
- Fixed dashboard behavior in restricted environments where `psutil.boot_time()` can raise permission errors
- Fixed list table checkbox rendering so bulk-select UI behaves correctly
- Fixed audit logging defaults by requiring an explicit audit model instead of instantiating an abstract base
- Fixed critical bug where `MatrixAdmin` failed to auto-initialize session dependency, resulting in empty list views
- Fixed demo application seeding logic and added reliable database reset for better testing
- Fixed session cookie configuration so local development and production can use different secure-cookie behavior

### Security

- Enforced configured model permissions in admin routes when authentication is enabled
- Preserved CSP, signed actions, and authenticated session flows while improving the admin surface

## [1.0.3] - 2025-12-07

### Added

- Async SQLAlchemy CRUD
- Auto-discovery
- Authentication and audit logging foundations
- Matrix-styled admin UI

[1.1.0]: https://github.com/rasinmuhammed/fastapi-matrix-admin/releases/tag/v1.1.0
[1.0.3]: https://github.com/rasinmuhammed/fastapi-matrix-admin/releases/tag/v1.0.3
