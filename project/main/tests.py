import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Course

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_course_list(api_client):
    Course.objects.create(title="Тест курс", description="Описание")
    url = reverse("course-list")  # Если используешь DRF роутер
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Тест курс"
