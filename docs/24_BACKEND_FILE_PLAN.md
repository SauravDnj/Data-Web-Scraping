# Backend File Plan

Recommended:

``` text
apps/api/
└── app/
    ├── main.py
    ├── api/
    │   └── v1/
    │       ├── projects.py
    │       ├── configs.py
    │       ├── jobs.py
    │       ├── records.py
    │       ├── exports.py
    │       └── schedules.py
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   └── logging.py
    ├── db/
    │   ├── base.py
    │   ├── session.py
    │   └── models/
    ├── domain/
    │   ├── jobs.py
    │   ├── records.py
    │   └── projects.py
    ├── services/
    ├── repositories/
    ├── providers/
    │   ├── base.py
    │   └── google_maps/
    ├── pipeline/
    │   ├── normalize.py
    │   ├── validate.py
    │   └── deduplicate.py
    └── schemas/
```

The exact structure may evolve, but responsibilities must remain
separated.
