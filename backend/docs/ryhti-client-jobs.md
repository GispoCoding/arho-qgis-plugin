# Running ryhti_client actions as jobs

The API gateway stops every request after 29 seconds. An action that takes longer
(a large plan export or import, a WFS import of many plans, a validation that waits
on the Ryhti API) then fails for the caller, even when the lambda finishes the work.
Job mode avoids this: the caller submits the request as a job, gets a `job_id` at
once and polls for the answer.

This page is for the developer of an API client, such as the QGIS plugin. Without the
job flag every action works as before, so a client can move to job mode one action at
a time.

## Submit a job

Add `"run_as_job": true` to the request of any action except `get_upload_url`. Only
the JSON value `true` turns job mode on.

```json
{
  "action": "get_plan",
  "plan_uuid": "1f8a5d6c-3b2e-4c1d-9e8f-7a6b5c4d3e2f",
  "run_as_job": true
}
```

The lambda checks the request first. A request that cannot run is refused at once,
with the same answer as without the flag, and no job is created (see
[Error codes](#error-codes)). Otherwise the answer is `202`:

```json
{
  "title": "Job submitted.",
  "details": {"job_id": "8d0bd5a4-6a4f-4f0e-9a5e-0d1c7b0c5b9e"},
  "ryhti_response": null
}
```

`get_upload_url` ignores the flag and answers at once, as before, so a client may send
the flag on every request. `get_job` ignores it too.

## Poll the job

Send the `get_job` action with the `job_id` at the top level of the request:

```json
{"action": "get_job", "job_id": "8d0bd5a4-6a4f-4f0e-9a5e-0d1c7b0c5b9e"}
```

When the job is found, the answer is always `200`, whatever happened to the job. An
error status from `get_job` means that the poll failed, never that the job failed.

```json
{
  "title": "Job found.",
  "details": {
    "job_id": "8d0bd5a4-6a4f-4f0e-9a5e-0d1c7b0c5b9e",
    "status": "done",
    "result": {
      "statusCode": 200,
      "body": {
        "title": "Returning serialized plan from database.",
        "details": {"download_url": "https://...", "key": "..."},
        "ryhti_response": null
      }
    }
  },
  "ryhti_response": null
}
```

`details` holds:

- `job_id`: the id of the job.
- `status`: `queued`, `running`, `done` or `failed`, see [Job states](#job-states).
- `result`: when the job is `done`, the answer that the action would have given
  without the flag. `statusCode` is its HTTP status code and `body` its JSON body, as
  an object, not as a string. For any other status, `result` is `null`.
- `error`: only when the job is `failed`, a generic message:
  `"The job failed. Please contact Arho support team."`

So a client can pass `result.statusCode` and `result.body` to the handler it already
has for the answer without the flag.

`get_job` honours `Accept-Encoding: gzip` like every other action. The whole answer is
compressed, and `result` inside it is plain JSON.

## Job states

| Status | Meaning |
| --- | --- |
| `queued` | The job is stored and waits to start. |
| `running` | The action runs. |
| `done` | The action ran. `result` holds its answer, whatever its status code. |
| `failed` | The job crashed, never started or never finished. `result` is `null`. |

`done` does not mean success. An action that answers with an error, for example `404`
for a plan that does not exist, makes a `done` job with that `404` in `result`. Handle
it as you would handle the answer without the flag.

`failed` means that there is no answer. Show a generic error. The details are in the
lambda log only.

### Stale jobs

A job that crashes hard (at the lambda timeout, or out of memory) cannot store its own
failure. So `get_job` reports `failed` for a job that is still

- `queued` longer than the job time limit after it was created, or
- `running` longer than the job time limit after it started.

The job time limit equals the lambda timeout: 900 seconds (15 minutes) in AWS. A job
past the limit is never started later.

### Retention

A job is deleted 7 days after it was created. `get_job` then answers `404`.

## Error codes

A submit, that is a request with `"run_as_job": true`:

| Status | Title | When |
| --- | --- | --- |
| `202` | `Job submitted.` | The job is stored and started. |
| `400` | `Missing action.` | The request has no `action`. |
| `400` | `Unknown action.` | No action has this name. |
| `400` | `Missing plan_uuid.` | The action needs a `plan_uuid` and the request has none. |
| `400` | `Invalid plan_uuid.` | `plan_uuid` is not a UUID. |
| `405` | `Plan matter actions not supported.` | A removed plan matter action. |
| `502` | `Job could not be started.` | The job was stored but could not be started. It is stored as `failed`. Try again later. |
| `500` | `Internal Server Error.` | An unexpected error, for example in the database. |

The `502` answer:

```json
{
  "title": "Job could not be started.",
  "details": {"error": "The job could not be started. Please try again later."},
  "ryhti_response": null
}
```

`get_job`:

| Status | Title | When |
| --- | --- | --- |
| `200` | `Job found.` | The job exists. See `details.status` for how it went. |
| `400` | `Missing job_id.` | The request has no `job_id`. |
| `400` | `Invalid job_id.` | `job_id` is not a UUID. |
| `404` | `Job not found.` | No job has this id, or the job was deleted after 7 days. |
| `500` | `Internal Server Error.` | An unexpected error, for example in the database. |

Every error answer carries a message in `details.error`.

## Polling

- Poll every 2 seconds, and stop when the status is `done` or `failed`.
- Give up after the job time limit plus a margin, for example after 16 minutes in AWS
  (900 seconds plus one minute). The stale rule normally makes `get_job` report
  `failed` before that, so the deadline matters only when the polls themselves fail.
- A `400` or `404` from `get_job` means a bug in the client, or a job older than 7
  days. A `500`, an error from the API gateway or a network error says nothing about
  the job: poll again at the next interval, until the deadline.
- While a job runs, a poll may take a few seconds longer, because it may start a new
  lambda instance.

## Good to know

- A job runs to its end even when the client stops polling. A job cannot be cancelled.
- The backend does not stop two jobs on the same plan from running at the same time,
  as it does not stop two calls without the flag. Do not submit the same action twice.
- The `download_url` in the result of a `get_plan` job expires one hour after the job
  ran, so fetch it soon after the job is `done`.
- The examples show the JSON body of a request through the API gateway. A direct
  lambda invocation, as in local development, sends the same keys in the event and
  gets `{"statusCode": ..., "body": {...}}` back.
- In local development (`JOB_RUNNER=inline`), the job runs inside the submit call, so
  the submit answers only after the job is `done` or `failed`. The API is the same.
