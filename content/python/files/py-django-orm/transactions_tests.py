# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "transactions_tests" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import sys
import unittest

import django
from django.apps import AppConfig
from django.conf import settings


class BankConfig(AppConfig):
    name = "__main__"
    label = "bank"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.BankConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models, transaction
from django.db.models import F
from django.test import TestCase


class Account(models.Model):
    owner = models.CharField(max_length=50)
    balance = models.IntegerField(default=0)                       # in cents, never a float for money


class NotEnoughMoney(Exception):
    pass


def transfer(from_id, to_id, cents):
    """Move money between two accounts: both changes happen, or neither does."""
    with transaction.atomic():
        Account.objects.filter(pk=to_id).update(balance=F("balance") + cents)
        sender = Account.objects.get(pk=from_id)
        if sender.balance < cents:
            raise NotEnoughMoney(f"{sender.owner} has only {sender.balance}")   # rolls back the update above
        Account.objects.filter(pk=from_id).update(balance=F("balance") - cents)


with connection.schema_editor() as editor:
    editor.create_model(Account)


# ---------- tests.py: each test runs inside a transaction that is rolled back afterwards ----------
class TransferTests(TestCase):
    @classmethod
    def setUpTestData(cls):                                         # runs once for the whole class
        cls.ann = Account.objects.create(owner="ann", balance=5000)
        cls.bob = Account.objects.create(owner="bob", balance=1000)

    def balances(self):
        return list(Account.objects.order_by("owner").values_list("balance", flat=True))

    def test_transfer_moves_money(self):
        transfer(self.ann.pk, self.bob.pk, 1500)
        self.assertEqual(self.balances(), [3500, 2500])

    def test_not_enough_money_changes_nothing(self):
        with self.assertRaises(NotEnoughMoney):
            transfer(self.bob.pk, self.ann.pk, 9999)
        self.assertEqual(self.balances(), [5000, 1000])           # bob was NOT paid half a transfer

    def test_each_test_starts_clean(self):
        self.assertEqual(self.balances(), [5000, 1000])           # the transfer of the first test is gone

    def test_query_count(self):
        with self.assertNumQueries(5):     # SAVEPOINT, UPDATE, SELECT, UPDATE, RELEASE (atomic inside a test)
            transfer(self.ann.pk, self.bob.pk, 1)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransferTests)
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
print("all passed" if result.wasSuccessful() else "some tests failed")
