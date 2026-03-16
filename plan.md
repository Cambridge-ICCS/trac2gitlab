# Plan

## Archietcture diagram

## Workflow

- create a source vm
  - install svn
  - install trac
- create a target vm
  - install gitlab
- use `deploy.py` to poulate source systems
- use `migrate.py` to test a migration
- use `pytest` to run user acceptance tests
