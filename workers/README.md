# workers

Python worker process. Scaffolded in T015. Consumes queued jobs from Redis,
executes the permitted provider operation, and runs the normalize/validate/
deduplicate/persist pipeline.
