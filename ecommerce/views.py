from django.http.response import HttpResponse
import stripe
from django.shortcuts import render
from ecommerce.models import Carrinho
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

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']

        carrinho = Carrinho.objects.filter(
            stripe_checkout_id=checkout_session['customer']).first()

        for produto_pedido in carrinho.produtos.all():
            if not produto_pedido.produto.has_variations:
                produto_pedido.produto.estoque -= produto_pedido.quantidade
                produto_pedido.produto.save()
            else:
                produto_pedido.variacao.estoque -= produto_pedido.quantidade
                produto_pedido.variacao.save()

            produto_pedido.ordered = True
            produto_pedido.save()

        carrinho.set_paid()
        carrinho.save()

    return HttpResponse(status=200)
