import os

file_path = "nemesis_id.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

start = content.find('<main')
end = content.find('</main>')
if start != -1 and end != -1:
    print('Main block length:', end - start)
else:
    print('Could not find <main> or </main>')
