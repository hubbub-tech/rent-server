import os

TAX = 0.08875
DEPOSIT = 0.25
DISCOUNT = 0.35
GRACE_LIMIT = 2
PENALTY_LIMIT = 14

PAYEE_ID = 32
DAYS_SERVICE_BUFFER = 2 # from datetime.now()
JSON_DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
COOKIE_KEY_CART = "cartSize"
COOKIE_KEY_USER_ID = "userId"
COOKIE_KEY_SESSION = "sessionToken"
ReCAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

GOOGLE_MAPS_APIKEY = os.getenv("GOOGLE_MAPS_APIKEY")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
CLIENT_DOMAIN = os.getenv("CORS_ALLOW_ORIGIN")
