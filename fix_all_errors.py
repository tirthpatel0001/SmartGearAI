#!/usr/bin/env python3

# Fix maintenance_dashboard.py
with open('app/maintenance_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the problematic function (around line 10-17)
new_lines = []
i = 0
while i < len(lines):
    if 'def display_gearbox_diagnosis' in lines[i]:
        # Add the function definition
        new_lines.append(lines[i])
        i += 1
        
        # Skip the problematic st.markdown section
        while i < len(lines) and 'uploaded_file = st.file_uploader' not in lines[i]:
            i += 1
        
        # Add the header and text
        new_lines.append('    st.header("⚙️ Predictive Maintenance & Diagnosis")\n')
        new_lines.append('    st.write("AI-powered gearbox signal analysis with cost insights and maintenance recommendations")\n')
        new_lines.append('\n')
        # Continue with file_uploader
        continue
    
    new_lines.append(lines[i])
    i += 1

with open('app/maintenance_dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Fixed maintenance_dashboard.py")

# Fix scm_chain.py
with open('app/scm_chain.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    if 'def display_inventory_management' in lines[i]:
        # Add the function definition
        new_lines.append(lines[i])
        i += 1
        
        # Skip the problematic st.markdown section
        while i < len(lines) and 'role = st.session_state.get' not in lines[i]:
            i += 1
        
        # Add the header
        new_lines.append('    st.header("📦 Inventory Management System")\n')
        # Continue with role line
        continue
    
    new_lines.append(lines[i])
    i += 1

with open('app/scm_chain.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Fixed scm_chain.py")
print("\n✅ All errors cleared!")
