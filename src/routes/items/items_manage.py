from datetime import datetime, timedelta
from flask import Blueprint, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import Items

from src.utils.settings import TASK_SESSION_KEY

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_UNAUTHORIZED
)

bp = Blueprint("manage", __name__)


@bp.get("/items/unlock")
def sweep_locked_items():

    dt_timeout = datetime.now()
    locked_items = Items.filter({ "is_locked": True })

    try:
        min_interval = int(request.args.get("min_interval"))
        session_token = request.args.get("session")
    except:
        error = "Your request has been rejected."
        response = make_response({"message": error}, CODE_4_BAD_REQUEST)
        return response
     
    if check_password_hash(session_token, TASK_SESSION_KEY) == False:
        error = "You are not authorized to make this request."
        response = make_response({"message": error}, CODE_4_UNAUTHORIZED)
        return response
    
    for item in locked_items:
        if item.dt_last_locked is None: continue
        
        if dt_timeout - timedelta(minutes=min_interval) > item.dt_last_locked:
            item.unlock()

    message = "Successfully unlocked forgotten items."
    response = make_response({"message": message}, CODE_2_OK)
    return response
