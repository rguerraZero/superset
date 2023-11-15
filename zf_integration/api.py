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
import logging

from jwt import ExpiredSignatureError
from typing import Any, Dict
from flask import request, Response, jsonify, make_response
from flask_appbuilder import expose
from marshmallow import ValidationError
from superset.utils.jwt import JWTParser

from superset.security.manager import GuestTokenResourceType
from superset.security.guest_token import GuestTokenUser, GuestUser, GuestToken
from superset.extensions import event_logger
from superset.views.base_api import BaseSupersetApi, statsd_metrics
from superset.models.dashboard import Dashboard
from superset.models.embedded_dashboard import EmbeddedDashboard
from bi_superset.bi_security_manager.models.access_origin import AccessOrigin
from bi_superset.bi_security_manager.models.access_method import AccessMethod
from bi_superset.bi_security_manager.models.user import User as ZFUser, BASE_VIEW_ROLE
from bi_superset.bi_security_manager.services.user_service import UserService


from sqlalchemy import and_
from flask_appbuilder.security.sqla.models import Role


logger = logging.getLogger(__name__)


class ZFIntegrationRestApi(BaseSupersetApi):
    resource_name = "zf_integration"
    openapi_spec_tag = "ZF-integration"
    csrf_exempt = True

    @expose("/get_info/", methods=["POST"])
    @event_logger.log_this
    @statsd_metrics
    def get_info(self) -> Response:
        """Response
        Returns a guest token that can be used for auth in embedded Superset, and the dashboard details to the related user.
        ---
        post:
          description: >-
            Fetches a guest token and the dashboard names and ids related to the user.
          requestBody:
            description: JWT token
            required: true
          responses:
            200:
              description: Result contains the guest token and dashboard details
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/guest_token_created_and_details'
            401:
              $ref: '#/components/responses/401'
            400:
              $ref: '#/components/responses/400'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            superset_user, token_user = self._get_superset_and_token_user(
                request)
            default_dashboards = self.get_dashboards_details_by_roles(
                [role.id for role in superset_user.roles if not BASE_VIEW_ROLE in role.name])
            custom_dashboards = self.get_dashboards_details_by_roles(
                [role.id for role in superset_user.roles if BASE_VIEW_ROLE in role.name]
            )
            guest_token = self.get_guest_token(
                token_user, default_dashboards['uuids'], custom_dashboards['uuids'],
                [role.name for role in superset_user.roles])
            respond = {
                'guest_token':  guest_token,
                'default_dashboards': default_dashboards['dashboards'],
                'custom_dashboards': custom_dashboards['dashboards'],
             }
            return make_response(jsonify(respond), 200)
        except ExpiredSignatureError:
            return self.response_401()
        except ValidationError as error:
            return self.response_400(message=error.messages)

    def _get_superset_and_token_user(self, request):
        '''
        Returns a Superset and Token user,
        based on the data contained on the JWT token.
        '''
        data = JWTParser.parse_jwt_from_request(request)
        user_base = self.get_guest_token_user(data)
        user_token = GuestToken(user=user_base, resources=[])
        superset_user = self._get_superset_user(user_token, data)
        return superset_user, user_token

    def _get_superset_user(self, user_token, data) -> Any:
        '''
        Returns a superset user with the roles and rls updated based on the base user and the ZF user defined on Data.
            Parameters:
                user_token: base user token define with base data from the JWT token
                data: complete data included on the JWT token
        '''
        guestUser = GuestUser(user_token, [])
        user_info = self.get_user_info_from_jwt_data(data)
        zf_user: ZFUser = ZFUser.from_dict(user_info)
        userService = self._get_user_service()
        return userService.update_roles_rls(guestUser, zf_user)
    
    def _get_user_service(self) -> UserService:
        '''
        Returns an UserService
        '''
        sm = self.appbuilder.sm
        return UserService(
            AccessMethod.EXTERNAL.value, AccessOrigin.ZF_DASHBOARD.value, sm)

    def get_user_info_from_jwt_data(self, data) -> Dict[str, Any]:
        '''
        Returns a dict which constain the complete info to represent a ZF user.
        Every user will be considered as not staff, due to be accessing from ZF-Dashboard
            Parameters: 
                data: Dict which the values to get the ZF user values
            Returns:
                user_info (Dict[str, Any]): Dict with user info.

        '''
        user_info = {
            'id': data['user_id'],
            'username': data['name'],
            'email': data['sub'],
            'first_name': data['name'],
            'last_name': data['name'],
            'is_staff': False,
            'is_active': True,
            'enterprise_id': data['enterprise_id'],
        }
        return user_info

    def get_guest_token(self, user, default_ds, custom_ds, roles) -> Any:
        '''
        Returns a valid guest token generated, based on the given user and dashboards.
        '''
        token = self.appbuilder.sm.create_guest_access_token(
            user,
            [{
                'type': GuestTokenResourceType.DASHBOARD.value,
                'id': uuid} for uuid in default_ds+custom_ds],
            [],
            roles
        )
        return token

    def get_guest_token_user(self, data) -> GuestTokenUser:
        '''
        Returns a GuestTokenUser object with username, first_name and last_name
            equal to the use full name defined on ZF.
        '''
        user = GuestTokenUser(
            username=data['name'],
            first_name=data["name"],
            last_name=data["name"])
        return user

    def get_dashboards_details_by_roles(self, roles) -> Dict[str, Any]:
        '''
        Returns a Dict with the uuids and the dashboard details related to the given role.
            Parameters:
                roles: List with roles id to get the Dashboards
            Returns:
                data (Dict[str, any]): Dict with uuids fields which contains the uuids of every selected dashboard
                    and dashboards field wich contain a list of dashboards with id, name and uuid details.

        '''
        dashboards = self.appbuilder.sm.get_session.query(
            Dashboard.id,
            Dashboard.dashboard_title,
            EmbeddedDashboard.uuid
        ).join(
            Dashboard.roles
        ).join(
            Dashboard.embedded
        ).filter(
            and_(
                Dashboard.published.is_(True),
                Role.id.in_(roles),
            ),
        ).distinct().all()
        data = {
            'uuids': [str(d.uuid) for d in dashboards],
            'dashboards': [{'id': d.id, 'name': d.dashboard_title, 'uuid': d.uuid} for d in dashboards]
        }
        return data
