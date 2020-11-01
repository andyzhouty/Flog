"""
    flog.api.v1.views
    ~~~~~~~~~~~~~~~~~

    The module for creating url routes.

    :copyright: Andy Zhou
    :license: MIT
"""
from . import api_v1
from .resources import IndexAPI, UserAPI, PostAPI


# index
api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
# get user schema
api_v1.add_url_rule('/user/<int:user_id>/', view_func=UserAPI.as_view('user'),
                    methods=['GET', 'PUT', 'DELETE'])
# get/put/patch/delete a post
api_v1.add_url_rule('/post/<int:post_id>/', view_func=PostAPI.as_view('post'),
                    methods=['GET', 'PUT', 'PATCH', 'DELETE'])
