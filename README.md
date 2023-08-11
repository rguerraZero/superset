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

1. `make build`: Generates local superset image
2. `make run`: Runs local superset image

Note: the local build will need you to compile the assets on the host machine:

```
cd superset-frontend
npm install
npm run build
```

## How to update this repo

in case that you need to update this repo, you can do in two ways

1. Updating from the original repo
2. Updating by a handmade fix


## Missing Things

1. Configure docker image  + nomad hcl definition
2. Create Tables of user access
3. finish RLS and Table generation



## Information

- [Superset API](https://superset.apache.org/docs/rest-api)
