from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordLengthValidator:
    def __init__(self, length=6):
        self.length = length

    def validate(self, password, user=None):
        if len(password) != self.length:
            raise ValidationError(
                _("This password must contain exactly %(length)d numbers."),
                code='password_wrong_length',
                params={'length': self.length},
            )

    def get_help_text(self):
        return _(
            "Your password must contain exactly %(length)d numbers."
            % {'length': self.length}
        )


class PasswordOnlyNumericValidator:
    def validate(self, password, user=None):
        if not password.isnumeric():
            raise ValidationError(
                _("This password must contain only numbers."),
                code='password_not_numeric',
            )

    def get_help_text(self):
        return _(
            "Your password must contain only numbers."
        )
