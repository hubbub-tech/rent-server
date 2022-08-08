from flask import Blueprint
from flask_cors import CORS


from .item_details import bp as item_details
from .item_feed import bp as item_feed
