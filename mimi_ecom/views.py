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