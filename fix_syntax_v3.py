#!/usr/bin/env python3
"""Direct file rewrite to fix syntax errors"""

# Fix maintenance_dashboard.py function
maint_fix = '''def display_gearbox_diagnosis():
    st.title("⚙️ Predictive Maintenance & Diagnosis")
    st.markdown("AI-powered gearbox signal analysis with cost insights and maintenance recommendations")

    uploaded_file = st.file_uploader('''

with open('app/maintenance_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the function and replace until uploaded_file definition
import re
pattern = r'def display_gearbox_diagnosis\(\):.*?uploaded_file = st\.file_uploader\('
replacement = (
    'def display_gearbox_diagnosis():\n'
    '    st.title("⚙️ Predictive Maintenance & Diagnosis")\n'
    '    st.markdown("AI-powered gearbox signal analysis with cost insights and maintenance recommendations")\n'
    '\n'
    '    uploaded_file = st.file_uploader('
)

content = re.sub(pattern, replacement, content, flags=re.DOTALL, count=1)

with open('app/maintenance_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed maintenance_dashboard.py")

# Fix scm_chain.py function
with open('app/scm_chain.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'def display_inventory_management\(\):.*?st\.markdown\(["\'].*?Inventory Management System.*?["\'],\s*unsafe_allow_html=True\)'
replacement = (
    'def display_inventory_management():\n'
    '    st.subheader("📦 Inventory Management")'
)

content = re.sub(pattern, replacement, content, flags=re.DOTALL, count=1)

with open('app/scm_chain.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed scm_chain.py")

print("✅ Files fixed with simpler headers!")
