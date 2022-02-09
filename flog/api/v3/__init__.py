"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import APIBlueprint
from flask_cors import CORS

api_v3 = APIBlueprint("api_v3", __name__)
CORS(api_v3)

from . import views
