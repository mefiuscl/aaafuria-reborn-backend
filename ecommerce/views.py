from django.http.response import HttpResponse
import stripe
from django.shortcuts import render
from bank.models import Conta
from ecommerce.models import Carrinho, Pagamento
from django.conf import settings


# Stripe webhook handler
def ecommerce_webhook(request):
    endpoint_secret = settings.ECOMMERCE_WEBHOOK_SECRET
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
                carrinho = Carrinho.objects.get(
                    stripe_checkout_id=checkout_session['id'])

                pagamento = Pagamento.objects.create(
                    user=carrinho.user,
                    carrinho=carrinho,
                    status='pago',
                    valor=carrinho.total,
                    forma_pagamento='cartao'
                )

                carrinho.set_paid()
                carrinho.save()

                pagamento.save()

            except Carrinho.DoesNotExist:
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(content=e, status=400)
        else:
            return HttpResponse(status=204)
    else:
        return HttpResponse(status=204)

    return HttpResponse(status=200)
