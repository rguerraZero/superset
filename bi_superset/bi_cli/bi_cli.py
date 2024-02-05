import logging
import click

from flask.cli import with_appcontext
from superset import appbuilder

logger = logging.getLogger(__name__)


@click.command()
@with_appcontext
def bi_init() -> None:
    """
    BI Custom CLI Superset command that sync all BI Security Manager
    """
    from bi_superset.bi_cli.bi_cli_security_manager import BICLISecurityManager

    logging.info("Starting BI Securirty Manager Sync")
    sec_manager = BICLISecurityManager(appbuilder)

    # logging.info("Syncing BI Roles and Permissions")
    # sec_manager.sync_roles_and_permissions()
    # logging.info("Syncing BI Roles and Permissions Completed")

    # logging.info("Syncing Roles per Job title")
    # sec_manager.loads_roles_per_job_title()
    # logging.info("Syncing Roles per Job title Completed")

    # logging.info("Syncing Data Sources Access")
    # sec_manager.loads_data_sources_access()
    # logging.info("Syncing Data Sources Access Completed")

    # logging.info("Syncing Dashboard Access")
    # sec_manager.loads_dashboard_access_external()
    # logging.info("Syncing Dashboard Access Completed")

    # logging.info("Updating Superset Dashboard default access")
    # sec_manager.update_dashboard_default_access()
    # logging.info("Updating Superset Dashboard default access Completed")

    logging.info("Updating RBAC Roles")
    sec_manager.sync_rbac_role_list()
    sec_manager.sync_dashboard_rbac_role_assignation()
    logging.info("Updating RBAC Roles Completed")

    logging.info("Sync Completed")
