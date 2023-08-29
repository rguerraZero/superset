##############################
# ROLE DEFINITIONS STATEMENT #
##############################
ROLE_DEFINITIONS_QUERY = """
SELECT
    human_readable as permission_name,
FROM {dataset}.bi_superset_access.role_definitions_{access_method}
WHERE {role_name} = true
"""

#####################################
# DATA SOURCE PERMISSIONS STATEMENT #
#####################################
DATA_SOURCE_PERMISSIONS_QUERY = """
SELECT
    database,
    table_catalog,
    table_schema,
    table_name
FROM {dataset}.bi_superset_access.datasource_access_{access_method}
WHERE {role_name} = true
"""

#######################
# ROLES PER JOB TITLE #
#######################
ROLES_PER_JOB_TITLE = """
SELECT
    employee,
    role_name
FROM {dataset}.bi_superset_access.roles_per_job_title
"""


#########
# ROLES #
#########

ROLES_QUERY = """
SELECT name
FROM {dataset}.bi_superset_access.roles
WHERE type = '{access_method}'
"""

##################################
# DASHBOARD ROLE ACCESS EXTERNAL #
##################################

DASHBOARD_ROLE_ACCESS_EXTERNAL = """
SELECT
    dashboard_id,
    role_name
FROM {dataset}.bi_superset_access.dashboard_role_access_exterrnal
"""
