from calendar import month
from django.conf import settings
from django.http.response import HttpResponse
import stripe
from bank.models import Conta
from core.models import Pagamento, Socio
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings


# Stripe webhook handler
def core_webhook(request):
    endpoint_secret = settings.CORE_WEBHOOK_SECRET
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

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        if checkout_session['mode'] == 'subscription':
            pagamento = Pagamento.objects.filter(
                checkout_id=checkout_session['id']).first()

            pagamento.status = checkout_session['status']

            socio = pagamento.socio
            socio.is_socio = True

            # Verificar e adicionar data_inicio e data_fim
            stripe.api_key = settings.STRIPE_API_KEY
            subscription = stripe.Subscription.list(
                customer=socio.stripe_customer_id,
                status='active'
            )

            if len(subscription.data) > 0:
                socio.stripe_subscription_id = subscription.data[0]['id']

                if not socio.data_inicio:
                    socio.data_inicio = datetime.fromtimestamp(
                        subscription.data[0]['current_period_start'])

                current_period_end = datetime.fromtimestamp(
                    subscription.data[0]['current_period_end'])

                socio.data_fim = current_period_end
                stripe.Subscription.modify(
                    f'{socio.stripe_subscription_id}',
                    proration_behavior='none'
                )

                if current_period_end.year > datetime.now().year:
                    socio.data_fim = datetime(
                        datetime.now().year, 12, 31, 23, 59, 59
                    )
                    stripe.Subscription.modify(
                        f'{socio.stripe_subscription_id}',
                        cancel_at=socio.data_fim,
                        proration_behavior='none'
                    )
                elif current_period_end - datetime.now() > timedelta(days=31):
                    if datetime.now().month < 7:
                        if current_period_end.month > 6:
                            socio.data_fim = datetime(
                                datetime.now().year, 6, 30, 23, 59, 59
                            )
                            stripe.Subscription.modify(
                                f'{socio.stripe_subscription_id}',
                                cancel_at=socio.data_fim,
                                proration_behavior='none'
                            )

            socio.save()
            pagamento.save()

            conta, _ = Conta.objects.get_or_create(socio=socio)
            if conta.socio.is_socio:
                conta.calangos += int(
                    ((checkout_session['amount_total'] / 100) // 5 * 50))
            conta.save()

    # Handle the customer.subscription.deleted event
    if event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']

        socio = Socio.objects.filter(
            stripe_customer_id=subscription['customer']).first()

        socio.is_socio = False
        socio.data_fim = timezone.now()
        socio.save()

    return HttpResponse(status=200)
