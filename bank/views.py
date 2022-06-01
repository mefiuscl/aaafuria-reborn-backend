import stripe
from django.conf import settings
from django.http.response import HttpResponse
from memberships.models import Attachment, Membership

from .models import Payment


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
            chechout_session = event['data']['object']

            if chechout_session['mode'] == 'subscription':
                if chechout_session['payment_status'] == 'paid':
                    payment = Payment.objects.get(
                        description=chechout_session['id'])
                    payment.membership.attachments.get_or_create(
                        title='stripe_subscription_id',
                        content=chechout_session['subscription'])

                    payment.set_paid('Subscription creation')

                    return HttpResponse(status=200)

            if chechout_session['mode'] == 'payment':
                pass

            return HttpResponse(status=200)
        except Exception as e:
            print(e)
            return HttpResponse(content=e, status=400)

    if event['type'] == 'invoice.paid':
        try:
            chechout_session = event['data']['object']

            if chechout_session['billing_reason'] == 'subscription_cycle':
                if chechout_session['status'] == 'paid':
                    membership = Attachment.objects.get(
                        content=chechout_session['subscription']).membership

                    payment = Payment.objects.create(
                        user=membership.member.user,
                        method=Payment.STRIPE,
                        amount=chechout_session['amount_paid'],
                        description=chechout_session['id'],
                    )

                    payment.set_paid('Subscription cycle')

                    membership.payment = payment
                    membership.refresh()

                    return HttpResponse(status=200)

            if chechout_session['mode'] == 'payment':
                pass

            return HttpResponse(status=200)
        except Exception as e:
            print(e)
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
