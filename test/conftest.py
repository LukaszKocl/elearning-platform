from elearning.models import Category, User, Permission, Course
from django.test import Client
import pytest

@pytest.fixture
def category():
    cat = Category.objects.create(name="Kategoira testowa", slug="kategoria-testowa")
    cat = Category.objects.create(name="Kategoira testowa2", slug="kategoria-testowa")
    return cat

@pytest.fixture
def category_edit():
    Category.objects.create(name="Kategoira testowa2", slug="kategoria-testowa")
    return Category.objects.get(pk=1)

@pytest.fixture
def user():
    user = User.objects.create(username='pawel', email='pawel@pawel.pl')
    user.set_password("pawel")
    user.save()
    user = User.objects.create(username='karol', email='karol@karol.pl')
    user.set_password("haslo")
    user.save()
    p = Permission.objects.get(codename="change_course")
    user.user_permissions.add(p)
    p = Permission.objects.get(codename="change_category")
    user.user_permissions.add(p)
    p = Permission.objects.get(codename="delete_category")
    user.user_permissions.add(p)
    p = Permission.objects.get(codename="add_course")
    user.user_permissions.add(p)
    p = Permission.objects.get(codename="change_course")
    user.user_permissions.add(p)
    return user


@pytest.fixture
def course(category, user):
    course = Course.objects.create(name="Kurs 1",
                                   description="Opis 1",
                                   tutor=user,
                                    price=100,
                                    is_active=True,
                                    category=category)
    return course

@pytest.fixture
def course_edit(category, user):
    Course.objects.create(name="Kurs 1",
                                   description="Opis 1",
                                   tutor=user,
                                    price=100,
                                    is_active=True,
                                    category=category)
    return Course.objects.get(pk=1)

@pytest.fixture
def client():
    client = Client()
    return client
