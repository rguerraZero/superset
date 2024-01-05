Contributing to `superset-external`

## Prerequisites

* Python 3.8
* Docker
* Recommended: pyenv w/virtualenv
* PIP packages
  * pip==23.0.1
  * pip-tools==6.12.3
  * pip-compile-multi==2.6.3

## Building docker

You will need to set 12GB of memory for docker to build the image.

```sh
> make docker-build
```

## Running superset

1. Modify `bi_superset/superset_config.py` by changing
this line `AUTH_TYPE = AUTH_OAUTH` to `AUTH_TYPE = AUTH_DB`
2. User management:
   * If running against local db:
        ```sh
        docker compose run superset flask create-user '<username>@zerofox.com' '<the-password>' '<firstname>' '<lastname>'
        ```
   * If running against QA then use the following credentials:
   * Username: `test_qa@zerofox.com`
   * Password: `test_qa`
3. Run docker compose:
    ```sh
    > make docker-up
    ```
4. Browse `http://localhost:8088` and use credentials from above.

### Troubleshooting

#### Static resources not loading

Make sure to configure NodeJs 16.

```sh
cs superset-frontend
ASSET_BASE_URL=http://localhost:8088 npm run build --verbose
```

## Celery debugging

1. Add `from celery.contrib import rdb; rdb.set_trace()` in the lines you wish the debugger to break.
2. Run `> docker compose up superset-worker-beat superset-worker` to start docker compose with the workers.
3. Search for celery worker id using `> docker ps`.
4. Run `> docker exec -it <celery_worker_id> /bin/bash` to enter the worker container.
5. Wait for logs in docker compose to show `Remote Debugger:6900: Waiting for client...`.
6. At this point you can attach to the debugger using `> telnet 127.0.0.1 6907`.

### Troubleshooting

#### Report Schedule is still working, refusing to re-compute.
This means that previous report is still running,
and it will not allow to run a new one until the previous one is finished.

This could happen if previous task exited unexpectedly,
and the celery worker did not have the chance to update the status of the task.

If this happens, you can manually update the status in using the following steps:

1. Connect to superset database.
2. Search for the task id in the table `report_schedule`
3. Filter out logs from `report_execution_log` and column `state`
   to `Error` for any log that has the same `report_schedule_id` as the task id.
   And its newer than timeout configured for the job.

## Adding dependencies

Add the dependency under `./requirements/base.in`.

Make sure you went through `Building docker` section.

```sh
> docker-rebuild-deps
```

This will generate all the .txt files under `./requirements/` directory.

### Troubleshooting unresolvable dependencies

#### Multiple possible versions for same dependency

1. You will get something like this
    ```
    Package pillow was resolved to different versions in different environments: 9.5.0 and 10.1.0
    ```

2. Find for pillow in the requirements/*.txt
    ```sh
    # At development.txt
    pillow==9.5.0
        # via
        #   apache-superset
        #   weasyprint

    # At base.txt
    pillow==10.1.0
        # via weasyprint
    ```

3. In this case, I will add pillow to the constraints.txt file,
since both dependencies are coming from weasyprint. 
I will pick the common version, which is 9.5.0.
    ```sh
    pillow==9.5.0
    ```

#### Bad constraints.txt file

1. If you get errors like this:
    ```
    There are incompatible versions in the resolved dependencies:
    greenlet==1.1.3.post0 (from -c requirements/constraints.txt (line 3))
    greenlet>=2.0.0 (from gevent==23.9.1->-r requirements/docker.in (line 19))
    ```
2. First find all the requirements/*.txt files too see where are they coming from.
In this case they are both coming from apache-superset (setup.py):
    ```sh
    # From base.txt:
    greenlet==1.1.3.post0
        # via
        #   -c requirements/constraints.txt
        #   sqlalchemy

    # From docker.txt
    greenlet==3.0.1
        # via
        #   gevent
        #   sqlalchemy
    ```
3. In this case, the constraints.txt is the one that is causing the issue, so we need to update it. If after checking dependencies.in is not clear, run dependency resolution and store the result in a file:
    ```sh
    > docker-rebuild-deps > out.txt
    ```
4. Look for lines such as: 
    ```sh
    sqlalchemy==1.4.50        requires greenlet!=0.4.17; python_version >= "3" and (platform_machine == "aarch64" or (platform_machine == "ppc64le" or (platform_machine == "x86_64" or (platform_machine == "amd64" or (platform_machine == "AMD64" or (platform_machine == "win32" or platform_machine == "WIN32"))))))[0m
    ```
5. Add to the constraints file or the requirements file a version of the package that is compatible with the rest of the dependencies.
