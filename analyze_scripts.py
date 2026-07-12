import os

scripts_dir = 'scripts'
if not os.path.exists(scripts_dir):
    print("No scripts dir")
    exit()

analysis = []
for f in os.listdir(scripts_dir):
    if f.endswith('.py'):
        filepath = os.path.join(scripts_dir, f)
        size = os.path.getsize(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                imports = [l.strip() for l in lines if l.startswith('import ') or l.startswith('from ')]
                classes = [l.strip() for l in lines if l.startswith('class ')]
                funcs = [l.strip() for l in lines if l.startswith('def ')]
                docstring = ""
                if lines and '"""' in lines[0]:
                    end = 1
                    while end < min(15, len(lines)) and '"""' not in lines[end]:
                        end += 1
                    docstring = "".join(lines[0:end+1]).strip()
                elif lines and lines[0].startswith('#'):
                    end = 0
                    while end < min(15, len(lines)) and lines[end].startswith('#'):
                        end += 1
                    docstring = "".join(lines[0:end]).strip()
                
                analysis.append(f"## {f} ({size} bytes)")
                if docstring:
                    analysis.append(f"**Docstring/Header:**\n```python\n{docstring}\n```")
                if classes:
                    analysis.append(f"**Classes:** {', '.join([c.split(' ')[1].split('(')[0].split(':')[0] for c in classes[:5]])}{'...' if len(classes)>5 else ''}")
                if funcs:
                    analysis.append(f"**Functions:** {', '.join([f.split(' ')[1].split('(')[0] for f in funcs[:5]])}{'...' if len(funcs)>5 else ''}")
                analysis.append("\n")
        except Exception as e:
            analysis.append(f"Error reading {f}: {e}")

with open('scripts_analysis_output.md', 'w', encoding='utf-8') as out:
    out.write('\n'.join(analysis))
print("Analysis complete")
