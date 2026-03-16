# Plan

## Architecture diagram

```mermaid
architecture-beta
    group testvm(disk)[Test VM]
    
    service svn(database)[SVN] in testvm
    service trac(database)[Trac] in testvm

    group gitlab(cloud)[GitLabs]

    service gitlab-ucam(cloud)[GitLab UCam] in gitlab
    service gitlab-ipsl(cloud)[GitLab IPSL] in gitlab

    service test_data(database)[test_data]

    service deploy(server)[deploy_py]
    service migrate(server)[migrate_py]
    service pytest(server)[pytest]

    test_data:T --> B:deploy
    deploy:T --> B:svn{group}

    trac{group}:B --> T:migrate
    migrate:R --> L:gitlab-ucam
    gitlab-ucam:B --> R:pytest
```


## Workflow

- create a source vm / containers
  - install svn
  - install trac
- create a target vm / containers / online service
  - install gitlab
- use `deploy.py` to poulate source systems
- use `migrate.py` to test a migration
- use `pytest` to run user acceptance tests
