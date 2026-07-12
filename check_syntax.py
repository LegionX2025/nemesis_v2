import bs4
import subprocess
import os

for html_file in ['nemesis_id.html', 'tracer.html']:
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')
        
    for i, script in enumerate(soup.find_all('script')):
        if not script.get('src') and script.string:
            temp_name = f'temp_{html_file}_script_{i}.js'
            with open(temp_name, 'w', encoding='utf-8') as f_temp:
                f_temp.write(script.string)
            
            result = subprocess.run(['node', '-c', temp_name], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Syntax error in {html_file} script block {i}:")
                print(result.stderr)
            os.remove(temp_name)
