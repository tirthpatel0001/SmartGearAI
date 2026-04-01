#!/usr/bin/env python3
"""Fix syntax errors in design updates"""
import re

# Fix maintenance_dashboard.py
with open('app/maintenance_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace triple-quoted strings with proper string concatenation
pattern1 = r'st\.markdown\(\s*"""\s*<div style="background: linear-gradient\(135deg, #1E3A5F.*?Predictive Maintenance.*?</div>\s*""",\s*unsafe_allow_html=True\)'

new_code_maint = (
    "st.markdown(\n"
    "    '<div style=\"background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 32px; border-radius: 8px; margin-bottom: 24px; border-top: 4px solid #D97706;\">' +\n"
    "    '<h1 style=\"margin: 0; font-size: 2.2em; font-weight: 700;\">⚙️ Predictive Maintenance & Diagnosis</h1>' +\n"
    "    '<p style=\"margin: 8px 0 0 0; opacity: 0.95;\">AI-powered gearbox signal analysis with cost insights and maintenance recommendations</p>' +\n"
    "    '</div>',\n"
    "    unsafe_allow_html=True\n"
    ")"
)

content = re.sub(pattern1, new_code_maint, content, flags=re.DOTALL)

with open('app/maintenance_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed maintenance_dashboard.py")

# Fix scm_chain.py  
with open('app/scm_chain.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern2 = r'st\.markdown\(\s*"""\s*<div style="background: linear-gradient\(135deg, #1E3A5F.*?Inventory Management System.*?</div>\s*""",\s*unsafe_allow_html=True\)'

new_code_scm = (
    "st.markdown(\n"
    "    '<div style=\"background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 24px; border-radius: 8px; margin-bottom: 20px; border-top: 3px solid #D97706;\">' +\n"
    "    '<h2 style=\"margin: 0; font-weight: 600;\">Inventory Management System</h2>' +\n"
    "    '</div>',\n"
    "    unsafe_allow_html=True\n"
    ")"
)

content = re.sub(pattern2, new_code_scm, content, flags=re.DOTALL)

with open('app/scm_chain.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed scm_chain.py")

print("\n✅ All syntax errors fixed!")

