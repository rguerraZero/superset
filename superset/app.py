# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import click

import logging
import os

from flask import Flask
from flask.cli import with_appcontext
from flask_appbuilder.security.sqla.models import User, Role

from werkzeug.security import generate_password_hash

from superset.initialization import SupersetAppInitializer
from superset.extensions import db


from prometheus_flask_exporter import PrometheusMetrics

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = SupersetApp(__name__)

    try:
        # Allow user to override our config completely
        config_module = os.environ.get("SUPERSET_CONFIG", "superset.config")
        app.config.from_object(config_module)

        app_initializer = app.config.get(
            "APP_INITIALIZER", SupersetAppInitializer)(app)
        app_initializer.init_app()

        PrometheusMetrics(app)
    
        @app.cli.command("create-user")
        @click.argument("email")
        @click.argument("password")
        @click.argument("first_name")
        @click.argument("last_name")
        @with_appcontext
        def create_user(email, password, first_name, last_name):
            """Create a new user in Flask-AppBuilder."""
            user = db.session.query(User).filter_by(username=email).first()
            if user:
                print(f"User {email} already exists.")
                return
            
            role = db.session.query(Role).filter_by(name='Alpha').first()
            if not role:
                print("Role 'Alpha' not found.")
                return
            
            user = User()
            user.username = email
            user.email = email
            user.password = generate_password_hash(password)
            user.first_name = first_name
            user.last_name = last_name
            user.active = True
            db.session.add(user)
            user.roles.append(role)
            db.session.commit()
            print(f"Created user {email}")

        return app

    # Make sure that bootstrap errors ALWAYS get logged
    except Exception as ex:
        logger.exception("Failed to create app")
        raise ex


class SupersetApp(Flask):
    pass
