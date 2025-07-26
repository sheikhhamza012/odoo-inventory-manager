# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [17.0.1.2.0] - 2025-01-26

### Added
- **Dual-Level BOM Validation**: Enhanced validation system with both product click and order confirmation validation
- **Real-time Stock Checking**: Immediate validation when products are selected in POS
- **Fallback Data Loading**: Automatically fetches BOM data if not initially loaded
- **Enhanced Error Handling**: Clear, specific error messages showing which components lack stock
- **POS Configuration Integration**: Added `enable_bom_validation` field to control validation per POS
- **Debug Support**: Comprehensive debugging tools and console helpers
- **Browser Console Helpers**: `bomDebug` object with multiple debugging functions
- **Backend Testing Scripts**: Complete test suite for validation logic
- **Enhanced Documentation**: Comprehensive README with troubleshooting guides

### Changed
- **JavaScript Architecture**: Migrated to proper Odoo 17 ORM service usage
- **RPC Calls**: Updated to use `this.env.services.orm.call` instead of deprecated RPC format
- **Validation Flow**: Improved validation workflow with multiple entry points
- **Error Messages**: Enhanced user feedback with detailed component information
- **Data Loading**: Improved BOM data loading in POS session

### Fixed
- **JavaScript Syntax**: Removed Python-style docstrings causing syntax errors
- **Translation Functions**: Fixed `this.env._t is not a function` errors
- **RPC URL Issues**: Resolved malformed URL issues in RPC calls (`[object Object]`)
- **Undefined BOM Fields**: Added fallback data fetching for missing BOM information
- **Async/Await Handling**: Proper async handling in validation methods

### Technical
- **Models Enhanced**: Extended `product.template`, `pos.order`, `pos.session`, `pos.config`
- **New Methods**: Added `validate_bom_stock()`, `validate_bom_stock_rpc()`, `validate_order_bom_stock()`
- **Frontend Patches**: Enhanced JavaScript patches for PosStore and Order models
- **Debug Tools**: Added comprehensive debugging and testing infrastructure

## [17.0.1.0.0] - 2024-XX-XX

### Added
- Initial release of POS BOM Integration
- Basic BOM validation functionality
- Automatic inventory deduction for BOM components
- Product template integration with BOM fields
- POS order processing with BOM data
- Basic error handling for insufficient stock

### Features
- Integration with Odoo Manufacturing (MRP) module
- BOM component tracking in POS orders
- Automatic stock moves creation for BOM components
- Product form enhancements for BOM configuration
