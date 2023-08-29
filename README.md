---
Service Owner: Guillermo Negrete (@zgnegrete)
Secondaries:
---
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
to run it locally take in note that needs atleast 3gb on docker memory to run properly

1. Duplicate /docker/.env.sample to /docker/.env
2. `make build`: Generates local superset image
3. `make run`: Runs local superset image

Note: the local build will need you to compile the assets on the host machine:

```
cd superset-frontend
npm install
npm run build
```

## How to update this repo

in case that you need to update this repo:
1. Start updating the superset code in one of two ways:
    1. Updating from the original repo
    2. Updating by a handmade fix
2. Manually regenerate API changes:
    - At superset/initialization/__init__.py
   ```
   from superset.zf_integration.api import ZFIntegrationRestApi
   ...
   ...
      appbuilder.add_api(ZFIntegrationRestApi)
   ```
3. Confirm that the folders address on the docker compose are still valid, to transfer our custom code into the superset project.
in case that you need to update this repo, you can do in two ways

## Deploy

This repo deploys two instances of superset, each one with a different `.terra` configuration:

### Superset internal (aka Superset Big)

Used for internal ZeroFox employees only. It has more internal data and it is only accesible from the VPN.

Links:

- QA: https://build.zerofox.com/job/superset-qa-deploy/
- Stag: https://build.zerofox.com/job/superset-stag-deploy/
- Prod: https://build.zerofox.com/job/superset-prod-deploy/

### Insights (aka Superset external or Superset Small)

Used for external users. It has less data and it is accesible from cloud.zerofox.com through ZF-Dashboard. Only ZeroFox employees can access the UI through the VPN.

Links:

- QA: https://build.zerofox.com/job/insights-qa-deploy/
- Stag: https://build.zerofox.com/job/insights-stag-deploy/
- Prod: https://build.zerofox.com/job/insights-prod-deploy/

## Information

- [Superset API](https://superset.apache.org/docs/rest-api)
