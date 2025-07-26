# Debug Tools for POS BOM Integration

This folder contains essential debugging and testing tools for the POS BOM Integration module.

## Files Overview

### Frontend Debug Tools
- **`console_helpers.js`** - Comprehensive browser console debugging functions with `bomDebug` object

### Backend Test Scripts
- **`test_enhanced_validation.py`** - Main validation testing script with comprehensive test coverage
- **`test_backend_data.py`** - Backend data loading verification and troubleshooting

### Documentation
- **`README.md`** - This file with usage instructions and debugging guides

## Usage

### Browser Console Debugging

1. Open POS interface
2. Open browser DevTools (F12) → Console tab
3. Copy and paste contents of `console_helpers.js`
4. Use available methods:
   ```javascript
   bomDebug.checkAllProducts()           // List all BOM products
   bomDebug.testValidation('product')    // Test validation for specific product
   bomDebug.refreshProductBomData('product') // Refresh BOM data
   bomDebug.testAddProduct('product')    // Test adding product to order
   ```

### Backend Testing

Run in Odoo shell:
```python
# Main validation test
exec(open('addons/pos_bom_integration/debug/test_enhanced_validation.py').read())
test_enhanced_validation()

# Backend data loading test
exec(open('addons/pos_bom_integration/debug/test_backend_data.py').read())
test_backend_bom_data()
```

## Quick Debugging Guide

### 1. BOM Fields Showing as Undefined
- Run `bomDebug.checkAllProducts()` in console
- Use `bomDebug.refreshProductBomData('product_name')` to reload data

### 2. Validation Not Working on Product Click
- Check browser console for error messages
- Run `test_enhanced_validation.py` in Odoo shell to check backend

### 3. Data Loading Problems
- Run `test_backend_data.py` to verify backend data loading
- Check if POS session properly loads BOM fields

## File Organization

```
debug/
├── README.md                    # This documentation
├── console_helpers.js          # Browser console debug tools
├── test_enhanced_validation.py # Main backend testing
└── test_backend_data.py        # Data loading verification
```

## Notes

- Debug files are excluded from production deployments
- Console helpers provide real-time debugging without server restarts
- Always test both frontend and backend components when debugging
