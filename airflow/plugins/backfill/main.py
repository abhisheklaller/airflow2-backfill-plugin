import json
import datetime
import _thread
import re
import flask
from flask import request
from flask_admin import BaseView, expose
from flask_appbuilder import (
    expose as app_builder_expose,
    BaseView as AppBuilderBaseView,
    has_access,
)
from airflow import configuration
from shelljob import proc
import os


# Set your Airflow home path
airflow_home_path = os.environ["AIRFLOW_HOME"]

# Local file where history will be stored
FILE = airflow_home_path + "/logs/backfill_history.txt"

rbac_authentication_enabled = configuration.getboolean("webserver", "RBAC")

# RE for remove ansi escape characters
ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")

# Creating a flask admin BaseView
def file_ops(mode, data=None):
    """ File operators - logging/writing and reading user request """
    if mode == "r":
        try:
            with open(FILE, "r") as f:
                return f.read()
        except IOError:
            with open(FILE, "w") as f:
                return f.close()

    elif mode == "w" and data:
        today = datetime.datetime.now()
        with open(FILE, "a+") as f:
            file_data = "{}: {}".format(today, data)
            f.write(file_data)
            return 1


class Backfill(AppBuilderBaseView):
    """ Backfill Airflow class and methods """

    route_base = "/backfill/"

    if rbac_authentication_enabled == True:

        @app_builder_expose("/")
        def list(self):
            """ Render the backfill page to client with RBAC"""
            return self.render_template(
                "backfill_page.html",
                rbac_authentication_enabled=rbac_authentication_enabled,
            )

    else:

        @expose("/")
        def base(self):
            """ Render the backfill page to client """
            return self.render("backfill_page.html")

    @expose("/background")
    @app_builder_expose("/background")
    def background(self):
        """ Runs user request in background """
        dag_name = request.args.get("dag_name")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        cmd = [
            "airflow",
            "tasks",
            "clear",
            str(dag_name),
            "-s",
            str(start_date),
            "-e",
            str(end_date),
            "--yes"
        ]

        # Update command used in history
        file_ops("w", " ".join(cmd) + "\n")
        g = proc.Group()
        g.run(cmd)

        def read_process():
            """ Read logs and append in log file."""
            while g.is_pending():
                lines = g.readlines()
                for proc, line in lines:
                    if not isinstance(line, str):
                        line = line.decode()
                    line = ansi_escape.sub("", line)
                    file_ops("w", "{0} ===> ".format(dag_name) + line)

        _thread.start_new_thread(read_process, ())

        response = json.dumps({"submitted": True})
        return flask.Response(response, mimetype="text/json")
