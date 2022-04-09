from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin
from airflow import configuration
from backfill.main import Backfill

# Get RBAC config.
rbac_authentication_enabled = configuration.getboolean("webserver", "RBAC")

# Add document
project_document_mitem = {
    "name": "Project Documentation",
    "href": "https://airflow.apache.org/",
}
airflow_monitoring_mitem = {
    "name": "Airflow",
    "href": "https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/index.html",
    "category": "Monitoring",
}

# Add new section on airflow UI for backfill
v_backfill_view = Backfill()
v_backfill_package = {
    "name": "Trigger",
    "category": "Backfill",
    "view": v_backfill_view,
}

# Creating a flask blueprint to integrate the templates folder
backfill_blueprint = Blueprint(
    "backfill_blueprint", __name__, template_folder="templates"
)

# Defining the plugin class
class AirflowBackfillPlugin(AirflowPlugin):
    name = "backfill_plugin"
    flask_blueprints = [backfill_blueprint]
    appbuilder_views = [v_backfill_package]
    appbuilder_menu_items = [project_document_mitem, airflow_monitoring_mitem]
