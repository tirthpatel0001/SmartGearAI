import pathlib
path = pathlib.Path(r"c:\Projects\SGMAS\app\main.py")
lines = path.read_text(encoding='utf-8').splitlines()
out=[]
skip=False
for line in lines:
    if line.strip().startswith('from app.maintenance_dashboard import display_gearbox_diagnosis'):
        out.append(line)
        skip=True
        continue
    if skip and line.strip().startswith('def display_admin_login'):
        out.append(line)
        skip=False
        continue
    if skip:
        continue
    out.append(line)
path.write_text("\n".join(out),encoding='utf-8')
print('cleaned {} lines'.format(len(out)))
