---
Service Owner: t-reporting
Secondaries: Guillermo Negrete (@zgnegrete)
---
# superset-external
Superset Service
<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# Welcome to Superset External

This repository  contains a copy of superset repo, to be compiled and used as a dependency for other projects.

**Current Superset Version Used: 2.1.1, Updated By Guillermo Negrete**


## How to run

To run it locally take in note that needs atleast 3gb on docker memory to run properly

1. Duplicate /docker/.env.sample to /docker/.env
2. `make build`: Generates local superset image
3. `make run`: Runs local superset image

Note: the local build will need you to compile the assets on the host machine:

```
cd superset-frontend
npm install
npm run build
```

### Run debuger

1. Add `breakpoint()` to the point you want to debug
2. After having the service runing, in a new terminal run `docker attach $(docker ps -f name=superset_app --format '{{.ID}}')`

## How to update this repo

in case that you need to update this repo:
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

### Test Download as PDF

To test this functionality locally you can add the followings lines into superset/download/api.py file, around line 95. Instead of raise an exception due to not be able to upload the file to S3, the code will return the file as a data url.
```
with open(f'/tmp/{file_name}', 'rb') as pdf_file:
  pdf_url = f'''data:application/pdf;base64,{base64.b64encode(pdf_file.read()).decode('UTF-8')}'''
```

## Information

- [Superset API](https://superset.apache.org/docs/rest-api)
