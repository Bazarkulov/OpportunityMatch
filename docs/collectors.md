# Collector support

OpportunityMatch uses published, unauthenticated job-board GET APIs.

| Adapter | Interface | Default boards |
|---|---|---|
| Greenhouse | Public Job Board API | `figma` |
| Lever | Public Postings API | `xcimer`, `anybotics`, `hermeus` |

Board identifiers are configurable through `GREENHOUSE_BOARDS` and `LEVER_SITES`. Adapters filter for student-oriented terms such as internship, student, new graduate, fellowship, scholarship, research assistant, co-op, and trainee.

One source failing does not abort the others. Runs record successes, failures, counts, and errors. Records are updated by `(source, external_id)` and an additional fingerprint suppresses obvious cross-source duplicates. Missing records from a successfully refreshed source and listings with parsed past deadlines are marked inactive.

No login-only pages, CAPTCHA, access controls, or application-submission endpoints are used. A board that blocks public GET access should be removed rather than bypassed.
