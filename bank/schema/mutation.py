import graphene
from bank.models import Payment
from django.utils.translation import gettext as _
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_relay import from_global_id


class CreatePayment(graphene.Mutation):
    class Arguments:
        amount = graphene.Float(required=True)
        method = graphene.String(required=True)
        description = graphene.String(required=True)
        atttachment_title = graphene.String()
        attachment = Upload()

    payment = graphene.Field('bank.schema.nodes.PaymentNode')
    payment_created = graphene.Boolean()

    def mutate(self, info, **kwargs):
        payment, created = Payment.objects.get_or_create(
            user=info.context.user,
            method=kwargs.get('method'),
            amount=kwargs.get('amount'),
            description=kwargs.get('description'),
        )
        if created:
            payment.attachments.create(
                title=kwargs.get('atttachment_title'),
                file=kwargs.get('attachment'),
            )

        return CreatePayment(payment=payment, payment_created=created)


class ConfirmPayment(graphene.Mutation):
    class Arguments:
        payment_id = graphene.ID(required=True)
        description = graphene.String(required=True)

    payment = graphene.Field('bank.schema.nodes.PaymentNode')
    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise GraphQLError(_('You are not allowed to do this action.'))
        payment = Payment.objects.get(
            id=from_global_id(kwargs.get('payment_id'))[1])
        payment.set_paid(kwargs.get('description'))

        return ConfirmPayment(payment=payment, ok=True)


class CancelPayment(graphene.Mutation):
    class Arguments:
        payment_id = graphene.ID(required=True)
        description = graphene.String(required=True)

    payment = graphene.Field('bank.schema.nodes.PaymentNode')
    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise GraphQLError(_('You are not allowed to do this action.'))
        payment = Payment.objects.get(
            id=from_global_id(kwargs.get('payment_id'))[1])
        payment.set_expired(kwargs.get('description'))

        return CancelPayment(payment=payment, ok=True)


class Mutation(graphene.ObjectType):
    create_payment = CreatePayment.Field()
    confirm_payment = ConfirmPayment.Field()
    cancel_payment = CancelPayment.Field()
