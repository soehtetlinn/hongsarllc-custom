# Product Course Link

## Description

This custom Odoo module automatically creates a course when a product is created and provides a complete one2many relationship between products and courses.

## Features

1. **Auto-Creation**: When a user creates a product, a course is automatically created with the same product name
2. **One2Many Relationship**: Each product can have multiple courses linked to it
3. **Form View Integration**: New "Courses" notebook page in product form view (positioned after Accounting page)
4. **Course Management**: View, create, and edit courses directly from the product form

## Module Structure

```
product_course_link/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── course.py          # Course model
│   └── product_template.py # Product template extension
├── views/
│   ├── course_views.xml   # Course tree/form/search views
│   └── product_template_views.xml # Product form extension
└── security/
    └── ir.model.access.csv # Access rights
```

## Installation

1. Place this module in your custom addons directory: `/home/odoo/custom/product_course_link`

2. Update the apps list in Odoo:
   ```bash
   # As odoo user
   odoo-bin -u all -d your_database --addons-path=/home/odoo/odoo18/odoo/addons,/home/odoo/custom
   ```

3. Or via Odoo UI:
   - Go to Apps → Update Apps List
   - Search for "Product Course Link"
   - Click Install

## Usage

### Creating a Product

1. When you create a new product, a course is automatically created with the same name
2. The course is linked to the product via the one2many relationship

### Viewing Courses

1. Open any product form view
2. Navigate to the "Courses" notebook page (after Accounting page)
3. View all courses linked to the product
4. Edit courses inline or create new ones

### Managing Courses

- **Add Course**: Click "Add a line" in the courses list on the product form
- **Edit Course**: Double-click on a course row to edit inline
- **View Course Details**: Open course form view for full details
- **Course Count**: See the number of courses in the stat button

## Models

### product.course

Fields:
- `name`: Course Name (required)
- `product_id`: Product (Many2one, required)
- `description`: Course Description
- `active`: Active status
- `create_date`: Creation date
- `create_uid`: Creator

### product.template (extended)

New Fields:
- `course_ids`: Courses (One2many)
- `course_count`: Courses Count (computed)

New Methods:
- `action_open_courses()`: Open courses linked to this product

## Views

### Product Form View

- New "Courses" notebook page with:
  - Stat button showing course count
  - Inline editable course list
  - Course form view for detailed editing

### Course Views

- Tree view: List of all courses
- Form view: Detailed course information
- Search view: Filter by name, product, active status

## Dependencies

- `product` module (standard Odoo module)

## Author

Soe Htet Linn

## License

LGPL-3

