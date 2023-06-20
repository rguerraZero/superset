#################################
#  ZF CACHE USER DATA STATEMENT #
#################################
CACHE_USER_DATA_QUERY = """
SELECT
    id,
    email as username,
    email,
    first_name,
    last_name,
    is_staff,
    is_active,
    cast(salesforce_id as integer) as enterprise_id
FROM csdataanalysis.cache.cache_user_dw
WHERE email = '{email}'
"""

##############################
# ROLE DEFINITIONS STATEMENT #
##############################
ROLE_DEFINITIONS_QUERY = """
SELECT
    human_readable as permission_name,
FROM csdataanalysis.bi_superset_access.role_definitions_{access_method}
WHERE 1 = 1
AND {role_name} = true
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
FROM csdataanalysis.bi_superset_access.datasource_access_{access_method}
WHERE 1 = 1
AND {role_name} = true
"""

#######################
# ROLES PER JOB TITLE #
#######################
ROLES_PER_JOB_TITLE = """
SELECT
    role_name
FROM csdataanalysis.bi_superset_access.roles_per_job_title
WHERE Employee = '{email}'
"""
