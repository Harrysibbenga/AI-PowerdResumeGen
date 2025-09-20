# Certification Date Format Guide

## ✅ Recommended Format: **YYYY-MM**

### Input Examples:
- `2023-06` → June 2023
- `2022-11` → November 2022  
- `2024-03` → March 2024
- `2021-01` → January 2021
- `2025-12` → December 2025

### Why YYYY-MM Format?

1. **ISO 8601 Standard**: International standard for date representation
2. **Database Compatible**: Works with all major databases and APIs
3. **Sortable**: Dates sort correctly alphabetically
4. **HTML5 Native**: Perfect for `<input type="month">` elements
5. **Unambiguous**: No confusion between day/month order

### UI Features:

#### HTML5 Month Picker:
```html
<input type="month" value="2023-06" placeholder="YYYY-MM" />
```
- Shows native date picker
- Automatically validates format
- Easy to use on mobile devices

#### Auto-formatting:
The component automatically converts these formats to YYYY-MM:
- `06-10-2023` → `2023-06`
- `06/2023` → `2023-06`
- `2023-06-15` → `2023-06`

#### Display Format:
For user display, dates show as:
- `2023-06` displays as "June 2023"
- `2022-11` displays as "November 2022"

### Example Certification Data:
```javascript
{
  name: "CompTIA Security+",
  issuer: "CompTIA", 
  date: "2023-06",           // June 2023
  expiryDate: "2026-06",     // June 2026
  credentialId: "COMP001234567"
}
```

### Benefits for Resume Building:
- **Professional**: Standard format expected by ATS systems
- **Precise**: Month-level accuracy without day confusion
- **Future-proof**: Compatible with all modern systems
- **Global**: Works in any locale/country