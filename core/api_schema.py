OPENAPI_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "Soru Havuzu API",
        "version": "1.0.0",
        "description": (
            "8. sınıf matematik soru havuzu için sürümlendirilmiş salt-okunur API. "
            "Soru uçları token gerektirir. Öğrenci/istemci rolünde doğru cevap ve "
            "çözüm gizlenir; güvenilir sunucu rolü tam yanıta erişebilir."
        ),
    },
    "servers": [{"url": "/api/v1"}],
    "components": {
        "securitySchemes": {
            "tokenAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Token <anahtar>",
            }
        }
    },
    "paths": {
        "/questions/": {
            "get": {
                "summary": "Filtrelenmiş soru listesi",
                "security": [{"tokenAuth": []}],
                "parameters": [
                    {"name": "q", "in": "query", "schema": {"type": "string"}},
                    {"name": "topics", "in": "query", "schema": {"type": "string"}},
                    {"name": "outcomes", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "outcome_match",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["any", "all"]},
                    },
                    {"name": "question_type", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "difficulty",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    {"name": "exclude", "in": "query", "schema": {"type": "string"}},
                    {"name": "page", "in": "query", "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {"description": "Sayfalanmış soru listesi"},
                    "401": {"description": "Token eksik veya geçersiz"},
                    "403": {"description": "API rolü yok"},
                },
            }
        },
        "/questions/{code}/": {
            "get": {
                "summary": "Tek soru",
                "security": [{"tokenAuth": []}],
                "parameters": [
                    {
                        "name": "code",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "pattern": "^Q[0-9]{6}$"},
                    }
                ],
                "responses": {
                    "200": {"description": "Soru"},
                    "401": {"description": "Token eksik veya geçersiz"},
                    "403": {"description": "API rolü yok"},
                    "404": {"description": "Bulunamadı"},
                },
            }
        },
        "/questions/random/": {
            "get": {
                "summary": "Filtrelenmiş rastgele sorular",
                "security": [{"tokenAuth": []}],
                "parameters": [
                    {
                        "name": "count",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    {"name": "q", "in": "query", "schema": {"type": "string"}},
                    {"name": "topics", "in": "query", "schema": {"type": "string"}},
                    {"name": "outcomes", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "outcome_match",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["any", "all"]},
                    },
                    {"name": "question_type", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "difficulty",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    {"name": "exclude", "in": "query", "schema": {"type": "string"}},
                ],
                "responses": {
                    "200": {"description": "Rastgele soru listesi"},
                    "401": {"description": "Token eksik veya geçersiz"},
                    "403": {"description": "API rolü yok"},
                },
            }
        },
    },
}
