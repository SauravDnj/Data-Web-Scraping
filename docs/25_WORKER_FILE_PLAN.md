# Worker File Plan

Recommended:

``` text
workers/
├── worker_main.py
├── queue.py
├── jobs/
│   ├── execute_collection.py
│   ├── heartbeat.py
│   ├── recovery.py
│   └── retry.py
└── observability/
    └── logging.py
```

The worker should depend on backend domain/service interfaces rather
than duplicating business logic.

There should be one source of truth for job state transitions.
