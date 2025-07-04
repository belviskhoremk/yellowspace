from django.shortcuts import render
# Create your views here.

def index(request):
    return render(request, 'index.html')


# views.py
from django.http import JsonResponse
from googletrans import Translator, LANGUAGES


def translate_text(request):
    text = request.GET.get('text', '')
    dest_lang = request.GET.get('lang', 'en')

    if not text:
        return JsonResponse({'error': 'No text provided'}, status=400)

    try:
        translator = Translator()
        translation = translator.translate(text, dest=dest_lang)
        return JsonResponse({
            'translation': translation.text,
            'src_lang': translation.src,
            'dest_lang': dest_lang
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# views.py
import os
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

User = get_user_model()


@csrf_exempt
@require_http_methods(["POST"])
def setup_admin(request):
    # Check if this is production and setup is allowed
    if not os.environ.get('ALLOW_ADMIN_SETUP'):
        return JsonResponse({'error': 'Admin setup not allowed'}, status=403)

    # Check if admin already exists
    if User.objects.filter(is_superuser=True).exists():
        return JsonResponse({'error': 'Admin user already exists'}, status=400)

    # Get credentials from environment or request
    username = os.environ.get('ADMIN_USERNAME', 'admin_mimi')
    email = os.environ.get('ADMIN_EMAIL', 'emelinezankli@gmail.com')
    password = os.environ.get('ADMIN_PASSWORD', '1amTh3Adm1n0fTh15App2025!?')

    if not password:
        return JsonResponse({'error': 'Admin password not configured'}, status=400)

    try:
        # Create the admin user
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Disable further admin creation by removing the env var
        # (You'll need to manually remove ALLOW_ADMIN_SETUP from Render after this)

        return JsonResponse({
            'success': True,
            'message': f'Admin user "{username}" created successfully'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

