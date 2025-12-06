# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Inline editing in list view
- Advanced filter sidebar
- Export to Excel/PDF
- Bulk actions UI
- WebSocket live updates

## [0.1.0] - 2025-12-05

### Added
- 🎉 Initial beta release
- ✨ Auto-discovery for SQLAlchemy models with smart defaults
- 🔐 Signed URL tokens for Anti-IDOR protection (unique feature!)
- 🎯 Pydantic v2 discriminated unions support (first FastAPI admin!)
- 🏗️ Full async CRUD operations with SQLAlchemy
- 👥 Authentication system with password hashing and session management
- 🛡️ Role-Based Access Control (RBAC) per model
- 📝 Field-level audit logging with change tracking
- 🎨 Modern Shadcn-inspired UI with dark mode
- 📊 Analytics dashboard with KPIs and Chart.js visualizations
- 🚫 CSP with nonces for XSS prevention
- 📤 CSV export with UTF-8 BOM (Excel-compatible)
- 🔍 Multi-field search functionality
- 📄 Pagination with configurable page sizes
- ⚡ Zero Node.js requirement (Pure Python + CDN)
- 🧪 27/30 tests passing (90% coverage)

### Security
- Implemented signed URL tokens for tamper-proof actions
- Added CSRF protection via signed cookies
- Implemented Content Security Policy with nonces
- Added password hashing with SHA-256 + salt
- Implemented comprehensive audit logging

### Documentation
- Comprehensive README with examples
- Contributing guidelines
- MIT License
- Code documentation with docstrings

### Technical
- FastAPI integration
- SQLAlchemy async support
- Pydantic v2 validation
- Jinja2 templating
- HTMX for progressive enhancement
- Alpine.js for reactivity
- Tailwind CSS via CDN

## [0.0.1] - 2025-12-01

### Added
- Initial project structure
- Basic admin interface prototype

---

## Version History Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

[Unreleased]: https://github.com/rasinmuhammed/fastapi-matrix-admin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rasinmuhammed/fastapi-matrix-admin/releases/tag/v0.1.0
[0.0.1]: https://github.com/rasinmuhammed/fastapi-matrix-admin/releases/tag/v0.0.1
