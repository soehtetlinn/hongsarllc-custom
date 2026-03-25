# Product Default Code Generator

## Description

This custom Odoo module automatically generates the `default_code` (Internal Reference) for products based on:

1. **Category initials** - Extracted from the category path, excluding "All"
2. **Creator initials** - First 2 characters of the creator's name (user who created the product)
3. **Sequence number** - Sequential numbering (001, 002, etc.) based on category + creator combination

## Format

The generated code follows this pattern: `CSM_Tu001`

- **CSM**: Category initials (e.g., "All / Courses / SAT / Maths" → "CSM")
- **Tu**: User initials (e.g., "tutor1" → "tu")
- **001**: Sequence number (first product = 001, second = 002, etc.)

## Examples

| Category Path | Creator | Sequence | Result |
|--------------|---------|----------|--------|
| All / Courses / SAT / Maths | tutor1 | 1st | CSM_Tu001 |
| All / Courses / SAT / Maths | tutor1 | 2nd | CSM_Tu002 |
| All / Courses / SAT / Maths | tutor2 | 1st | CSM_Tt001 |
| All / Courses / English | tutor1 | 1st | CE_Tu001 |

## Installation

1. Place this module in your custom addons directory: `/home/odoo/custom/product_default_code_generator`

2. Update the apps list in Odoo:
   ```bash
   # As odoo user
   odoo-bin -u product_default_code_generator -d your_database
   ```

3. Or via Odoo UI:
   - Go to Apps → Update Apps List
   - Search for "Product Default Code Generator"
   - Click Install

## How It Works

- The `default_code` field is computed automatically when:
  - A product is created
  - The category (`categ_id`) changes
  - The creator (`create_uid`) changes

- The sequence number increments automatically for each product created by the same user in the same category

- Users can still manually edit the `default_code` if needed (the field is editable)

## Dependencies

- `product` module (standard Odoo module)

## Author

Custom Development

## License

LGPL-3

