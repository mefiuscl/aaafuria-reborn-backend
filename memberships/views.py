import stripe
from django.conf import settings
from django.http.response import HttpResponse

from .models import Attachment


def memberships_webhook(request):
    endpoint_secret = settings.MEMBERSHIPS_WEBHOOK_SECRET
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

    if event['type'] == 'customer.subscription.deleted':
        try:
            subscription = event['data']['object']
            membership = Attachment.objects.get(
                content=subscription['id']).membership
            membership.refresh()

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(content=e, status=400)
    if event['type'] == 'customer.subscription.update':
        try:
            subscription = event['data']['object']
            membership = Attachment.objects.get(
                content=subscription['id']).membership
            membership.refresh()

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(content=e, status=400)

    return HttpResponse(status=204)
