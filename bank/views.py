import stripe
from core.models import Socio
from django.conf import settings
from django.http.response import HttpResponse
from django.utils import timezone

from .models import Conta, Movimentacao, Payment


def bank_webhook(request):
    endpoint_secret = settings.BANK_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    if event['type'] == 'checkout.session.completed':
        try:
            checkout_session = event['data']['object']

            if checkout_session['mode'] == 'subscription':
                if checkout_session['payment_status'] == 'paid':
                    payment = Payment.objects.get(
                        description=checkout_session['id'])
                    payment.set_paid('Subscription creation')

            if checkout_session['mode'] == 'payment':
                pass

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(content=e, status=400)

    if event['type'] == 'checkout.session.expired':
        try:
            checkout_session = event['data']['object']

            payment = Payment.objects.get(
                description=checkout_session['id'])
            payment.set_expired('Session expired')

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(content=e, status=400)

    return HttpResponse(status=204)
