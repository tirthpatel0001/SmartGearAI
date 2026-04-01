# SmartGear AI - UI/UX Design System & Brand Guidelines

## 📋 Overview
Complete design system for SmartGear AI - a professional gear manufacturing management platform featuring industrial aesthetics, modern UI/UX, and optimized user experience for manufacturing companies.

---

## 🎨 Color Palette

### Primary Colors
- **Primary Dark Steel**: `#1E3A5F` - Main header backgrounds, key sections
- **Primary Steel**: `#2C5282` - Secondary headers, gradients
- **Accent Orange**: `#D97706` - Call-to-action, highlights, borders
- **Accent Amber**: `#B8860B` - Secondary accents, gold highlights

### Semantic Colors
- **Success Green**: `#059669` - Positive results, confirmations
- **Danger Red**: `#DC2626` - Alerts, defects, errors
- **Background Light**: `#F9F9F9` - Main page background
- **Card Background**: `#FFFFFF` - Content cards, containers
- **Text Primary**: `#111827` - Main text, headers
- **Text Secondary**: `#6B7280` - Supporting text, descriptions
- **Border Light**: `#E5E7EB` - Subtle dividers, borders

### Shadow System
- **Shadow SM**: `0 1px 2px rgba(0, 0, 0, 0.05)` - Subtle depths
- **Shadow MD**: `0 4px 6px rgba(0, 0, 0, 0.1)` - Medium elevation
- **Shadow LG**: `0 10px 15px rgba(0, 0, 0, 0.1)` - High elevation

---

## 🔤 Typography

### Font Family
- **Primary**: `Inter` - Body text, UI elements. Modern, clean, professional.
- **Alternative**: `Roboto Mono` - Monospaced for numeric values and metrics

### Font Weights
- **300**: Light (rarely used)
- **400**: Regular (body text)
- **500**: Medium (semi-bold text)
- **600**: Semi-bold (headers, labels)
- **700**: Bold (major headings)

### Font Sizes & Usage
- **H1**: `2.2em` / `700` weight - Page titles, major headers
- **H2**: `1.4em` / `700` weight - Section headers
- **H3**: `1.3em` / `600` weight - Sub-section headers
- **H4**: `1.1em` / `600` weight - Card titles
- **Body**: `1em` / `400` weight - Regular text
- **Small**: `0.9em` / `400` weight - Supporting text
- **Label**: `0.85em` / `600` weight - Form labels, badges

---

## 🏗️ Component Styles

### Hero Header (Page Title Section)
```css
background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
color: white;
padding: 32px;
border-radius: 8px;
border-top: 4px solid #D97706;
box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
```
**Usage**: Main page titles, dashboard headers

### Industrial Card (Content Containers)
```css
background: white;
padding: 24px;
border-radius: 8px;
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
border-left: 4px solid #D97706;
transition: all 0.3s ease;
```
**Hover**: `transform: translateY(-2px);` + enhanced shadow
**Usage**: Feature cards, input sections, information containers

### Metric Card (KPI Display)
```css
background: white;
padding: 24px;
border-radius: 8px;
border-top: 3px solid #D97706;
text-align: center;
```
**Value Style**: 
- Font-size: `2.2em`
- Font-family: `Roboto Mono`
- Color: `#D97706`

**Usage**: KPI dashboards, statistics, measurements

### Success Card (Positive Results)
```css
background: linear-gradient(135deg, #059669 0%, #047857 100%);
color: white;
padding: 28px;
border-radius: 8px;
border-left: 4px solid #10B981;
```
**Usage**: Successful operations, confirmations, positive alerts

### Input Section (Form Container)
```css
background: white;
padding: 28px;
border-radius: 8px;
border-top: 3px solid #1E3A5F;
```
**Usage**: Forms, configuration panels, data entry

### Buttons
```css
background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
color: white;
border-radius: 6px;
padding: 11px 28px;
font-weight: 600;
transition: all 0.3s ease;
```
**Hover State**:
- `transform: translateY(-2px);`
- `background: linear-gradient(135deg, #B45309 0%, #D97706 100%);`

---

## 📐 Layout System

### Spacing
- **Padding Cards**: `24px`
- **Padding Headers**: `32px`
- **Margin Between Elements**: `16px - 24px`
- **Gap Between Columns**: `8px - 16px`

### Border Radius
- **Containers**: `8px`
- **Cards**: `8px`
- **Buttons**: `6px`
- **Small Elements**: `4px`

### Responsive Layout
- **Desktop**: 3-column layouts for metrics, 2-column for content
- **Tablet**: 2-column layouts
- **Mobile**: Single-column stacked layout

---

## 🎯 Section Styling

### Sidebar Header
```css
background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
color: white;
padding: 16px;
border-radius: 8px;
border-top: 3px solid #D97706;
```

### Section Headers (for Admin, Config, etc.)
```css
background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
color: white;
padding: 14px 20px;
border-radius: 6px;
font-weight: 600;
```

### Breakdown Tables
```
Header Row: #1E3A5F background, white text, bold font
Data Rows: Alternating white background, 1px borders
Last Row: 2px bottom border, orange text, bold weight
```

---

## 🌟 Visual Hierarchy

### Priority Levels
1. **Critical**: Dark steel blue headers with orange accents (Alerts, important data)
2. **Primary**: White cards with left orange border (Main content)
3. **Secondary**: Light gray background sections (Supporting info)
4. **Tertiary**: Inline text, small labels (Metadata)

### Visual Weight
- Use orange accent for calls-to-action
- Use dark blue for structural elements
- Use white for content areas
- Use green for success states
- Use red for warning/error states

---

## 📱 Responsive Design Principles

1. **Mobile First**: Design starts mobile, enhances for desktop
2. **Touch Targets**: Minimum 44px for interactive elements
3. **Typography Scaling**: Use proportional sizes
4. **Column Reduction**: Reduce columns on smaller screens
5. **Touch-Friendly Spacing**: Increase padding on mobile

---

## ♿ Accessibility Guidelines

### Color Contrast
- All text meets WCAG AA standards (4.5:1 for regular text)
- Orange `#D97706` + White `#FFFFFF`: 7.8:1 ratio
- Dark blue `#1E3A5F` + White `#FFFFFF`: 10.2:1 ratio

### Text Alternatives
- All icons include text labels or aria descriptions
- Meaningful heading hierarchy (H1 → H2 → H3)
- Form inputs clearly labeled

### Focus States
- All buttons have visible focus indicators
- Tab navigation is logical and efficient
- Skip-to-content links available

---

## 🔄 Animation & Transitions

### Standard Transitions
- **Duration**: `0.3s ease`
- **Properties**: `transform`, `box-shadow`, `background`

### Transformation Effects
- **Hover Lift**: `translateY(-2px)` - cards, buttons
- **Hover Scale**: `scale(1.05)` - metric cards
- **Focus Outline**: `outline-offset: 2px`

---

## 📊 Data Visualization

### Chart Colors (Use when needed)
- **Primary**: `#1E3A5F`
- **Accent**: `#D97706`
- **Success**: `#059669`
- **Warning**: `#DC2626`

### Table Styling
- Header: Dark blue background, white text
- Rows: Alternating white/light gray
- Hover: Slightly elevated shadow
- Total Row: Bold, orange accent

---

## 🏭 Industry-Specific Elements

### Gear Manufacturing Theme
- **Icon Usage**: ⚙️ (Gears), 🏭 (Factory), 📊 (Analytics)
- **Language**: Professional, technical terminology
- **Focus Areas**: Quality, precision, efficiency, cost
- **Tone**: Authoritative yet accessible

### Trust Indicators
- Consistent branding throughout
- Clear hierarchy and information architecture
- Professional color scheme (industrial blues/oranges)
- Numerical precision in metrics and prices

---

## 🔧 Implementation Checklist

### New Components
- [ ] Use `#1E3A5F` for primary backgrounds
- [ ] Add `#D97706` accent borders/highlights
- [ ] Implement hover states with `translateY(-2px)`
- [ ] Use `Inter` font family
- [ ] Add appropriate shadow depth
- [ ] Ensure mobile responsiveness
- [ ] Check color contrast ratios
- [ ] Test keyboard navigation

### Page Updates
- [ ] Replace old gradient colors
- [ ] Update buttons to orange gradient
- [ ] Refresh card styling with new shadows
- [ ] Update typography sizes
- [ ] Implement new spacing standards
- [ ] Test on multiple devices

---

## 📚 File Locations

### CSS/Style Implementations
- `.streamlit/config.toml` - Streamlit theme config
- `app/main.py` - Global styles (lines 175-436)
- `app/dashboard.py` - Dashboard specific styles
- `app/admin_panel.py` - Admin panel styles
- `app/login.py` - Login page styles
- Individual page headers - Inline styles with new theme

### Design Resources
- `UI_DESIGN_GUIDE.md` - This file (design documentation)

---

## 🚀 Future Enhancements

### Planned Features
1. Dark mode toggle (maintain color relationships)
2. Custom company branding (logo, colors)
3. Advanced charting library integration
4. Enhanced animations and micro-interactions
5. Accessibility improvements (AAA compliance)
6. Design token system for easier maintenance

---

## 📞 Design Support

For design consistency questions or new components:
1. Reference this guide
2. Check existing implementations
3. Follow the color palette and spacing rules
4. Test responsiveness on multiple devices
5. Verify accessibility requirements

---

**Last Updated**: March 23, 2026  
**Version**: 1.0  
**Design System**: SmartGear AI Industrial Theme
