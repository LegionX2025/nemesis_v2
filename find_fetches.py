import os
files = [f for f in os.listdir('.') if f.endswith('.js') or f.endswith('.html')]
for f in files:
    try:
        content = open(f, encoding='utf-8').read()
        if 'fetch(' in content or 'BACKEND_URL' in content or 'onrender.com' in content:
            print(f'Found fetch/backend references in {f}')
    except Exception as e:
        print(e)
