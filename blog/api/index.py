# api/index.py  — Django WSGI 엔트리
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = get_wsgi_application()  # <-- Vercel Python은 WSGI callable인 'app'를 찾습니다.