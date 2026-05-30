# API Overview

> Auto-generated docs available at `/api/docs/` (Swagger) and `/api/redoc/`.
> Live OpenAPI schema: `/api/schema/`.

All endpoints are prefixed with `/api/v1/`. JWT authentication is required for everything except `/auth/register/`, `/auth/login/`, `/auth/refresh/`, `/auth/forgot-password/`, `/auth/reset-password/`, and `/auth/verify-email/{token}/`.

## Auth

| Method | Path                                    | Description                            |
|-------:|-----------------------------------------|----------------------------------------|
| POST   | `/auth/register/`                       | Create a new user (student or teacher) |
| POST   | `/auth/login/`                          | Returns `access`, `refresh`, `user`    |
| POST   | `/auth/refresh/`                        | Refresh access token                   |
| POST   | `/auth/logout/`                         | Blacklist the refresh token            |
| GET    | `/auth/verify-email/{token}/`           | Verify email                           |
| POST   | `/auth/forgot-password/`                | Email a reset link                     |
| POST   | `/auth/reset-password/`                 | Reset password using token             |

## Users

| Method | Path                                    | Role              |
|-------:|-----------------------------------------|-------------------|
| GET    | `/users/users/`                         | Super Admin       |
| GET    | `/users/users/me/`                      | Any authenticated |
| PATCH  | `/users/users/me/`                      | Any authenticated |
| POST   | `/users/users/change-password/`         | Any authenticated |
| GET    | `/users/students/`                      | Teacher / Admin   |
| GET    | `/users/students/me/`                   | Student           |
| GET    | `/users/teachers/me/`                   | Teacher           |

## Subjects & Exams

| Method | Path                                              | Role            |
|-------:|---------------------------------------------------|-----------------|
| GET    | `/exams/subjects/`                                | All             |
| POST   | `/exams/subjects/`                                | Teacher / Admin |
| GET    | `/exams/`                                         | All (scoped)    |
| POST   | `/exams/`                                         | Teacher / Admin |
| GET    | `/exams/{slug}/`                                  | All             |
| POST   | `/exams/{slug}/publish/`                          | Teacher / Admin |
| POST   | `/exams/{slug}/enroll/`                           | Teacher / Admin |
| POST   | `/exams/{slug}/enroll-all/`                       | Teacher / Admin |
| GET    | `/exams/my-upcoming/`                             | Student         |

## Questions

| Method | Path                              | Role            |
|-------:|-----------------------------------|-----------------|
| GET    | `/questions/`                     | Teacher / Admin |
| POST   | `/questions/`                     | Teacher / Admin |
| GET    | `/questions/options/`             | Teacher / Admin |
| GET    | `/questions/test-cases/`          | Teacher / Admin |

## Submissions

| Method | Path                                              | Role     |
|-------:|---------------------------------------------------|----------|
| POST   | `/submissions/attempts/start/`                    | Student  |
| POST   | `/submissions/attempts/{id}/answer/`              | Student  |
| POST   | `/submissions/attempts/{id}/submit/`              | Student  |
| POST   | `/submissions/attempts/{id}/proctor-event/`       | Student  |
| POST   | `/submissions/attempts/{id}/run-code/`            | Student  |
| GET    | `/submissions/attempts/my-attempts/`              | Student  |
| GET    | `/submissions/attempts/pending-evaluation/`       | Teacher  |
| GET    | `/submissions/attempts/{id}/`                     | Owner / Teacher |

## Evaluations

| Method | Path                                  | Role     |
|-------:|---------------------------------------|----------|
| POST   | `/evaluations/from-attempt/`          | Teacher  |
| POST   | `/evaluations/{id}/grade-answer/`     | Teacher  |
| POST   | `/evaluations/{id}/publish/`          | Teacher  |
| GET    | `/evaluations/me/`                    | Student  |

## Analytics & reports

| Method | Path                                                  | Role            |
|-------:|-------------------------------------------------------|-----------------|
| GET    | `/analytics/student-dashboard/`                       | Student         |
| GET    | `/analytics/teacher-dashboard/`                       | Teacher         |
| GET    | `/analytics/super-admin-dashboard/`                   | Super Admin     |
| GET    | `/analytics/leaderboard/?exam_id=...`                 | Any             |
| GET    | `/analytics/reports/attempts-csv/?exam_id=...`        | Teacher         |
| GET    | `/analytics/reports/attempts-xlsx/?exam_id=...`       | Teacher         |
| GET    | `/analytics/reports/attempt-pdf/{attempt_id}/`        | Teacher         |

## Notifications

| Method | Path                                  | Role  |
|-------:|---------------------------------------|-------|
| GET    | `/notifications/`                     | Self  |
| POST   | `/notifications/{id}/mark-read/`      | Self  |
| POST   | `/notifications/mark-all-read/`       | Self  |
| GET    | `/notifications/unread-count/`        | Self  |

## AI Assistant (Databricks)

| Method | Path                                                       | Role     |
|-------:|------------------------------------------------------------|----------|
| POST   | `/ai/assistant/convert/sql-to-spark-sql/`                  | Any auth |
| POST   | `/ai/assistant/convert/sql-to-pyspark/`                    | Any auth |
| POST   | `/ai/assistant/convert/python-to-pyspark/`                 | Any auth |
| POST   | `/ai/assistant/explain/`                                   | Any auth |
| POST   | `/ai/assistant/grade-descriptive/`                         | Teacher  |
| POST   | `/ai/assistant/chat/`                                      | Any auth |
| GET    | `/ai/history/`                                             | Self     |

## Audit (Super Admin)

| Method | Path                  |
|-------:|-----------------------|
| GET    | `/audit/logs/`        |

---

## Sample requests

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mewatitech.edu","password":"Admin@12345"}'
```

### Start an attempt

```bash
ACCESS=eyJhbGciOiJIUzI1NiIsIn...
EXAM_ID=00000000-0000-0000-0000-000000000000

curl -X POST http://127.0.0.1:8000/api/v1/submissions/attempts/start/ \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"exam_id\":\"$EXAM_ID\"}"
```

### Convert SQL → Spark SQL via AI

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/assistant/convert/sql-to-spark-sql/ \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"code":"select top 100 * from employee"}'
```
