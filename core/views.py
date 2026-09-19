from django.http import JsonResponse


def health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "soru-havuzu",
        }
    )


def api_root(request):
    return JsonResponse(
        {
            "name": "Soru Havuzu API",
            "version": "v1",
            "status": "foundation-ready",
        }
    )

