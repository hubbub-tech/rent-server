import time
import json
import requests
from datetime import datetime, date
from werkzeug.security import generate_password_hash

from flask import Blueprint, redirect, session, g, request, url_for, send_from_directory, current_app
from flask_cors import CORS

from blubber_orm import Users, Profiles, Orders, Addresses
from blubber_orm import Items, Details, Testimonials, Issues

from server.tools.build import create_review
from server.tools.build import send_async_email, get_newsletter_welcome
from server.tools.build import validate_edit_account, validate_edit_password, upload_image
from server.tools.build import generate_receipt_json

from server.tools.settings import get_random_testimonials
from server.tools.settings import login_required, AWS, json_sort
from server.tools.settings import Config, ReCAPTCHA_VERIFY_URL

from server.tools import blubber_instances_to_dict, json_date_to_python_date

bp = Blueprint('main', __name__)
CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)

@bp.get("/index")
def index():
    user_url = AWS.get_url(dir="users")
    testimonial = get_random_testimonials(size=1)

    if testimonial:
        testimonial = testimonial[0]
        testimonial_to_dict = testimonial.to_dict()

        user = Users.get({"id": testimonial.user_id})
        user_to_dict = user.to_dict()

        user_to_dict["name"] = user.alias
        user_to_dict["city"] = user.address.city
        user_to_dict["state"] = user.address.state
        user_to_dict["profile"] = user.profile.to_dict()
    else:
        user_to_dict = {}
        testimonial_to_dict = {}
    return {
        "user": user_to_dict,
        "testimonial": testimonial_to_dict,
        "photo_url": user_url
    }

@bp.post("/newsletter/join")
def newsletter_form_submit():
    flashes = []
    data = request.json
    recaptcha_data = {
        "secret": Config.ReCAPTCHA_SERVER_API_KEY,
        "response": data.get('token')
    }
    captcha_response = requests.post(ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()
    if data and captcha["success"]:
        name = data.get("name")
        email = data.get("email")
        if email:
            email_data = get_newsletter_welcome({"name": name, "email": email})
            send_async_email.apply_async(kwargs=email_data)
            flashes.append("Woo, you've been added to our newsletter!")
            return {"flashes": flashes}, 200
    return {"flashes": ["There was a problem adding you to our email list. try again."]}, 406

@bp.get("/accounts/u/id=<int:id>")
@login_required
def account(id):
    searched_user = Users.get({"id": id})
    user_url = AWS.get_url(dir="users")
    item_url = AWS.get_url(dir="items")
    if searched_user:
        user_to_dict = searched_user.to_dict()
        user_to_dict["name"] = searched_user.name
        user_to_dict["cart"] = searched_user.cart.to_dict()
        user_to_dict["profile"] = searched_user.profile.to_dict()
        listings = Items.filter({"lister_id": searched_user.id})
        listings_to_dict = []
        for item in listings:
            item_to_dict = item.to_dict()
            next_start, next_end  = item.calendar.next_availability()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["lister"] = user_to_dict
            item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
            item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
            item_to_dict["details"] = item.details.to_dict()
            listings_to_dict.append(item_to_dict)
        return {
            "photo_url": {"user": user_url, "item": item_url},
            "user": user_to_dict,
            "listings": listings_to_dict
        }
    else:
        return {"flashes": ["this user does not exist at the moment."]}, 404

#edit personal account
@bp.get("/accounts/u/edit")
@login_required
def edit_account():
    photo_url = AWS.get_url(dir="users")
    user_to_dict = g.user.to_dict()
    user_to_dict["address"] = g.user.address.to_dict()
    user_to_dict["profile"] = g.user.profile.to_dict()
    return {
        "user": user_to_dict,
        "photo_url": photo_url
    }

#edit personal account
@bp.post("/accounts/u/edit/submit")
@login_required
def edit_account_submit():
    flashes = []
    data = request.json
    form_data = {
        "self": g.user,
        "email": data.get("email", g.user.email),
        "bio": data.get("bio", g.user.profile.bio),
        "payment": data.get("payment", g.user.payment),
        "phone": data.get("phone", g.user.profile.phone)
    }

    form_check = validate_edit_account(form_data)
    if form_check["is_valid"]:
        Users.set({"id": g.user_id}, {
            "email": form_data["email"],
            "payment": form_data["payment"]
        })
        Profiles.set({"id": g.user_id}, {
            "bio": form_data["bio"],
            "phone": form_data["phone"]
        })
        flashes.append("Successfully edited your account!")
        return {"flashes": flashes}, 200
    else:
        flashes.append(form_check["message"])
        return {"flashes": flashes}, 406

@bp.post("/accounts/u/photo/submit")
@login_required
def edit_account_photo_submit():
    flashes = []
    image = request.files.get("image")
    if image:
        image_data = {
            "self": g.user,
            "image" : image,
            "directory" : "users",
            "bucket" : AWS.S3_BUCKET
        }
        upload_response = upload_image(image_data)
        if upload_response["is_valid"]:
            Profiles.set({"id": g.user_id}, {"has_pic": True})
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 200
        else:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 406
    return {"flashes": ["Failed to receive your profile update."]}, 406

#edit personal password
#check that the confirmation pass and new pass match on frontend
@bp.post("/accounts/u/password/submit")
@login_required
def edit_password_submit():
    flashes = []
    errors = []
    data = request.json
    if data:
        form_data = {
            "self" : g.user,
            "current_password" : data["password"]["old"],
            "new_password" : data["password"]["new"]
        }
        form_check = validate_edit_password(form_data)
        if form_check["is_valid"]:
            hashed_pass = generate_password_hash(form_data["new_password"])
            Users.set({"id": g.user_id}, {"password": hashed_pass})

            flashes.append(form_check["message"])
            return {"flashes": flashes}, 200
        else:
            errors.append(form_check["message"])
            return {"errors": errors}, 406
    flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, 406

@bp.post("/accounts/u/address/submit")
@login_required
def edit_address_submit():
    flashes = []
    data = request.json
    form_data = {
        "num": data["address"]["num"],
        "street": data["address"]["street"],
        "apt": data["address"].get("apt", ""),
        "zip": data["address"]["zip"],
        "city": data["address"]["city"],
        "state": data["address"]["state"]
    }
    address = Addresses.filter(form_data)
    if not address: address = Addresses.insert(form_data)

    Users.set({"id": g.user_id}, {
        "address_num": form_data["num"],
        "address_street": form_data["street"],
        "address_apt": form_data["apt"],
        "address_zip": form_data["zip"]
    })
    flashes.append("You successfully changed your address!")
    return {"flashes": flashes}, 200

@bp.post("/accounts/i/hide/id=<int:item_id>")
@login_required
def hide_item(item_id):
    flashes = []
    item = Items.get({"id": item_id})
    if item:
        if item.lister_id == g.user_id:
            data = request.json
            if data: Items.set({"id": item_id}, {"is_available": data["toggle"]})

            if item.is_available: flashes.append("Item has been revealed.")
            else: flashes.append("Item has been hidden.")
            return {"flashes": flashes}, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 403
    return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.get("/accounts/i/edit/id=<int:item_id>")
@login_required
def edit_item(item_id):
    flashes = []
    item = Items.get({"id": item_id})
    if item:
        if item.lister_id == g.user_id:
            item_to_dict = item.to_dict()
            item_to_dict["details"] = item.details.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            return { "item": item_to_dict }, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 403
    return {"flashes": ["this item does not exist at the moment."]}, 404

@bp.post("/accounts/i/edit/submit")
@login_required
def edit_item_submit():
    flashes = []
    data = request.json
    if data:
        item = Items.get({"id": data["itemId"]})
        # date_end_extended = json_date_to_python_date(data["extendEndDate"])
        form_data = {
            "price": data.get("price", item.price),
            "description": data.get("description", item.details.description),
            # "extend": date_end_extended
        }
        Items.set({"id": item.id}, {"price": form_data["price"]})
        Details.set({"id": item.id}, {"description": form_data["description"]})
        # Calendars.set({"id": item.id}, {"date_ended": date_end_extended})
        flashes.append(f"Your {item.name} has been updated!")
        return {"flashes": flashes}, 200
    flashes.append("No changes were received! Try again.")
    return {"flashes": flashes}, 406

@bp.post("/accounts/i/photo/submit")
@login_required
def edit_item_photo_submit():
    flashes = []
    data = request.form
    item = Items.get({"id": data["itemId"]})
    image = request.files.get("image")
    if image and item:
        image_data = {
            "self": item.id,
            "image" : image,
            "directory" : "items",
            "bucket" : AWS.S3_BUCKET
        }
        upload_response = upload_image(image_data)
        if upload_response["is_valid"]:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 200
        else:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 406
    return {"flashes": ["Failed to receive the photo update for your item."]}, 406


@bp.get("/accounts/o/review/id=<int:order_id>")
@login_required
def review_item(order_id):
    flashes = []
    order = Orders.get({"id": order_id})
    if order:
        item = Items.get(order.item_id)
        if order.renter_id == g.user_id:
            item_to_dict = item.to_dict()
            item_to_dict["details"] = item.details.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            order_to_dict = order.to_dict()
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()
            return { "item": item_to_dict, "order": order_to_dict }, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 406
    return {"flashes": ["this order does not exist at the moment."]}, 404


@bp.post("/accounts/o/review/submit")
@login_required
def review_item_submit():
    flashes = []
    data = request.json
    if data:
        item = Items.get({"id": data["itemId"]})
        review_data = {
            "item_id": item.id,
            "author_id": g.user_id,
            "body": data.get("body", "No review provided."),
            "rating": data.get("rating")
        }
        review = create_review(review_data)
        flashes.append(f"Thanks for your feedback on your {item.name} rental!")
        return {"flashes": flashes}, 200
    return {"flashes": ["No changes were received! Try again."]}, 406


@bp.post('/feedback/submit')
def feedback_submit():
    flashes = []
    data = request.json
    if data:
        feedback = {
            "link": data["href"],
            "complaint": data["feedback"],
            "user_id": data.get('userId')
        }
        issue = Issues.insert(feedback)
        flashes.append("We got your feedback! Thanks for your patience :)!")
        return {"flashes": flashes}, 200
    flashes.append(f"There was a problem receiving your feedback :(... Try again or email at hello@hubbub.shop.")
    return {"flashes": flashes}, 406


@bp.get('/accounts/o/receipt/id=<int:order_id>')
@login_required
def download_receipt(order_id):
    order = Orders.get({"id": order_id})
    if order:
        if g.user_id == order.renter_id:
            receipt = generate_receipt_json(order)
            return { "receipt": receipt }, 200
        return {"flashes": ["You're not authorized to view this receipt."]}, 406
    return {"flashes": ["This order does not exist at the moment."]}, 404
