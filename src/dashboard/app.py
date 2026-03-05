from flask import Flask, render_template, jsonify, request, redirect
import os
import psutil
import platform
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/')
def index():
    return render_template('index.html', publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

@app.route('/api/stats')
def stats():
    return jsonify({
        "status": "Online",
        "cpu": f"{psutil.cpu_percent()}%",
        "ram": f"{psutil.virtual_memory().percent}%",
        "platform": platform.system(),
        "version": "1.0.0"
    })

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'AnnaBot Premium',
                        },
                        'unit_amount': 999,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    return "<h1>Payment Successful! Welcome to Premium.</h1>"

@app.route('/cancel')
def cancel():
    return "<h1>Payment Cancelled.</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
