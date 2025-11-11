#!/usr/bin/env python
"""
Django URL Extractor
Extracts all URL patterns, views, and metadata from Django project
"""
import os
import sys
import django
import json
from django.urls import get_resolver
from django.conf import settings

def setup_django():
    """Initialize Django settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # Try common settings module names
    for module in ['config.settings', 'settings', f'{os.path.basename(os.getcwd())}.settings']:
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = module
            django.setup()
            print(f"✅ Django initialized with: {module}")
            return True
        except:
            continue
    return False

def get_view_name(view_func):
    """Extract clean view name from view function"""
    if hasattr(view_func, '__name__'):
        return view_func.__name__
    elif hasattr(view_func, '__class__'):
        return view_func.__class__.__name__
    return str(view_func)

def extract_urls(urlpatterns=None, prefix='', namespace='', app_name=''):
    """Recursively extract all URL patterns"""
    if urlpatterns is None:
        urlpatterns = get_resolver().url_patterns
    
    urls_data = []
    
    for pattern in urlpatterns:
        # Get the pattern string
        pattern_str = str(pattern.pattern)
        full_path = prefix + pattern_str
        
        # Handle included URLconfs
        if hasattr(pattern, 'url_patterns'):
            # It's an include()
            new_namespace = f"{namespace}:{pattern.namespace}" if pattern.namespace else namespace
            new_app_name = pattern.app_name or app_name
            urls_data.extend(
                extract_urls(
                    pattern.url_patterns,
                    prefix=full_path,
                    namespace=new_namespace,
                    app_name=new_app_name
                )
            )
        else:
            # It's a regular URL pattern
            view_name = pattern.name or 'unnamed'
            
            # Get view info
            callback = pattern.callback
            view_class = get_view_name(callback)
            view_module = callback.__module__ if hasattr(callback, '__module__') else 'unknown'
            
            # Detect app name from module path
            detected_app = 'core'
            if '.' in view_module:
                parts = view_module.split('.')
                if 'views' in parts:
                    idx = parts.index('views')
                    if idx > 0:
                        detected_app = parts[idx - 1]
                elif len(parts) > 0:
                    detected_app = parts[0]
            
            # Detect HTTP methods (for viewsets/APIView)
            methods = ['GET']  # Default
            if hasattr(callback, 'cls'):
                # DRF ViewSet or APIView
                cls = callback.cls
                if hasattr(cls, 'http_method_names'):
                    methods = [m.upper() for m in cls.http_method_names if m != 'options']
                elif hasattr(cls, 'queryset'):
                    # It's likely a ViewSet
                    methods = ['GET', 'POST', 'PUT', 'DELETE']
            
            # Detect authentication requirement
            requires_auth = 'login' in view_module.lower() or 'auth' in view_module.lower()
            is_admin = 'admin' in full_path or 'admin' in view_module
            is_api = 'api' in full_path or 'rest_framework' in view_module
            
            urls_data.append({
                'path': full_path,
                'name': view_name,
                'view': view_class,
                'module': view_module,
                'app': app_name or detected_app,
                'namespace': namespace,
                'methods': methods,
                'requires_auth': requires_auth,
                'is_admin': is_admin,
                'is_api': is_api
            })
    
    return urls_data

def main():
    print("🔍 Extracting URLs from Django project...\n")
    
    # Setup Django
    if not setup_django():
        print("❌ Could not initialize Django. Check your settings module.")
        sys.exit(1)
    
    # Extract URLs
    try:
        urls = extract_urls()
        print(f"✅ Found {len(urls)} URL patterns\n")
        
        # Group by app for preview
        apps = {}
        for url in urls:
            app = url['app']
            if app not in apps:
                apps[app] = []
            apps[app].append(url)
        
        print("📊 URLs by App:")
        for app, app_urls in sorted(apps.items()):
            print(f"  • {app}: {len(app_urls)} URLs")
        
        # Save to JSON
        output_file = 'urls_dump.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to: {output_file}")
        print(f"📦 Total URLs extracted: {len(urls)}")
        
    except Exception as e:
        print(f"❌ Error extracting URLs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()