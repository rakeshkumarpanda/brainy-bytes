# 4.2 Django in depth: ORM, migrations, forms, users and tests
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== 1683. Invalid Tweets (Easy)
# https://leetcode.com/problems/invalid-tweets/
# Pattern: annotate(Length(...)) then filter
# Idea: A computed column: annotate each tweet with the length of its text, then keep the ones
# longer than 15.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models.functions import Length


class Tweet(models.Model):
    tweet_id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=500)


def invalid_tweets(rows):
    load(Tweet, rows)
    long_ones = Tweet.objects.annotate(size=Length("content")).filter(size__gt=15)
    return sorted(long_ones.values_list("tweet_id", flat=True))


# ================================================================== 1378. Replace Employee ID With The Unique Identifier (Easy)
# https://leetcode.com/problems/replace-employee-id-with-the-unique-identifier/
# Pattern: Subquery with OuterRef, a LEFT JOIN without a ForeignKey
# Idea: The two tables share an id but have no ForeignKey. A Subquery that looks up the unique id
# for each employee works like a LEFT JOIN, and gives None when there is no match.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import OuterRef, Subquery


class Employee(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class EmployeeUNI(models.Model):
    id = models.IntegerField(primary_key=True)
    unique_id = models.IntegerField()


def replace_employee_id(employees, uni):
    load(Employee, employees)
    load(EmployeeUNI, uni)
    match = EmployeeUNI.objects.filter(id=OuterRef("id")).values("unique_id")[:1]
    rows = Employee.objects.annotate(unique_id=Subquery(match)).order_by("name")
    return [[row.unique_id, row.name] for row in rows]


# ================================================================== 1068. Product Sales Analysis I (Easy)
# https://leetcode.com/problems/product-sales-analysis-i/
# Pattern: Follow a ForeignKey inside values()
# Idea: With a ForeignKey, product__product_name in values() makes Django write the JOIN for you.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=50)


class Sale(models.Model):
    sale_id = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    year = models.IntegerField()
    price = models.IntegerField()


def sales_analysis(sales, products):
    load(Product, products)
    load(Sale, sales)                    # product_id fills the ForeignKey
    rows = Sale.objects.order_by("sale_id").values_list("product__product_name", "year", "price")
    return [list(row) for row in rows]


# ================================================================== 1661. Average Time of Process per Machine (Easy)
# https://leetcode.com/problems/average-time-of-process-per-machine/
# Pattern: Conditional aggregation with Sum(Case(When(...)))
# Idea: Group by machine. Add the end times and subtract the start times with Case and When, then
# divide by the number of processes.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import Case, Count, F, FloatField, Sum, When


class Activity(models.Model):
    machine_id = models.IntegerField()
    process_id = models.IntegerField()
    activity_type = models.CharField(max_length=5)
    timestamp = models.FloatField()


def average_processing_time(rows):
    load(Activity, rows)
    signed = Case(When(activity_type="end", then=F("timestamp")), default=-F("timestamp"), output_field=FloatField())
    groups = (Activity.objects.values("machine_id")
              .annotate(total=Sum(signed), processes=Count("process_id", distinct=True))
              .order_by("machine_id"))
    return [[g["machine_id"], round(g["total"] / g["processes"], 3)] for g in groups]


# ================================================================== 1280. Students and Examinations (Easy)
# https://leetcode.com/problems/students-and-examinations/
# Pattern: Count per group, then fill in the zeros
# Idea: Every student must appear with every subject, even with 0 exams. Count the exams per
# (student, subject) with values() and annotate(), then loop over all pairs.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import Count


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    student_name = models.CharField(max_length=50)


class Subject(models.Model):
    subject_name = models.CharField(max_length=50, primary_key=True)


class Examination(models.Model):
    student_id = models.IntegerField()
    subject_name = models.CharField(max_length=50)


def students_and_examinations(students, subjects, exams):
    load(Student, students)
    load(Subject, subjects)
    load(Examination, exams)
    counts = {}
    for row in Examination.objects.values("student_id", "subject_name").annotate(n=Count("id")):
        counts[(row["student_id"], row["subject_name"])] = row["n"]
    result = []
    for student in Student.objects.order_by("student_id"):
        for subject in Subject.objects.order_by("subject_name"):
            key = (student.student_id, subject.subject_name)
            result.append([student.student_id, student.student_name, subject.subject_name, counts.get(key, 0)])
    return result


# ================================================================== 1251. Average Selling Price (Easy)
# https://leetcode.com/problems/average-selling-price/
# Pattern: Subquery for the price on the sale date, then a weighted average
# Idea: Each sale needs the price that was valid on its date. A Subquery with OuterRef and two date
# lookups finds it, then Sum(price times units) / Sum(units) gives the weighted average.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import F, OuterRef, Subquery, Sum


class Price(models.Model):
    product_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.IntegerField()


class UnitSold(models.Model):
    product_id = models.IntegerField()
    purchase_date = models.DateField()
    units = models.IntegerField()


def average_selling_price(prices, sold):
    load(Price, prices)
    load(UnitSold, sold)
    price_then = Price.objects.filter(product_id=OuterRef("product_id"), start_date__lte=OuterRef("purchase_date"),
                                      end_date__gte=OuterRef("purchase_date")).values("price")[:1]
    totals = (UnitSold.objects.annotate(price=Subquery(price_then)).values("product_id")
              .annotate(money=Sum(F("price") * F("units")), units_total=Sum("units")))
    found = {row["product_id"]: round(row["money"] / row["units_total"], 2) for row in totals}
    products = sorted(set(Price.objects.values_list("product_id", flat=True)))
    return [[product, found.get(product, 0)] for product in products]


# ================================================================== 1211. Queries Quality and Percentage (Easy)
# https://leetcode.com/problems/queries-quality-and-percentage/
# Pattern: Avg of a computed value and Count with a filter
# Idea: Group by query name. Avg(rating / position) gives the quality, and Count with
# filter=Q(rating__lt=3) counts the poor results.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import Avg, Count, F, FloatField, Q
from django.db.models.functions import Cast


class QueryResult(models.Model):
    query_name = models.CharField(max_length=30)
    result = models.CharField(max_length=50)
    position = models.IntegerField()
    rating = models.IntegerField()


def queries_stats(rows):
    load(QueryResult, rows)
    groups = (QueryResult.objects.values("query_name")
              .annotate(quality=Avg(Cast("rating", FloatField()) / F("position")),
                        poor=Count("id", filter=Q(rating__lt=3)), total=Count("id"))
              .order_by("query_name"))
    return [[g["query_name"], round(g["quality"], 2), round(100 * g["poor"] / g["total"], 2)] for g in groups]


# ================================================================== 607. Sales Person (Easy)
# https://leetcode.com/problems/sales-person/
# Pattern: exclude with a subquery of ids
# Idea: Find the sales people with an order for the company RED, as a QuerySet of ids, and exclude
# them. Django puts the inner query into one SQL statement with NOT IN.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

class SalesPerson(models.Model):
    sales_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class Company(models.Model):
    com_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class SalesOrder(models.Model):
    order_id = models.IntegerField(primary_key=True)
    com_id = models.IntegerField()
    sales_id = models.IntegerField()


def sales_person(people, companies, orders):
    load(SalesPerson, people)
    load(Company, companies)
    load(SalesOrder, orders)
    red = Company.objects.filter(name="RED").values("com_id")
    sold_to_red = SalesOrder.objects.filter(com_id__in=red).values("sales_id")
    return sorted(SalesPerson.objects.exclude(sales_id__in=sold_to_red).values_list("name", flat=True))


# ================================================================== 1193. Monthly Transactions I (Medium)
# https://leetcode.com/problems/monthly-transactions-i/
# Pattern: Group by a computed month, Count and Sum with filters
# Idea: Annotate each row with its month (the first 7 characters of the date), group by month and
# country, and use filter=Q(state="approved") inside Count and Sum.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce, Substr


class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    amount = models.IntegerField()
    trans_date = models.CharField(max_length=10)


def monthly_transactions(rows):
    load(Transaction, rows)
    approved = Q(state="approved")
    groups = (Transaction.objects.annotate(month=Substr("trans_date", 1, 7)).values("month", "country")
              .annotate(trans_count=Count("id"), approved_count=Count("id", filter=approved),
                        trans_total=Sum("amount"), approved_total=Coalesce(Sum("amount", filter=approved), 0))
              .order_by("month", "country"))
    return [[g["month"], g["country"], g["trans_count"], g["approved_count"], g["trans_total"], g["approved_total"]] for g in groups]


# ================================================================== 1174. Immediate Food Delivery II (Medium)
# https://leetcode.com/problems/immediate-food-delivery-ii/
# Pattern: Subquery for the first order of each customer
# Idea: Find each customer's first order date with a Subquery that sorts by date and takes one row,
# keep only those first orders, then count how many were delivered on the day they were ordered.

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])

from django.db.models import F, OuterRef, Subquery


class Delivery(models.Model):
    delivery_id = models.IntegerField(primary_key=True)
    customer_id = models.IntegerField()
    order_date = models.DateField()
    customer_pref_delivery_date = models.DateField()


def immediate_percentage(rows):
    load(Delivery, rows)
    first_date = Delivery.objects.filter(customer_id=OuterRef("customer_id")).order_by("order_date").values("order_date")[:1]
    first_orders = Delivery.objects.filter(order_date=Subquery(first_date))
    immediate = first_orders.filter(customer_pref_delivery_date=F("order_date")).count()
    return round(100 * immediate / first_orders.count(), 2)


if __name__ == "__main__":
    results = []
    results.append(check("1683. Invalid Tweets", [('invalid_tweets([{"tweet_id": 1, "content": "Let us Code"}, {"tweet_id": 2, "content": "More than fifteen chars are here!"}])', [2])]))
    results.append(check("1378. Replace Employee ID With The Unique Identifier", [('replace_employee_id([{"id": 1, "name": "Alice"}, {"id": 7, "name": "Bob"}, {"id": 11, "name": "Meir"}, {"id": 90, "name": "Winston"}, {"id": 3, "name": "Jonathan"}], [{"id": 3, "unique_id": 1}, {"id": 11, "unique_id": 2}, {"id": 90, "unique_id": 3}])', [[None, 'Alice'], [None, 'Bob'], [1, 'Jonathan'], [2, 'Meir'], [3, 'Winston']])]))
    results.append(check("1068. Product Sales Analysis I", [('sales_analysis([{"sale_id": 1, "product_id": 100, "year": 2008, "price": 5000}, {"sale_id": 2, "product_id": 100, "year": 2009, "price": 5000}, {"sale_id": 7, "product_id": 200, "year": 2011, "price": 9000}], [{"product_id": 100, "product_name": "Nokia"}, {"product_id": 200, "product_name": "Apple"}, {"product_id": 300, "product_name": "Samsung"}])', [['Nokia', 2008, 5000], ['Nokia', 2009, 5000], ['Apple', 2011, 9000]])]))
    results.append(check("1661. Average Time of Process per Machine", [('average_processing_time([{"machine_id": 0, "process_id": 0, "activity_type": "start", "timestamp": 0.712}, {"machine_id": 0, "process_id": 0, "activity_type": "end", "timestamp": 1.52}, {"machine_id": 0, "process_id": 1, "activity_type": "start", "timestamp": 3.14}, {"machine_id": 0, "process_id": 1, "activity_type": "end", "timestamp": 4.12}, {"machine_id": 1, "process_id": 0, "activity_type": "start", "timestamp": 0.55}, {"machine_id": 1, "process_id": 0, "activity_type": "end", "timestamp": 1.55}, {"machine_id": 1, "process_id": 1, "activity_type": "start", "timestamp": 0.43}, {"machine_id": 1, "process_id": 1, "activity_type": "end", "timestamp": 1.42}, {"machine_id": 2, "process_id": 0, "activity_type": "start", "timestamp": 4.1}, {"machine_id": 2, "process_id": 0, "activity_type": "end", "timestamp": 4.512}, {"machine_id": 2, "process_id": 1, "activity_type": "start", "timestamp": 2.5}, {"machine_id": 2, "process_id": 1, "activity_type": "end", "timestamp": 5.0}])', [[0, 0.894], [1, 0.995], [2, 1.456]])]))
    results.append(check("1280. Students and Examinations", [('students_and_examinations([{"student_id": 1, "student_name": "Alice"}, {"student_id": 2, "student_name": "Bob"}], [{"subject_name": "Math"}, {"subject_name": "Physics"}], [{"student_id": 1, "subject_name": "Math"}, {"student_id": 1, "subject_name": "Math"}, {"student_id": 2, "subject_name": "Physics"}])', [[1, 'Alice', 'Math', 2], [1, 'Alice', 'Physics', 0], [2, 'Bob', 'Math', 0], [2, 'Bob', 'Physics', 1]])]))
    results.append(check("1251. Average Selling Price", [('average_selling_price([{"product_id": 1, "start_date": "2019-02-17", "end_date": "2019-02-28", "price": 5}, {"product_id": 1, "start_date": "2019-03-01", "end_date": "2019-03-22", "price": 20}, {"product_id": 2, "start_date": "2019-02-01", "end_date": "2019-02-20", "price": 15}, {"product_id": 2, "start_date": "2019-02-21", "end_date": "2019-03-31", "price": 30}, {"product_id": 3, "start_date": "2019-01-01", "end_date": "2019-01-31", "price": 9}], [{"product_id": 1, "purchase_date": "2019-02-25", "units": 100}, {"product_id": 1, "purchase_date": "2019-03-01", "units": 15}, {"product_id": 2, "purchase_date": "2019-02-10", "units": 200}, {"product_id": 2, "purchase_date": "2019-03-22", "units": 30}])', [[1, 6.96], [2, 16.96], [3, 0]])]))
    results.append(check("1211. Queries Quality and Percentage", [('queries_stats([{"query_name": "Dog", "result": "Golden Retriever", "position": 1, "rating": 5}, {"query_name": "Dog", "result": "German Shepherd", "position": 2, "rating": 5}, {"query_name": "Dog", "result": "Mule", "position": 200, "rating": 1}, {"query_name": "Cat", "result": "Shirazi", "position": 5, "rating": 2}, {"query_name": "Cat", "result": "Siamese", "position": 3, "rating": 3}, {"query_name": "Cat", "result": "Sphynx", "position": 7, "rating": 4}])', [['Cat', 0.66, 33.33], ['Dog', 2.5, 33.33]])]))
    results.append(check("607. Sales Person", [('sales_person([{"sales_id": 1, "name": "John"}, {"sales_id": 2, "name": "Amy"}, {"sales_id": 3, "name": "Mark"}, {"sales_id": 4, "name": "Pam"}, {"sales_id": 5, "name": "Alex"}], [{"com_id": 1, "name": "RED"}, {"com_id": 2, "name": "ORANGE"}, {"com_id": 3, "name": "YELLOW"}, {"com_id": 4, "name": "GREEN"}], [{"order_id": 1, "com_id": 3, "sales_id": 4}, {"order_id": 2, "com_id": 4, "sales_id": 5}, {"order_id": 3, "com_id": 1, "sales_id": 1}, {"order_id": 4, "com_id": 1, "sales_id": 4}])', ['Alex', 'Amy', 'Mark'])]))
    results.append(check("1193. Monthly Transactions I", [('monthly_transactions([{"id": 121, "country": "US", "state": "approved", "amount": 1000, "trans_date": "2018-12-18"}, {"id": 122, "country": "US", "state": "declined", "amount": 2000, "trans_date": "2018-12-19"}, {"id": 123, "country": "US", "state": "approved", "amount": 2000, "trans_date": "2019-01-01"}, {"id": 124, "country": "DE", "state": "approved", "amount": 2000, "trans_date": "2019-01-07"}])', [['2018-12', 'US', 2, 1, 3000, 1000], ['2019-01', 'DE', 1, 1, 2000, 2000], ['2019-01', 'US', 1, 1, 2000, 2000]])]))
    results.append(check("1174. Immediate Food Delivery II", [('immediate_percentage([{"delivery_id": 1, "customer_id": 1, "order_date": "2019-08-01", "customer_pref_delivery_date": "2019-08-02"}, {"delivery_id": 2, "customer_id": 2, "order_date": "2019-08-02", "customer_pref_delivery_date": "2019-08-02"}, {"delivery_id": 3, "customer_id": 1, "order_date": "2019-08-11", "customer_pref_delivery_date": "2019-08-12"}, {"delivery_id": 4, "customer_id": 3, "order_date": "2019-08-24", "customer_pref_delivery_date": "2019-08-24"}, {"delivery_id": 5, "customer_id": 3, "order_date": "2019-08-21", "customer_pref_delivery_date": "2019-08-22"}, {"delivery_id": 6, "customer_id": 2, "order_date": "2019-08-11", "customer_pref_delivery_date": "2019-08-13"}, {"delivery_id": 7, "customer_id": 4, "order_date": "2019-08-09", "customer_pref_delivery_date": "2019-08-09"}])', 50.0)]))
    if all(results):
        print("Every solution passes its tests.")
