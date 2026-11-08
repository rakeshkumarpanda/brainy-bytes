# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "auth_demo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    LOGIN_URL="/login/",
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.http import HttpResponse
from django.test import Client
from django.urls import path

call_command("migrate", verbosity=0)                      # the tables of users, groups, permissions and sessions

# 1. Users: the password is stored only as a salted, slow hash
ann = User.objects.create_user("ann", "ann@example.com", "correct horse 42")
print("stored:", ann.password[:42], "...")
print("check:", ann.check_password("correct horse 42"), ann.check_password("wrong"))
print("authenticate:", authenticate(username="ann", password="correct horse 42"), authenticate(username="ann", password="x"))

# 2. Permissions: each model gets add, change, delete and view. Groups bundle them.
editors = Group.objects.create(name="editors")
editors.permissions.add(Permission.objects.get(codename="change_user"))
bob = User.objects.create_user("bob", password="another long one 7")
bob.groups.add(editors)
print("bob can change users?", bob.has_perm("auth.change_user"), " ann?", ann.has_perm("auth.change_user"))


# 3. Views protected by decorators
@login_required
def profile(request):
    return HttpResponse(f"Hello {request.user.username}")


@permission_required("auth.change_user", raise_exception=True)
def edit_users(request):
    return HttpResponse("You may edit users")


urlpatterns = [path("profile/", profile), path("users/edit/", edit_users)]

client = Client()
response = client.get("/profile/")
print("anonymous /profile/:", response.status_code, "->", response["Location"])
client.login(username="ann", password="correct horse 42")
print("ann /profile/:", client.get("/profile/").content.decode(), "| /users/edit/:", client.get("/users/edit/").status_code)
client.logout()
client.login(username="bob", password="another long one 7")
print("bob /users/edit/:", client.get("/users/edit/").status_code, client.get("/users/edit/").content.decode())
