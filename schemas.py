from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    """ Schema for user validation """
    first_name = fields.Str(required=True, validate=validate.Length(
        min=1, error="First name can't be empty."))
    last_name = fields.Str(required=True, validate=validate.Length(
        min=1, error="Last name can't be empty."))
    phone_number = fields.Str(required=True, validate=[validate.Length(min=1, error="Phone number can't be empty."), validate.Regexp(
        '^\+(?:[0-9]){6,14}[0-9]$', error="Must be a valid phone number with country code.")])
    date_of_birth = fields.DateTime(required=True)


class MessageSchema(Schema):
    """ Schema for message validation """
    message = fields.Str(required=True, validate=validate.Length(
        min=1, error="Message can't be blank."))
    phone_number = fields.Str(required=True, validate=[validate.Length(min=1, error="Phone number can't be empty."), validate.Regexp(
        '^\+(?:[0-9]){6,14}[0-9]$', error="Must be a valid phone number with country code.")])
    token = fields.Str(required=True, validate=validate.Length(
        min=1, error="Token can't be empty."))
