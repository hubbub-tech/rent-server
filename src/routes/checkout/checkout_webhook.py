import stripe
from flask import Blueprint, make_response, request, jsonify, g

from src.utils import create_charge
from src.utils.settings import STRIPE_ENDPOINT_SECRET

bp = Blueprint("webhook", __name__)

@bp.post('/checkout/webhook')
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
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
      checkout_session = event['data']['object']

      amount = checkout_session['amount_total'] / 100
      charge_data = {
        "notes": "",
        "amount": amount,
        "currency": "usd",
        "checkout_session_key": checkout_session['client_reference_id'],
        "txn_processor": f"stripe-{checkout_session['id']}",
        "is_paid": True,
        "order_id": None,
        "payee_id": None,
        "payer_id": None,
        "issue_id": None
      }

      charge = create_charge(charge_data)

    else:
      print('Do something different...')

    response = make_response({ 'messages': ["Created charge."] }, 200)
    return response
