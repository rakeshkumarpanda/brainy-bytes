# 5.1 Django REST framework: JSON APIs on top of Django
# Example "auth_permissions" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework",
                    "rest_framework.authtoken", "__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
        "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
        "DEFAULT_THROTTLE_RATES": {"anon": "3/minute"},
    },
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, models
from django.urls import include, path
from rest_framework import permissions, serializers, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient

call_command("migrate", verbosity=0)                       # users and tokens


class Note(models.Model):
    text = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


with connection.schema_editor() as editor:
    editor.create_model(Note)


class IsOwnerOrReadOnly(permissions.BasePermission):        # a permission of your own, checked per object
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.owner == request.user


class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Note
        fields = ["id", "text", "owner"]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.order_by("id")
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):                   # the owner comes from the token, never from the body
        serializer.save(owner=self.request.user)


router = DefaultRouter()
router.register("notes", NoteViewSet)
urlpatterns = [path("api/", include(router.urls)), path("api/token/", obtain_auth_token)]

User.objects.create_user("ann", password="ann secret 123")
User.objects.create_user("bob", password="bob secret 456")


def show(label, response):
    print(f"{label:34} {response.status_code} {response.json() if response.content else None}")


anon = APIClient()
show("anon POST /api/notes/", anon.post("/api/notes/", {"text": "hi"}, format="json"))
show("anon POST /api/token/ (wrong pw)", anon.post("/api/token/", {"username": "ann", "password": "nope"}, format="json"))
token = anon.post("/api/token/", {"username": "ann", "password": "ann secret 123"}, format="json").json()["token"]
print("ann's token:", token[:8] + "...", "stored:", Token.objects.filter(user__username="ann").exists())

ann = APIClient()
ann.credentials(HTTP_AUTHORIZATION="Token " + token)       # sent with every request from now on
show("ann POST /api/notes/", ann.post("/api/notes/", {"text": "buy milk", "owner": "bob"}, format="json"))

bob = APIClient()
bob.force_authenticate(User.objects.get(username="bob"))    # a test shortcut: no token needed
show("bob GET /api/notes/1/", bob.get("/api/notes/1/"))
show("bob DELETE /api/notes/1/", bob.delete("/api/notes/1/"))
show("ann PATCH /api/notes/1/", ann.patch("/api/notes/1/", {"text": "buy oat milk"}, format="json"))

throttled = APIClient()
for i in range(4):                                          # anonymous users may make 3 requests a minute
    response = throttled.get("/api/notes/")
    print(f"anon GET #{i + 1}: {response.status_code}", response.get("Retry-After", ""))
