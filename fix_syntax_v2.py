#!/usr/bin/env python3
"""Fix syntax errors - read file bytes and reconstruct"""

import re

# Fix maintenance_dashboard.py
print("Processing maintenance_dashboard.py...")
with open('app/maintenance_dashboard.py', 'rb') as f:
    content_bytes = f.read()

content_str = content_bytes.decode('utf-8')

# Find and replace the problematic section
# Look for the function definition and the st.markdown call
lines = content_str.split('\n')
new_lines = []
i = 0
fixed = False

while i < len(lines):
    line = lines[i]
    
    # Check if this is the start of display_gearbox_diagnosis function
    if 'def display_gearbox_diagnosis' in line:
        new_lines.append(line)
        i += 1
        found_markdown = False
        markdown_lines = []
        
        # Collect the st.markdown call
        while i < len(lines):
            current_line = lines[i]
            markdown_lines.append(current_line)
            
            if 'st.markdown' in current_line:
                found_markdown = True
            
            if found_markdown and 'unsafe_allow_html=True' in current_line:
                # Found the end of st.markdown call, now replace all collected lines
                markdown_str = '\n'.join(markdown_lines)
                
                # Check if this is the problematic format
                if '"""' in markdown_str and 'Predictive Maintenance' in markdown_str:
                    # Replace with proper format
                    new_lines.append("    st.markdown('<div style=\"background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 32px; border-radius: 8px; margin-bottom: 24px; border-top: 4px solid #D97706;\"><h1 style=\"margin: 0; font-size: 2.2em; font-weight: 700;\">⚙️ Predictive Maintenance & Diagnosis</h1><p style=\"margin: 8px 0 0 0; opacity: 0.95;\">AI-powered gearbox signal analysis with cost insights and maintenance recommendations</p></div>', unsafe_allow_html=True)")
                    fixed = True
                else:
                    # Keep as is
                    for md_line in markdown_lines:
                        new_lines.append(md_line)
                
                i += 1
                break
            
            i += 1
    else:
        new_lines.append(line)
        i += 1

if fixed:
    with open('app/maintenance_dashboard.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("✓ Fixed maintenance_dashboard.py")
else:
    print("⚠ Could not find pattern in maintenance_dashboard.py")

# Fix scm_chain.py
print("Processing scm_chain.py...")
with open('app/scm_chain.py', 'rb') as f:
    content_bytes = f.read()

content_str = content_bytes.decode('utf-8')

lines = content_str.split('\n')
new_lines = []
i = 0
fixed_scm = False

while i < len(lines):
    line = lines[i]
    
    if 'def display_inventory_management' in line:
        new_lines.append(line)
        i += 1
        found_markdown = False
        markdown_lines = []
        
        while i < len(lines):
            current_line = lines[i]
            markdown_lines.append(current_line)
            
            if 'st.markdown' in current_line:
                found_markdown = True
            
            if found_markdown and 'unsafe_allow_html=True' in current_line:
                markdown_str = '\n'.join(markdown_lines)
                
                if '"""' in markdown_str and 'Inventory Management System' in markdown_str:
                    new_lines.append("    st.markdown('<div style=\"background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 24px; border-radius: 8px; margin-bottom: 20px; border-top: 3px solid #D97706;\"><h2 style=\"margin: 0; font-weight: 600;\">Inventory Management System</h2></div>', unsafe_allow_html=True)")
                    fixed_scm = True
                else:
                    for md_line in markdown_lines:
                        new_lines.append(md_line)
                
                i += 1
                break
            
            i += 1
    else:
        new_lines.append(line)
        i += 1

if fixed_scm:
    with open('app/scm_chain.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("✓ Fixed scm_chain.py")
else:
    print("⚠ Could not find pattern in scm_chain.py")

print("\n✅ Syntax error fixes attempted!")
