from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def tag_url(tag_id):
    """Create and return a recipe a detail url."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(**params):
    """Create and return a new user."""
    default = {
        "email": "email@email.com",
        "password": "password",
    }

    default.update(params)

    return get_user_model().objects.create_user(default["email"], default["password"])


class PublicTagsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by(("-name"))
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email="other@email.com")
        Tag.objects.create(user=user2, name="Other_tag")
        tag = Tag.objects.create(user=self.user, name="User_tag")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test full update of recipe"""
        tag = Tag.objects.create(user=self.user, name="After Dinner")
        payload = {
            "name": "Before Dinner",
        }

        url = tag_url(tag.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        url = tag_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
