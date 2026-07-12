import re

with open('tracer.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the start of the landing page
start_idx = html.find('<div id="landing-page"')
end_idx = html.find('<div id="main-ui"')

if start_idx != -1 and end_idx != -1:
    # Cut out the landing page
    html = html[:start_idx] + html[end_idx:]
    
    # Remove the 'hidden' class from main-ui so it shows immediately
    html = html.replace('<div id="main-ui" class="hidden flex-col h-screen w-full">', 
                        '<div id="main-ui" class="flex flex-col h-screen w-full">')
    
    with open('tracer.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully removed landing page from tracer.html and unhid main-ui")
else:
    print("Could not find start or end bounds.")
