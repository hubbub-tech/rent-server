from flask import Blueprint
from flask_cors import CORS

from .checkout_cart import bp as checkout_cart

from .checkout_res_add import bp as checkout_res_add
from .checkout_res_edit import bp as checkout_res_edit
from .checkout_res_remove import bp as checkout_res_remove
from .checkout_res_validate import bp as checkout_res_validate


bp = Blueprint("checkout", __name__)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
