from flask import Blueprint
from .custom_llm import custom_llm
from .webhook import webhook

api = Blueprint("api", __name__)


# Register blueprints
api.register_blueprint(custom_llm, url_prefix="/custom-llm")
api.register_blueprint(webhook, url_prefix="/webhook")
