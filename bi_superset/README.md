# ZF Superset Custom Security 

This enables to separate custom logic for authentication and permissions sync to be incorporate on superset

## Files and Folder Structure


```
bi_superset
├── bi_cli
│   ├── bi_cli.py                                   # Superset command injected on `superset/cli/`
│   └── bi_cli_security_manager.py                  # loads instruction that get data from bq into superset table
├── bi_macros
│   └── macros.py                                   # Superset Macros
├── bi_security_manager
│   ├── bi_custom_security_manager.py               # Access logic for superset
│   ├── bi_security_manager
│   │   ├── adapter
│   │   │   └── bigquery_sql.py                     # Get data from BQ
│   │   ├── models
│   │   │   ├── acces_method.py                     # Enum model `internal` and `external`
│   │   │   ├── models.py                           # BI superset models over tables created by this process
│   │   │   ├── superset_role_permission.py         # Roles and permission mapping
│   │   │   └── user.py                             # ZF SSO user
│   │   ├── port
│   │   │   └── a_sql.py                            # Interface for SQL
│   │   ├── services
│   │   │   ├── dashboard_role_access_service.py    # Gets dashboard access over roles `eternal`
│   │   │   ├── data_source_permission_service.py   # Gets data source access per role `internal`
│   │   │   ├── role_gatherer_service.py            # Gets all roles `internal` and `external`
│   │   │   └── roles_per_job_title_service.py      # Gets all roles per job title `internal`
│   │   └── sql
│   │       └── queries.py                          # List of all queries over bigquery access tables
├── bi_custom_security_manager.py                   # All logic regarding custom sso auth and permissions
├── superset_config_loca.py                         # Superset config for local development
└── superset_config.py                              # Superset config
```



# How this works

the logic is divided in two parts:

## Sync permission and role access

This is done by running `superset bi-init`, this will query `csdataanalysis.bi_superset_access` tables and load this data inside of superset DB.

Based on the env variable `SUPERSET_ACCCESS_METHOD` it will use the `internal` or `external` access method.

This will query the following tables

- `csdataanalysis.bi_superset_access.dashboard_role_access_external`: This contains roles and dashboard id relation to be loaded on superset, where RBAC is enabled for external user
  - target table: `bi_superset_access_dashboard_role_access`
- `csdataanalysis.bi_superset_access.datasource_access_{external,internal}`: This contains roles and data source id relation to be loaded on superset. restricting access to datasources
  - taget table: `bi_datasource_access`
- `csdataanalysis.bi_superset_access.role_definitions_{external,internal}`: This contains role definitions permissions to be loaded into superset
  - target table: `ab_role`
- `csdataanalysis.bi_superset_access.roles`: this contains list of roles names
  - target table: `ab_role`
- `csdataanalysis.bi_superset_access.roles_per_job_title`: this contains list of roles per job title used only for `internal` zf users
  - target table: `bi_roles_per_job_title`


## Security Manager

this has all the logic regarding user authentication and permissions sync, this is loaded on `superset_config.py` and `superset_config_local.py`. 

all this logic is based on the data loaded on `superset bi-init` step, so is super important to have this data loaded before running superset or any time where is a change over the data source.

main task are:
1. Set and update the propper user roles based on sso provided information
2. Set and update Row level security based on sso provided information


# Updating process

As mention before all data is located in `csdataanalysis.bi_superset_access` tables, so any change on this tables will be reflected on superset after running `superset bi-init` command.

Those tables information are linked with a google drive sheet located [HERE](https://docs.google.com/spreadsheets/d/18uqs55hVFXg-78miD-cU_jXZfKG4bXgfPqHPenv9geU/edit#gid=1515956923)


