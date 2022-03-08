from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
import stripe
from bank.models import Conta
from django.conf import settings

from eventos.models import Ingresso


# Stripe webhook handler
def eventos_webhook(request):
    endpoint_secret = settings.EVENTOS_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']

        if checkout_session['mode'] == 'payment' and checkout_session['payment_status'] == 'paid':
            try:
                ingresso = Ingresso.objects.get(
                    stripe_checkout_id=checkout_session['id'])

                ingresso.set_paid()
                ingresso.save()

            except Ingresso.DoesNotExist:
                return HttpResponse(content=Ingresso.objects.none(), status=204)
            except ValidationError as e:
                return HttpResponse(content=e, status=400)
        else:
            return HttpResponse(status=204)

    if event['type'] == 'checkout.session.expired':
        checkout_session = event['data']['object']

        if checkout_session['mode'] == 'payment':
            try:
                ingresso = Ingresso.objects.get(
                    stripe_checkout_id=checkout_session['id'])

                ingresso.set_expired()
                ingresso.save()

            except Ingresso.DoesNotExist:
                return HttpResponse(content=Ingresso.objects.none(), status=204)
            except ValidationError as e:
                return HttpResponse(content=e, status=400)
            except Exception as e:
                return HttpResponse(content=e, status=400)
        else:
            return HttpResponse(status=204)

    if event['type'] == 'checkout.session.async_payment_succeeded':
        checkout_session = event['data']['object']

        if checkout_session['mode'] == 'payment':
            try:
                ingresso = Ingresso.objects.get(
                    stripe_checkout_id=checkout_session['id'])

                ingresso.set_paid()
                ingresso.save()

            except Ingresso.DoesNotExist:
                return HttpResponse(content=Ingresso.objects.none(), status=204)
            except ValidationError as e:
                return HttpResponse(content=e, status=400)
        else:
            return HttpResponse(status=204)

    if event['type'] == 'checkout.session.async_payment_failed':
        checkout_session = event['data']['object']

        if checkout_session['mode'] == 'payment':
            try:
                ingresso = Ingresso.objects.get(
                    stripe_checkout_id=checkout_session['id'])

                ingresso.set_expired()
                ingresso.save()

            except Ingresso.DoesNotExist:
                return HttpResponse(content=Ingresso.objects.none(), status=204)
            except ValidationError as e:
                return HttpResponse(content=e, status=400)
            except Exception as e:
                return HttpResponse(content=e, status=400)
        else:
            return HttpResponse(status=204)

    return HttpResponse(status=200)
