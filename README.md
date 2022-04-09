# Airflow 2 Plugin - One Stop Shop

This repo contains production-ready airflow 2 plugin to support backfill compatability and keeping documentation/monitoring dashboards link on UI. 
Codebase is written in python language, HTML and Bootstrap 4.

## Overview:

With rollout of new airflow version, there is migration activity starts in most of the organisation. And why not to migrate!! as airflow 2.x version
provides new cool features ranging from high-availability to advance plugins support. In this blog, we will focus how we can make airflow UI as central
point to many components for your project.


## Features:
* Backfill through UI
* Add external monitoring dashboard links
* Add documents on UI

## Assumptions:

### Support Airflow 2.x versions
### Backfill through UI:
Have you created a new Airflow DAG, but now you have to run it using every data snapshot created during the last six months? There is straight forward 
command (`airflow tasks clear -s <start-date> -e <end-date>`) which you can run in your airflow cluster but sometimes it won't be good to access airflow 
production cluster and run command directly. For community version, end user can't access airflow cluster directly due to security reason and they end up 
creating requests of backfill to platform team.

Ideally dags owner should have rights to run backfill in production as they are whole sole owner of their execution. For that, as platform team we can easily
provide backfill compatibility on UI so that user can just click one button and boom!! their backfill starts.

*Note:* 
  * It is highly recommend to use `airflow tasks clear` instead of `airflow dags backfill` as it won't fully worked if your cluster is in k8's
  * In order to use `airflow tasks clear`, you might need history in airflow metadata of that dag for given date time range.

## Directory Structure:

    .
    ├── airflow                   # Airflow main directory
    ├────────── images            # Contains images of screenshots of airflow UI
    ├────────── dags              # Contains all your dags
    └────────── plugins           # Plugin code for backfill and integrate external links on UI

## Usage

* Click trigger under the Backfill section
![Alt text](./airflow/images/trigger.png?raw=true "Trigger")

* Provide your Dag ID (Note: Users are supposed to put the correct dag id as plugin is not validating it).
![Alt text](./airflow/images/backfill.png?raw=true "Backfill")
* Provide start and end date (It should not be greater than the current date and the difference between shouldn’t be greater than 30 days, otherwise you will get the invalidate prompt)
* Once you click start button, the framework will trigger backfill in the airflow webserver and you can see the logs of your dag as usual on UI. Please note: sometime it will take time to spin up the dag instance depending upon Kubernetes resources and scheduler queue.
![Alt text](./airflow/images/submitted.png?raw=true "Submitted")
* You can integrate external links on ui by changing code [here](https://github.com/abhisheklaller/airflow2-backfill-plugin/blob/f26ee1fa8e2495020a2f69f02194548379b0dccf/airflow/plugins/__init__.py#L12)

## Testing locally:
Follow below steps:

Step 1. Clone this repo in your local.

Step 2. Create virtual env by running `python3.7 -m virtualenv ~/python-virtual-envs/airflow2-backfill-plugin`.

Step 3. Activate above env e.g. `source ~/python-virtual-envs/airflow2-backfill-plugin/bin/activate`.

Step 4. Export the following env vars:
  * `export AIRFLOW_HOME={full_path_to_repo_dir}/airflow2-backfill-plugin/airflow`
  * `export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW_HOME}/dags"`
Step 5. Run below command to install packages
  * `CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.2.5/constraints-3.7.txt"`
  * `pip install "apache-airflow==2.2.5" --constraint "${CONSTRAINT_URL}"`
  * `pip install shelljob`
  * `pip install flask_admin`

Step 6. Run `airflow standalone`. If not able to run, `deactivate` the virtual env and activate again.

Step 7. Set `rbac=True` in airflow.cfg file placed at `$AIRFLOW_HOME`

Step 8. You should now be able to access Airflow at `http://localhost:8080/`.

Step 9. Login in Airflow with username and password as `admin` and password will be shown in logs when run `airflow standalone` command.

## Integrating in existing airflow 2 cluster:
Follow below steps:

Step 1. Clone this repository code in your system

Step 2. Plugin configuration

  * If plugin folder not already available, just simply put the plugin folder inside your cluster at `AIRFLOW_HOME`.
  * if it's an existing Airflow Environment. Navigate to the existing plugins folder in your codebase. Extend your existing `__init__.py` file by `__init__.py` of this plugin.

Step 3. Add below library dependency in your docker image:
```
flask-admin==1.5.7
shelljob==0.5.6
```

Step 4. Restart the webserver.

**Note:** You can check the logs of the backfill command by entering in webserver pod and reading `$AIRFLOW_HOME/logs/backfill_history.txt` file.