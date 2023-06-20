# %%
%load_ext autoreload
%autoreload 2
# %%
%env GOOGLE_APPLICATION_CREDENTIALS=/Users/gnegrete/Library/Application Support/zf-bi/env/secrets/service-acct.json
# %%
from bi_security_manager.adapter.bigquery_sql import BigquerySQL
from bi_security_manager.services.role_gatherer import RoleGatherer
from bi_security_manager.services.user_gatherer import UserGatherer
from bi_security_manager.services.data_source_permission import DataSourcePermission
# %%
sql = BigquerySQL()
role_gatherer = RoleGatherer(sql=sql)
user_gatherer = UserGatherer(sql=sql)
data_source_permission = DataSourcePermission(sql=sql)
# %%
user = user_gatherer.get_user(user_email="gnegrete@zerofox.com")
#%%
user._is_staff = False
user._enterprise_id = 'asdasd'
# %%
user.role_name = role_gatherer.get_user_role_name(user=user)
# %%
role_permissions = role_gatherer.get_user_role_permission(user=user)
# %%
role_permissions
