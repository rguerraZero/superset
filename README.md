---
Service Owner: Andrew Mason (@amason09)
Secondaries: Guillermo Negrete (@zgnegrete)
---

# superset

## Table of Contents
+ [What is superset?](#what-is-airflow)
+ [Installing superset](#installing-superset)
    + [Building image for local testing](#building-image-for-local-testing)

## What is superset?
**Apache Superset** is an open-source software application for data exploration and data visualization able to handle data at petabyte scale.

## Installing superset
### Pre Requisites

1. Create a folder called dev/secrets
2. Add your google service account as `service-acct.json`

### Building image for local testing

Clone repository

```
git clone git@github.com:riskive/superset.git
```

Navigate to repository

```
cd superset
```

Build image over Make command( this will take some time to finish)

```
make build-local
```

Start local airflow instance

```
make run-local
```

End local superset instance

```
make stop-local
```