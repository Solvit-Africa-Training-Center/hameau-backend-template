import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from programs.models import ChildCaretakerAssignment, House, Caretaker, Child
from accounts.models import User
from uuid import uuid4


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def residential_manager(db):
    return User.objects.create_user(
        email="manager@test.com",
        password="testpass123",
        role="RESIDENTIAL_MANAGER",
    )


@pytest.fixture
def caretaker(db):
    return Caretaker.objects.create(
        first_name="Test",
        last_name="Caretaker",
        phone="0780000000",
        hire_date=timezone.now().date(),
        is_active=True,
    )


@pytest.fixture
def house(db, caretaker):
    return House.objects.create(
        caretaker=caretaker,
    )


@pytest.fixture
def child(db):
    return Child.objects.create(
        first_name="John",
        last_name="Doe",
        date_of_birth="2015-01-01",
        gender="MALE",
        start_date="2023-01-01",
    )


@pytest.mark.django_db
def test_list_assignments(api_client, residential_manager, house, child):
    api_client.force_authenticate(user=residential_manager)

    ChildCaretakerAssignment.objects.create(
        child=child,
        house=house,
        assigned_date=timezone.now().date(),
        is_active=True,
    )

    url = reverse("children_caretaker-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_create_assignment(api_client, residential_manager, house, child):
    api_client.force_authenticate(user=residential_manager)

    url = reverse("children_caretaker-list")

    data = {
        "child": str(child.id),
        "caretaker_id": str(house.caretaker.id),
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == 201
    assert ChildCaretakerAssignment.objects.count() == 1


@pytest.mark.django_db
def test_bulk_assign(api_client, residential_manager, house):
    api_client.force_authenticate(user=residential_manager)

    child1 = Child.objects.create(
        first_name="Child1",
        last_name="Test",
        date_of_birth="2016-01-01",
        gender="MALE",
        start_date="2023-01-01",
    )
    child2 = Child.objects.create(
        first_name="Child2",
        last_name="Test",
        date_of_birth="2017-01-01",
        gender="FEMALE",
        start_date="2023-01-01",
    )

    url = reverse("children_caretaker-bulk-assign")

    data = {
        "caretaker_id": str(house.caretaker.id),
        "children_ids": [str(child1.id), str(child2.id)],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 201
    assert ChildCaretakerAssignment.objects.count() == 2

@pytest.mark.django_db
def test_bulk_assign_ignore_duplicates(api_client, residential_manager, house, child):
    api_client.force_authenticate(user=residential_manager)

    ChildCaretakerAssignment.objects.create(
        child=child,
        house=house,
        assigned_date=timezone.now().date(),
        is_active=True,
    )

    url = reverse("children_caretaker-bulk-assign")

    data = {
        "caretaker_id": str(house.caretaker.id),
        "children_ids": [str(child.id)],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 201
    assert ChildCaretakerAssignment.objects.count() == 1


@pytest.mark.django_db
def test_destroy_assignment(api_client, residential_manager, house, child):
    api_client.force_authenticate(user=residential_manager)

    assignment = ChildCaretakerAssignment.objects.create(
        child=child,
        house=house,
        assigned_date=timezone.now().date(),
        is_active=True,
    )

    url = reverse("children_caretaker-detail", args=[assignment.id])
    response = api_client.delete(url)

    assert response.status_code == 204
    assert ChildCaretakerAssignment.objects.count() == 0


@pytest.mark.django_db
def test_bulk_remove(api_client, residential_manager, house):
    api_client.force_authenticate(user=residential_manager)

    child1 = Child.objects.create(
        first_name="A",
        last_name="B",
        date_of_birth="2016-01-01",
        gender="MALE",
        start_date="2023-01-01",
    )
    child2 = Child.objects.create(
        first_name="C",
        last_name="D",
        date_of_birth="2017-01-01",
        gender="FEMALE",
        start_date="2023-01-01",
    )

    assignment1 = ChildCaretakerAssignment.objects.create(
        child=child1,
        house=house,
        assigned_date=timezone.now().date(),
        is_active=True,
    )

    assignment2 = ChildCaretakerAssignment.objects.create(
        child=child2,
        house=house,
        assigned_date=timezone.now().date(),
        is_active=True,
    )

    url = reverse("children_caretaker-bulk-remove")

    data = {
        "caretaker_id": str(house.caretaker.id),
        "assignment_ids": [str(assignment1.id), str(assignment2.id)],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 200
    assert response.data["deleted"] == 2
    assert ChildCaretakerAssignment.objects.count() == 0


@pytest.mark.django_db
def test_permission_denied(api_client, house, child):
    user = User.objects.create_user(
        email="normal@test.com",
        password="testpass123",
        role="USER",
    )

    api_client.force_authenticate(user=user)

    url = reverse("children_caretaker-list")
    response = api_client.get(url)

    assert response.status_code == 403
