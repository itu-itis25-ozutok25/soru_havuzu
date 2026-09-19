from django.test import SimpleTestCase
from django.urls import reverse


class FoundationEndpointTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "soru-havuzu",
            },
        )

    def test_api_v1_root(self):
        response = self.client.get(reverse("api-v1-root"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "v1")

