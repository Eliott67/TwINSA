# editing_profile_airtable.py

import os
import backend_airtable.airtable_secrets as secrets
from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.user_airtable import User

# use the shared DB instance with secrets
users_db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)


def update_personal_info(user: User, name=None, age=None, country=None):
    updated_fields = {}

    if name is not None:
        user.name = name
        updated_fields["name"] = name

    if age is not None:
        try:
            age = int(age)
            user.age = age
            updated_fields["age"] = age
        except ValueError:
            # keep previous value
            pass

    if country is not None:
        user.country = country
        updated_fields["country"] = country

    if user.record_id and updated_fields:
        users_db.update_user_fields(user.record_id, updated_fields)

    return True


def update_profile_picture(user: User, picture_path):
    if not os.path.exists(picture_path):
        return False

    user.profile_picture = picture_path
    if user.record_id:
        users_db.update_user_fields(user.record_id, {"profile_picture": picture_path})
    return True


def delete_account(user: User, password):
    # use get_password for private attr
    if user.get_password() != password:
        return False

    if user.record_id:
        users_db.delete_user(user.record_id)
    return True

def edit_profile(
        identifier: str,
        name=None,
        age=None,
        country=None,
        profile_picture=None
    ):
    """
    Fonction exigée par les tests :
    - identifier : username OU record_id
    - autres champs facultatifs
    """

    # récupérer l'utilisateur (le test exige cette logique)
    user = users_db.get_user(identifier)
    if not user:
        return False

    # mise à jour des champs simples
    updated = update_personal_info(user, name=name, age=age, country=country)

    # photo ?
    if profile_picture is not None:
        pic_ok = update_profile_picture(user, profile_picture)
        updated = updated and pic_ok

    return updated