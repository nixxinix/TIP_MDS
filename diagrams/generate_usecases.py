#!/usr/bin/env python
"""
Django Use Case Diagram Generator
Converts urls_dump.json into a clean Mermaid use case diagram
"""
import json
import re
from collections import defaultdict

# Actor assignment rules
ACTOR_RULES = {
    'admin': 'Admin',
    'doctor': 'Doctor',
    'student': 'Student',
    'notification': 'User',
    'account': 'User',
    'login': 'Guest',
    'register': 'Guest',
    'signup': 'Guest',
    'api': 'API Client'
}

def clean_path(path):
    """Remove URL parameters and clean path"""
    # Remove regex patterns and parameters
    path = re.sub(r'\^', '', path)
    path = re.sub(r'\$', '', path)
    path = re.sub(r'<[^>]+>', '{id}', path)
    path = re.sub(r'\([^)]+\)', '', path)
    path = re.sub(r'\?P<[^>]+>', '', path)
    return path.strip('/')

def generate_usecase_name(url_data):
    """Generate human-readable use case name"""
    path = clean_path(url_data['path'])
    name = url_data['name']
    view = url_data['view']
    app = url_data['app']
    
    # Skip utility URLs
    if any(x in path for x in ['static', 'media', 'jsi18n', 'autocomplete']):
        return None
    
    # Use view name if meaningful
    if name and name != 'unnamed':
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        if words:
            return ' '.join(word.capitalize() for word in words)
    
    # Parse from path
    parts = [p for p in path.split('/') if p and p != '{id}']
    
    if not parts:
        if app == 'django':
            return None
        return f"View {app.capitalize()} Home"
    
    # Handle specific patterns
    last_part = parts[-1]
    
    # CRUD operations
    crud_map = {
        'create': 'Create',
        'add': 'Create',
        'new': 'Create',
        'edit': 'Edit',
        'update': 'Update',
        'delete': 'Delete',
        'remove': 'Delete',
        'list': 'View',
        'detail': 'View Details',
        'view': 'View',
        'read': 'Mark as Read',
        'mark-all-read': 'Mark All as Read',
        'preferences': 'Manage Preferences',
        'count': 'Get Count'
    }
    
    action = crud_map.get(last_part, None)
    
    if action:
        # Get the entity (second to last part)
        if len(parts) > 1:
            entity = parts[-2].replace('-', ' ').replace('_', ' ').title()
        else:
            entity = app.capitalize()
        return f"{action} {entity}"
    
    # Default: capitalize the last meaningful part
    usecase = last_part.replace('-', ' ').replace('_', ' ').title()
    
    # Add context from app if generic
    if usecase.lower() in ['index', 'home', 'main', 'dashboard']:
        return f"View {app.capitalize()} {usecase}"
    
    return usecase

def assign_actor(url_data, usecase_name):
    """Assign appropriate actor based on URL characteristics"""
    path = url_data['path'].lower()
    app = url_data['app'].lower()
    
    # Admin URLs
    if url_data['is_admin'] or 'admin' in path:
        return 'Admin'
    
    # API endpoints
    if url_data['is_api'] or '/api/' in path:
        return 'API Client'
    
    # Authentication URLs
    if any(x in path for x in ['login', 'logout', 'register', 'signup', 'password_reset']):
        return 'Guest'
    
    # App-specific actors
    if 'doctor' in app or 'doctor' in path:
        return 'Doctor'
    
    if 'student' in app or 'student' in path:
        return 'Student'
    
    # Check use case name for clues
    if usecase_name:
        name_lower = usecase_name.lower()
        if 'doctor' in name_lower:
            return 'Doctor'
        if 'student' in name_lower:
            return 'Student'
        if 'notification' in name_lower or 'alert' in name_lower:
            return 'User'
    
    # Default: authenticated user
    return 'User'

def generate_mermaid_diagram(urls_data):
    """Generate Mermaid use case diagram"""
    
    # Filter and process URLs
    usecases_by_app = defaultdict(list)
    
    for url in urls_data:
        usecase_name = generate_usecase_name(url)
        
        if not usecase_name:
            continue
        
        actor = assign_actor(url, usecase_name)
        app = url['app']
        
        # Skip duplicate use cases in same app
        existing = [u['name'] for u in usecases_by_app[app]]
        if usecase_name in existing:
            continue
        
        usecases_by_app[app].append({
            'name': usecase_name,
            'actor': actor,
            'path': clean_path(url['path']),
            'methods': url['methods']
        })
    
    # Generate Mermaid code
    mermaid = ['graph LR']
    mermaid.append('    %% Actors')
    
    # Collect all unique actors
    all_actors = set()
    for app_usecases in usecases_by_app.values():
        for uc in app_usecases:
            all_actors.add(uc['actor'])
    
    # Define actors with icons
    actor_icons = {
        'Guest': '👤',
        'User': '👥',
        'Admin': '⚙️',
        'Doctor': '👨‍⚕️',
        'Student': '👨‍🎓',
        'API Client': '🔌'
    }
    
    for actor in sorted(all_actors):
        icon = actor_icons.get(actor, '👤')
        actor_id = actor.replace(' ', '_')
        mermaid.append(f'    {actor_id}["{icon} {actor}"]')
    
    mermaid.append('')
    
    # Skip admin app (too many URLs)
    apps_to_show = [app for app in usecases_by_app.keys() 
                    if app not in ['admin', 'django']]
    
    # Generate use cases by app
    for app in sorted(apps_to_show):
        usecases = usecases_by_app[app]
        
        if not usecases:
            continue
        
        mermaid.append(f'    %% {app.upper()} App')
        mermaid.append(f'    subgraph {app.upper()}')
        
        for i, uc in enumerate(usecases[:15]):  # Limit to 15 per app for clarity
            uc_id = f"{app}_{i}"
            uc_name = uc['name']
            methods = ','.join(uc['methods'][:2])  # Show max 2 methods
            
            # Add method indicator
            method_icon = ''
            if 'POST' in uc['methods']:
                method_icon = '➕'
            elif 'PUT' in uc['methods'] or 'PATCH' in uc['methods']:
                method_icon = '✏️'
            elif 'DELETE' in uc['methods']:
                method_icon = '🗑️'
            else:
                method_icon = '👁️'
            
            mermaid.append(f'        {uc_id}("{method_icon} {uc_name}")')
        
        mermaid.append('    end')
        mermaid.append('')
        
        # Add actor connections
        for i, uc in enumerate(usecases[:15]):
            uc_id = f"{app}_{i}"
            actor_id = uc['actor'].replace(' ', '_')
            mermaid.append(f'    {actor_id} --> {uc_id}')
        
        mermaid.append('')
    
    # Add admin summary (collapsed)
    if 'admin' in usecases_by_app:
        admin_count = len(usecases_by_app['admin'])
        mermaid.append('    %% Admin Panel')
        mermaid.append('    subgraph ADMIN')
        mermaid.append(f'        admin_panel("⚙️ Django Admin Panel<br/>({admin_count} admin URLs)")')
        mermaid.append('    end')
        mermaid.append('    Admin --> admin_panel')
        mermaid.append('')
    
    # Styling
    mermaid.append('    %% Styling')
    mermaid.append('    classDef actorStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px')
    mermaid.append('    classDef usecaseStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px')
    
    for actor in all_actors:
        actor_id = actor.replace(' ', '_')
        mermaid.append(f'    class {actor_id} actorStyle')
    
    return '\n'.join(mermaid)

def main():
    print("🎨 Generating Use Case Diagram...\n")
    
    # Load URLs
    try:
        with open('urls_dump.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
        print(f"✅ Loaded {len(urls)} URLs from urls_dump.json")
    except FileNotFoundError:
        print("❌ Error: urls_dump.json not found. Run extract_urls.py first.")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return
    
    # Generate diagram
    mermaid_code = generate_mermaid_diagram(urls)
    
    # Save to file
    output_file = 'usecases.mmd'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_code)
    
    print(f"✅ Saved Mermaid diagram to: {output_file}")
    print(f"\n📊 Diagram Statistics:")
    
    # Count use cases by app
    lines = mermaid_code.split('\n')
    apps = [line.split('subgraph ')[1] for line in lines if 'subgraph' in line]
    print(f"  • Apps included: {', '.join(apps)}")
    
    actors = [line.split('[')[1].split(']')[0] for line in lines if '[' in line and ']' in line and any(x in line for x in ['👤', '👥', '⚙️', '👨‍⚕️', '👨‍🎓', '🔌'])]
    print(f"  • Actors: {len(set(actors))}")
    
    usecases = len([line for line in lines if '("' in line and 'subgraph' not in line])
    print(f"  • Use cases: {usecases}")
    
    print(f"\n🎯 Next steps:")
    print(f"  1. Preview online: https://mermaid.live/")
    print(f"  2. Or render locally: bash render_mermaid.sh")

if __name__ == '__main__':
    main()
    