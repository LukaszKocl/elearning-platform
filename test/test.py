from elearning.models import Category, Course
import pytest


@pytest.mark.django_db
def test_category1(category):
    assert Category.objects.get(name="Kategoira testowa2") == category

@pytest.mark.django_db
def test_add_category_view(client, category):
    response = client.post('/kategoria/dodawanie/', {"name":"Kategoira testowa2", "slug":"kategoria-testowa"})
    assert response.status_code == 302

@pytest.mark.django_db
def test_edit_category_view(client, category_edit):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kategoria/modyfikacja/1/')
    assert response_get.status_code == 200 #zweryfikować

@pytest.mark.django_db
def test_delete_category_view(client, category):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kategoria/usuniecie/1/')
    assert response_get.status_code == 302

@pytest.mark.django_db
def test_add_course_view(client, course):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kurs/dodawanie/')
    assert response_get.status_code == 200

@pytest.mark.django_db
def test_edit_course_view(client, course_edit, user):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kurs/modyfikacja/1/')
    assert response_get.status_code == 200


@pytest.mark.django_db
def test_delete_course_view(client, course):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kurs/usuniecie/1/')

    assert response_get.status_code == 200

@pytest.mark.django_db
def test_list_course_view(client):
    response_get = client.get('/kursy/szczegoly/1/')

    assert response_get.status_code == 200

@pytest.mark.django_db
def test_course_detail_view(client):
    response_get = client.get('/kurs/moduly/1/')

    assert response_get.status_code == 200


@pytest.mark.django_db
def test_course_video_view(client, course):
    client.login(username="karol", password="haslo")
    response_get = client.get('/kurs/moduly/video/1/1')

    assert response_get.status_code == 200

"""
@pytest.mark.django_db
def test_orders(client):
    response = client.get('/zamowienia/lista/')

    assert response.status_code == 200
    assert len(response.context["orders"]) == 0
"""
@pytest.mark.django_db
def test_category2(client, category):
    response = client.get('/')
    assert response.status_code == 200
    assert len(response.context["categories"]) == 2

