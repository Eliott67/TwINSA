import os
import sys
import uuid
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from backend_airtable.user_airtable import User
from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.post_airtable_db import AirtablePostsDB
from backend_airtable.posts_airtable import PostAirtable

from backend_airtable.Login_LogoutV2_airtable import login, logout
from backend_airtable.change_password_airtable import SecureUser
from backend_airtable.editing_profile_airtable import edit_profile
from backend_airtable.feed_airtable import FeedAirtable
from backend_airtable.notification_airtable import Notification


import backend_airtable.airtable_secrets as secrets


# ======================================================
# FIXTURES : instancient les DB Airtable réelles
# ======================================================

@pytest.fixture(scope="module")
def user_db():
    return AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

@pytest.fixture(scope="module")
def post_db():
    return AirtablePostsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)


# ======================================================
# TEST 1 : CHANGE PASSWORD
# ======================================================

def test_change_password(user_db):
    # création user
    user = SecureUser(
        username="pwdtest123",
        email="pwd@test.com",
        password="Old123!"
    )
    
    rec = user_db.add_user(user)
    user.record_id = rec["id"]

    # test changement
    assert user.change_password("Old123!", "New123!")
    
    # vérifier en DB
    fetched = user_db.get_user_by_record_id(rec["id"])
    assert fetched.password == "New123!"

    user_db.delete_user(rec["id"])


# ======================================================
# TEST 2 : EDIT PROFILE
# ======================================================

def test_edit_profile(user_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"edit_{unique}",
        email=f"{unique}@example.com",
        password="Test123!",
        name="Original Name",
        age=30,
        country="FR",
    )
    rec = user_db.add_user(user)
    user_id = rec["id"]

    # apply edits
    updated = edit_profile(
        identifier=user.username,
        name="Updated Name",
        age=99,
        country="JP"
    )

    assert updated is not None
    fetched = user_db.get_user_by_record_id(user_id)

    assert fetched.name == "Updated Name"
    assert fetched.age == 99
    assert fetched.country == "JP"

    user_db.delete_user(user_id)


# ======================================================
# TEST 3 : NOTIFICATIONS
# ======================================================

def test_notifications(user_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"notif_{unique}",
        email=f"{unique}@example.com",
        password="Test123!"
    )
    rec = user_db.add_user(user)
    user_id = rec["id"]

    notif_id = Notification.create_notification(
        user_record_id=user_id,
        content="This is a test notification."
    )

    assert notif_id is not None

    notifs = Notification.get_notifications(user_id)
    assert len(notifs) >= 1
    assert "test notification" in notifs[-1]["content"].lower()

    user_db.delete_user(user_id)


# ======================================================
# TEST 4 : FEED (si ton feed inclut les posts de tous)
# ======================================================

def test_feed(user_db, post_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"feed_{unique}",
        email=f"{unique}@example.com",
        password="Test123!"
    )
    rec = user_db.add_user(user)
    user_id = rec["id"]

    # create some posts
    p1 = PostAirtable(owner_record_id=user_id, content="Feed Test 1")
    p2 = PostAirtable(owner_record_id=user_id, content="Feed Test 2")

    r1 = post_db.add_post(p1)
    r2 = post_db.add_post(p2)

    feed = FeedAirtable.build_feed()

    contents = [item["content"] for item in feed]
    assert "Feed Test 1" in contents
    assert "Feed Test 2" in contents

    # cleanup
    post_db.delete_post(r1["id"])
    post_db.delete_post(r2["id"])
    user_db.delete_user(user_id)


# ======================================================
# TEST 5 : UPDATE & DELETE POST
# ======================================================

def test_update_and_delete_post(user_db, post_db):
    unique = str(uuid.uuid4())[:8]

    user = User(
        username=f"updpost_{unique}",
        email=f"{unique}@example.com",
        password="Test123!"
    )
    urec = user_db.add_user(user)
    user_id = urec["id"]

    p = PostAirtable(owner_record_id=user_id, content="Original")
    prec = post_db.add_post(p)
    post_id = prec["id"]

    # update
    post_db.update_post_fields(post_id, {"content": "Updated!"})
    updated = post_db.get_post(post_id)
    assert updated.content == "Updated!"

    # delete
    deleted = post_db.delete_post(post_id)
    assert deleted

    user_db.delete_user(user_id)
