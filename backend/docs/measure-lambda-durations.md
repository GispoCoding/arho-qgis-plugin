# Measuring ryhti_client lambda durations

The API gateway cuts requests at 29 seconds (`infra/api.tf`). The lambda itself
may run 120 seconds. To find out whether real imports and exports come close to
the 29 second limit, query the CloudWatch logs.

Log groups: `/aws/lambda/<prefix>-ryhti_client` where `<prefix>` is
`hame-dev`, `tykki-test` or `arho-test`. The environments may live behind
different AWS profiles. Remember the MFA session: `. infra/get-mfa-vars.sh`.

## Overall duration statistics (works on existing logs)

The lambda uses JSON log format, so the platform report is structured.
CloudWatch Logs Insights query:

```
filter `type` = 'platform.report'
| stats count() as invocations,
        pct(record.metrics.durationMs, 50) as p50_ms,
        pct(record.metrics.durationMs, 95) as p95_ms,
        max(record.metrics.durationMs) as max_ms,
        pct(record.metrics.initDurationMs, 95) as p95_init_ms,
        max(record.metrics.maxMemoryUsedMB) as max_mem_used_mb
```

CLI wrapper, one environment at a time:

```bash
PREFIX=hame-dev
QID=$(aws logs start-query \
  --log-group-name "/aws/lambda/${PREFIX}-ryhti_client" \
  --start-time "$(date -d '30 days ago' +%s)" \
  --end-time "$(date +%s)" \
  --query-string "filter \`type\` = 'platform.report'
| stats count() as invocations,
        pct(record.metrics.durationMs, 50) as p50_ms,
        pct(record.metrics.durationMs, 95) as p95_ms,
        max(record.metrics.durationMs) as max_ms,
        pct(record.metrics.initDurationMs, 95) as p95_init_ms" \
  --output text --query queryId)
sleep 15
aws logs get-query-results --query-id "$QID" --output table
```

## Duration per action (after this change is deployed)

The handler logs one `arho_timing` line per invocation with the action name
and the handler wall time. Query:

```
filter message like 'arho_timing action='
| parse message 'action=* duration_ms=*' as action, duration_ms
| stats count() as calls,
        pct(duration_ms, 50) as p50_ms,
        pct(duration_ms, 95) as p95_ms,
        max(duration_ms) as max_ms
  by action
| sort p95_ms desc
```

## Duration per step of an export

`get_plan` logs one `arho_timing step=...` line per phase, so the export can be
split into database time, Python time, gzip time and S3 time. The steps are
`fetch_plan`, `serialize_plan` (which contains `load_plan_objects` and
`plan_object_dicts`), `json_dumps`, `gzip_compress`, `s3_put` and `presign`.
Query:

```
filter message like 'arho_timing step='
| parse message 'step=* duration_ms=*' as step, duration_ms
| stats count() as calls,
        pct(duration_ms, 50) as p50_ms,
        max(duration_ms) as max_ms
  by step
| sort max_ms desc
```

The plan size is logged next to it, so the durations can be read per object
count: `arho_export plan=... land_use_areas=... other_areas=... lines=...
points=...`, `arho_export regulation_groups=...` and
`arho_export json_bytes=... gzip_bytes=...`.

## Deeper profiling with environment variables

Two extra tools are off by default and cost nothing when unset. Set the
variable on the lambda, invoke once, read the logs, then remove the variable.

- `PROFILE_SQL=1` counts every SQL statement and its time. It logs
  `arho_timing step=sql_total duration_ms=... queries=...` and then one
  `arho_sql count=... duration_ms=... sql=...` line per statement, slowest
  first. A high `count` on one statement means the same query is repeated,
  which is the usual sign of a missing eager load.
- `PROFILE_PYTHON=1` runs cProfile around the serialization and logs the 30
  slowest calls as `arho_profile label=get_plan_dictionary`.

Locally, put the variables in `.env` and run
`make dev-ryhti-export uuid=<plan-uuid>`, then read `docker compose -f
docker-compose.dev.yml logs ryhti_client`. The dev container sets
`AWS_LAMBDA_LOG_LEVEL=INFO`, because the lambda runtime drops INFO logs without
it.

## Reading the numbers

- `arho_timing` measures handler wall time only. The platform report
  `durationMs` is the billed view and `initDurationMs` shows cold starts.
- Compare p95 and max against 29000 ms. If real plans still pass that limit
  after these speedups, the next step is an asynchronous import/export design.
