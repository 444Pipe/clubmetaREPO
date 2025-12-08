from django.http import HttpResponse
from django.conf import settings
import importlib

def diag_view(request):
    out = []
    out.append(f'ROOT_URLCONF = {settings.ROOT_URLCONF}')
    out.append(f'DEBUG = {settings.DEBUG}')
    out.append(f'STATIC_URL = {settings.STATIC_URL}')
    out.append(f'MEDIA_URL = {settings.MEDIA_URL}')
    out.append(f"TEMPLATES DIRS = {getattr(settings, 'TEMPLATES', []) and settings.TEMPLATES[0].get('DIRS')}")

    # Try to import urlpatterns from ROOT_URLCONF
    try:
        mod = importlib.import_module(settings.ROOT_URLCONF)
        urlpatterns = getattr(mod, 'urlpatterns', None)
    except Exception as e:
        out.append('Error importing ROOT_URLCONF: ' + str(e))
        return HttpResponse('\n'.join(out), content_type='text/plain')

    out.append('\nFirst 60 URL patterns (pattern -> name or include):')
    if not urlpatterns:
        out.append(' (no urlpatterns found)')
    else:
        i = 0
        for p in urlpatterns:
            if i >= 60:
                break
            try:
                pat = getattr(p, 'pattern', p)
                name = getattr(p, 'name', None)
                # For URLResolver (include), show its regex/pattern repr
                out.append(f'{i+1}. {pat} -> name={name} type={type(p).__name__}')
            except Exception as e:
                out.append(f'{i+1}. <error inspecting pattern>: {e}')
            i += 1

    return HttpResponse('\n'.join(out), content_type='text/plain')
