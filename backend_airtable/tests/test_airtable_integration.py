import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import uuid
import pytest
from datetime import datetime

from backend_airtable.user_airtable import User
from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.post_airtable_db import AirtablePostsDB
from backend_airtable.posts_airtable import PostAirtable
import backend_airtable.airtable_secrets as secrets


# ============================================
# FIXTURES : instancient les DB réelles Airtable
# ============================================

@pytest.fixture(scope="module")
def user_db():
    return AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

@pytest.fixture(scope="module")
def post_db():
    return AirtablePostsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)


# ============================================
# TEST 1 : CREATION + FETCH D’UN USER
# ============================================

def test_create_and_fetch_user(user_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique}",
        email=f"{unique}@example.com",
        password="Test123!",
        name="Integration Tester",
        age=25,
        country="France"
    )

    rec = user_db.add_user(user)
    assert "id" in rec, "Airtable n’a pas renvoyé d’ID !"
    user_id = rec["id"]

    fetched = user_db.get_user_by_record_id(user_id)

    assert fetched is not None
    assert fetched.username == user.username
    assert fetched.email == user.email

    # cleanup
    user_db.delete_user(user_id)


# ============================================
# TEST 2 : RECHERCHE PAR USERNAME + EMAIL
# ============================================

def test_find_user(user_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"searchtest_{unique}",
        email=f"search_{unique}@example.com",
        password="Test123!"
    )

    rec = user_db.add_user(user)
    user_id = rec["id"]

    by_username = user_db.get_user_by_username(user.username)
    assert by_username is not None
    assert by_username.email == user.email

    by_email = user_db.get_user_by_email(user.email)
    assert by_email is not None
    assert by_email.username == user.username

    # cleanup
    user_db.delete_user(user_id)


# ============================================
# TEST 3 : LOGIN REEL
# ============================================

def test_real_login(user_db):
    from backend_airtable.Login_LogoutV2_airtable import login, logout

    unique = str(uuid.uuid4())[:8]
    pwd = "Test123!"
    user = User(
        username=f"logintest_{unique}",
        email=f"log_{unique}@example.com",
        password=pwd
    )

    rec = user_db.add_user(user)

    logged = login(identifier=user.username, password=pwd)
    assert logged is not None
    assert logged.username == user.username

    logout(logged)

    # cleanup
    user_db.delete_user(rec["id"])


# ============================================
# TEST 4 : CREATION D’UN POST
# ============================================

def test_create_post(user_db, post_db):
    # create a user first
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"poster_{unique}",
        email=f"poster_{unique}@example.com",
        password="Test123!"
    )
    user_rec = user_db.add_user(user)
    user_id = user_rec["id"]

    post = PostAirtable(
        owner_record_id=user_id,
        content="Hello from integration test!",
        images=[]
    )

    post_rec = post_db.add_post(post)
    assert "id" in post_rec
    post_id = post_rec["id"]

    fetched = post_db.get_post(post_id)
    assert fetched.content == post.content
    assert fetched.owner_record_id == user_id

    # cleanup
    post_db.delete_post(post_id)
    user_db.delete_user(user_id)


# ============================================
# TEST 5 : GET POSTS BY USER
# ============================================

def test_get_posts_by_user(user_db, post_db):
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"postlist_{unique}",
        email=f"postlist_{unique}@example.com",
        password="Test123!"
    )
    user_rec = user_db.add_user(user)
    user_id = user_rec["id"]

    # Create 2 posts
    p1 = PostAirtable(owner_record_id=user_id, content="Post A")
    p2 = PostAirtable(owner_record_id=user_id, content="Post B")

    r1 = post_db.add_post(p1)
    r2 = post_db.add_post(p2)

    posts = post_db.get_posts_by_user(user_id)
    assert len(posts) >= 2, "Airtable n’a pas renvoyé les 2 posts !"

    # cleanup
    post_db.delete_post(r1["id"])
    post_db.delete_post(r2["id"])
    user_db.delete_user(user_id)
