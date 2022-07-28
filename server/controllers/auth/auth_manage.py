from flask import Blueprint

bp = Blueprint('manage', __name__)

@bp.post('/password/reset/token=<token>')
def pass_reset(token):
    flashes = []
    data = request.json
    if data:
        user = Users.unique({"email": data["email"].lower()})
        if user:
            is_authenticated = verify_auth_token(token, user.id)
            if is_authenticated:
                hashed_pass = generate_password_hash(data["newPassword"])
                Users.set({"id": user.id}, {"password": hashed_pass})

                flashes.append("You've successfully reset your password!")
                data = {"flashes": flashes}
                response = make_response(data, 200)
                return response
    flashes.append("Reset attempt failed. Try again.")
    data = {"flashes": flashes}
    response = make_response(data, 200)
    return response


@bp.post('/password/recovery')
def pass_recover():
    flashes = []
    data = request.json
    if data:
        user = Users.unique({"email": data["email"].lower()})
        if user:
            if user.session is None: token = create_auth_token(user)
            else: token = generate_password_hash(user.session)

            reset_link = f"{Config.CORS_ALLOW_ORIGIN}/password/reset/token={token}"
            email_data = get_password_reset_email(user, reset_link)
            send_async_email.apply_async(kwargs=email_data)
        flashes.append("If this email has an account, we have sent the recovery link there.")
        data = {"flashes": flashes}
        response = make_response(data, 200)
        return response
    else:
        flashes.append("Sorry, you didn't send anything in the form, try again.")
        data = {"flashes": flashes}
        response = make_response(data, 406)
        return response
