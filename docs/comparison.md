# Why Teams Pick Matrix Admin

FastAPI Matrix Admin is meant for teams who already know their stack and want the admin to fit that stack cleanly.

## If you are comparing FastAPI admin libraries

Choose Matrix Admin when you want:

- FastAPI-first integration rather than a framework-agnostic abstraction layer
- async SQLAlchemy as the main supported ORM path
- a quick `register()` experience with a deeper `ModelAdmin` escape hatch
- request-aware scoping for organization, tenant, or role-based data visibility
- a UI that feels intentional and memorable instead of generic backoffice chrome

## What it is trying to be

The best open-source admin for FastAPI teams running real applications.

That means the project is biased toward:

- production-safe defaults
- explicit model registration
- permission-aware routes
- extension points that compose with existing FastAPI services

## What it is not trying to be

- a kitchen-sink multi-ORM admin
- a separate auth platform
- a totally neutral CRUD generator with no product opinion

That narrower scope is deliberate. It is how the library stays sharp.
