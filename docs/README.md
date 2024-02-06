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

This repository contains a copy of superset repo, to be compiled and used as a dependency for other projects.

**Current Superset Version Used: 2.1.1, Updated By Guillermo Negrete**

## How to run

To run it locally take in note that needs atleast 3gb on docker memory to run properly

1. Duplicate /docker/.env.sample to /docker/.env
2. `make build`: Generates local superset image
3. `make run`: Runs local superset image

Note: the local build will need you to compile the assets on the host machine:
Note2: in case that access method to test is `external`
add to the composer for each image the argument
```
    build:
      context: .
      dockerfile: Dockerfile
      args:
        ASSET_BASE_URL: http://localhost:8088
```


```
cd superset-frontend
npm install
npm run build
```

### Run debugger

1. Add `breakpoint()` to the point you want to debug
2. After having the service runing, in a new terminal run `docker attach $(docker ps -f name=superset_app --format '{{.ID}}')`


### Test Download as PDF

To test this functionality locally you can add the followings lines into superset/download/api.py file, around line 95. Instead of raise an exception due to not be able to upload the file to S3, the code will return the file as a data url.
```
with open(f'/tmp/{file_name}', 'rb') as pdf_file:
  pdf_url = f'''data:application/pdf;base64,{base64.b64encode(pdf_file.read()).decode('UTF-8')}'''
```

## Information

- [Superset API](https://superset.apache.org/docs/rest-api)
