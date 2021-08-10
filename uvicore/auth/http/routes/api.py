import uvicore
from uvicore.http import Request
from uvicore.http.routing import Routes, ApiRouter, ModelRouter, Guard
from uvicore.support.dumper import dump, dd
from uvicore.auth.user_info import UserInfo

@uvicore.routes()
class Api(Routes):

    # Apply scopes to all routes and children controllers
    #scopes = ['authenticated']
    #scopes = ['authenticated', 'employee']
    #scopes = None

    def register(self, route: ApiRouter):
        """Register API Route Endpoints"""

        # Define controller base path
        route.controllers = 'uvicore.auth.http.api'

        @route.group(tags=['Auth'], scopes=['authenticated'])
        def authenticated_routes():

            @route.get('/userinfo')
            def userinfo(request: Request) -> UserInfo:
                """Detailed User Info Including Roles and Permissions"""

                # HTTP example
                # TOKEN=$(fa-api tgb-local login wiki-vue-app token)
                # http GET 'https://wiki-api-local.triglobal.io/api/auth/userinfo' Authorization:"Bearer $TOKEN"

                # Get the user from the request
                user: UserInfo = request.scope['user']
                # uvicore.auth.user_info.UserInfo(
                #     id=2,
                #     uuid='823003ad-6e1f-42ed-a024-f45f400c1b30',
                #     username='mreschke@triglobalblockchain.com',
                #     email='mreschke@triglobalblockchain.com',
                #     first_name='Matthew',
                #     last_name='Reschke',
                #     title='',
                #     avatar='',
                #     groups=['Administrator'],
                #     roles=['Administrator'],
                #     permissions=['authenticated', 'admin'],
                #     superadmin=True,
                #     authenticated=True
                # )

                # Return UserInfo
                return user

        # Return router
        return route
