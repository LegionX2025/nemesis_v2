import os

filepath = '.env'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('DATABASE_MONGO_URL='):
        new_lines.append('DATABASE_MONGO_URL=mongodb+srv://nemesis:nemesis2026@nemesisdb.vir5vg2.mongodb.net/?appName=nemesisdb\n')
    elif line.startswith('VITE_DATABASE_MONGO_URL='):
        new_lines.append('VITE_DATABASE_MONGO_URL=mongodb+srv://nemesis:nemesis2026@nemesisdb.vir5vg2.mongodb.net/?appName=nemesisdb\n')
    else:
        new_lines.append(line)

new_lines.append('\n# NEO4J\n')
new_lines.append('NEO4J_URI=neo4j+s://89ea7d8f.databases.neo4j.io\n')
new_lines.append('NEO4J_USERNAME=89ea7d8f\n')
new_lines.append('NEO4J_PASSWORD=pMyRVGUtCLJCHBph0vR3FBVk5Ct1jkrThq-ApD2cJAA\n')
new_lines.append('NEO4J_DATABASE=89ea7d8f\n')

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Updated .env successfully')
