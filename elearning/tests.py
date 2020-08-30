from django.test import TestCase, Client

# Create your test here.
import pytest


def add(a, b):
    return a + b

@pytest.mark.parametrize ("a, b, result",(
        (2,2,4),
        (2,3,6),
        (3,4,9),
        (4,4,8),
))
def test_add_1(a, b, result):
    assert add(a, b) == result

c = Client()
response = c.get('/zamowienia/lista/')
print(response.content_type)

