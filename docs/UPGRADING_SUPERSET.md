# Upgrading Superset

In case that you need to update this repo:

1. Start updating the superset code in one of two ways:
    1. Updating from the original repo
    2. Updating by a handmade fix
2. Manually regenerate API changes:
    - At superset/initialization/__init__.py
   ```python
    from superset.zf_integration.api import ZFIntegrationRestApi

    appbuilder.add_api(ZFIntegrationRestApi)
   ```
3. Confirm that the folders address on the docker compose are still valid, to transfer our custom code into the superset project.
4. Migrate the following features/changes/improvements:
    
    1. Import as PDF:
      - Add option to main menu
      - Add API endpoint
      - Add loading screen on Frontend
    2. Chart menu displays reduced list of actions on Embedded dashboars
      - The chart menu should only display "Export to .CSV" and "Download as Image" 
    3. Main action menu displays reduced list of actions on Embedded dashboards
      - the menu should only display refresh and download actions.
    4. Superset notifications are not displays on Embedded dashboards
    5. Title of the dashboards is not display on Embedded dashboards
    6. Add loading progress feedback, on PDF import loading screen.
    7. Add new funnel option: Order by category. ZFE-76991
    8. Remove available actions on tabs.