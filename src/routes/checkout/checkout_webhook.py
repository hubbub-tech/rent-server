import stripe
from flask import Blueprint, make_response, request, redirect, g

from src.models import Charges, Promos
from src.models import Orders, Extensions

from src.utils import create_charge
from src.utils.settings import STRIPE_ENDPOINT_SECRET, PAYEE_ID, SERVER_DOMAIN

bp = Blueprint("webhook", __name__)

@bp.post('/checkout/stripe/payment-wh')
def checkout_webhook():

    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return 500
        # raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 401
        # raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
      checkout_session = event['data']['object']

      client_reference_id = checkout_session.get('client_reference_id')

      if client_reference_id:
          attr_key, attr_value = client_reference_id.split(":")
      else:
          return 400

      if attr_key == "orders_checkout_session_key":
          checkout_session_key = attr_value
      else:
          return redirect(f"{SERVER_DOMAIN}/extensions/stripe/payment-wh", code=302)

      line_items = checkout_session['line_items']

      # Get order-bundle subtotal
      orders = Orders.filter({ "checkout_session_key": checkout_session_key })

      charge_data = {
        "amount": checkout_session['amount_subtotal'],
        "currency": checkout_session['currency'],
        "txn_token": checkout_session['client_reference_id'],
        "txn_processor": "stripe",
        "is_paid": True,
        "payer_id": orders[0].renter_id,
        "payee_id": PAYEE_ID
      }

      Charges.insert(charge_data)

      # Get order-delivery charge
      total_details = checkout_session["total_details"]

      amount_delivery = total_details["amount_shipping"]

      if amount_delivery > 0:
          delivery_charge_data = {
            "amount": amount_shipping,
            "currency": checkout_session['currency'],
            "txn_token": checkout_session['client_reference_id'],
            "txn_processor": "stripe",
            "is_paid": True,
            "payer_id": orders[0].renter_id,
            "payee_id": PAYEE_ID
          }

          Charges.insert(delivery_charge_data)

    response = make_response({ 'message': "Created a charge." }, 200)
    return response


@bp.post('/extensions/stripe/payment-wh')
def extension_webhook():

    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return 500
        # raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 401
        # raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
      checkout_session = event['data']['object']

      client_reference_id = checkout_session['client_reference_id']
      attr_key, attr_value = client_reference_id.split(":")

      if attr_key == "orders_id":
          order_id = attr_value
      else:
          return 401

      order = Orders.get({ "id": order_id })

      line_items = checkout_session['line_items']

      # Get order-bundle subtotal
      orders = Orders.filter({ "checkout_session_key": client_reference_id })

      charge_data = {
        "amount": checkout_session['amount_subtotal'],
        "currency": checkout_session['currency'],
        "txn_token": checkout_session['client_reference_id'],
        "txn_processor": "stripe",
        "is_paid": True,
        "payer_id": order.renter_id,
        "payee_id": PAYEE_ID
      }

      Charges.insert(charge_data)

    response = make_response({ 'message': "Created a charge." }, 200)
    return response
