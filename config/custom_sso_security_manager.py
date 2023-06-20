import logging
from superset.security import SupersetSecurityManager
import pandas as pd
import pandas_gbq


class CustomSsoSecurityManager(SupersetSecurityManager):
    
    def oauth_user_info(self, provider, response=None):
        logging.debug("Oauth2 provider: {0}.".format(provider))
        if provider == "zfapi":
            me = (
                self.appbuilder.sm.oauth_remotes[provider]
                .get("https://api.zerofox.com/1.0/users/me/")
                .json()
            )
            print(response)
            logging.debug("user_data: {0}".format(me))
            details = {
                "id": me["id"],
                "username": me["email"],
                "email": me["email"],
                "first_name": me["first_name"],
                "last_name": me["last_name"],
                "is_staff": me.get("is_staff", False),
                "is_active": me.get("is_active", False),
            }

            return details

    def auth_user_oauth(self, userinfo):
        user = super(CustomSsoSecurityManager, self).auth_user_oauth(userinfo)
        logging.debug(f" Current User: {user} ")
        logging.debug(f" User Info: {userinfo}")
        user_query = f"""
        SELECT DISTINCT SALESFORCE_ID FROM `csdataanalysis.cache.cache_user_dw` where id = {userinfo["id"]}
        """
        if userinfo["is_staff"] is True and user.roles != "Admin":
            roles = self.find_role("zerofox_internal")
        elif userinfo["is_staff"] is not True:
            df = pd.read_gbq(user_query)
            enterprise = df["SALESFORCE_ID"].values[0]
            logging.debug(f" Returned SALESFORCE_ID Value: {enterprise}")
            if not enterprise:
                logging.debug("No SALESFORCE_ID or is_staff value present")
                # set role as zf_anon that mimics the public role
                roles = self.find_role("zf_anon")
            else:
                logging.debug("SALESFORCE_ID present, no existing role")
                if not self.find_role(enterprise):
                    logging.debug("Role Missing")
                    # add new role with SALESFORCE_ID
                    enterprise_role = self.add_role(enterprise)
                    logging.debug(f"Role Created: {enterprise_role}")
                    base_role = self.find_role("enterprise_base")
                    # assign permissions to new role that mirrors enterprise_base permissions
                    for x in base_role.permissions:
                        logging.debug(f"Permissions found {x}")
                        self.add_permission_role(enterprise_role, x)
                        # assign newly created role to user
                    roles = self.find_role(f"{enterprise}")
        else:
            logging.debug("No SALESFORCE_ID or is_staff value present")
            roles = self.find_role("zf_anon")
        user.roles += [roles]
        logging.debug(" Update <User: %s> role to %s", user.username, roles)
        self.update_user(user)  # update user role
        return user
