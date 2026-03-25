# Tutor Access Right Module - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Teaching Departments](#teaching-departments)
4. [User Management](#user-management)
5. [Tutor Groups](#tutor-groups)
6. [Tutor Access Rights](#tutor-access-rights)
7. [Linking Products and Courses](#linking-products-and-courses)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Tutor Access Right** module helps educational institutions manage:
- **User Types**: Differentiate between Students, Tutors, and Operators
- **Teaching Departments**: Organize users into departments with hierarchy
- **Tutor Groups**: Group tutors together for better management
- **Access Rights**: Control which tutors have access to specific products and courses

### Key Concepts

- **User Type**: Every login user must be classified as either:
  - **Student**: Regular student users
  - **Tutor**: Users who can teach and have access to courses/products
  - **Operator**: Administrative or support staff
  
- **Teaching Department**: Organizational unit that groups users (students, tutors, operators)
  
- **Tutor Group**: A group of tutors who work together or share similar responsibilities
  
- **Access Right**: Permission granted to a tutor (or tutor group) to access specific products or courses

---

## Getting Started

### Module Location

After installation, navigate to: **Tutor Management** (main menu)

You'll see three sub-menus:
1. **Teaching Departments**
2. **Tutor Groups**
3. **Tutor Access Rights**

### Prerequisites

- Module dependencies: `base`, `product`, `website_slides`
- Users must be created in Odoo's user management system
- Products and courses should be set up (if you want to link them)

---

## Teaching Departments

### Creating a Teaching Department

1. Go to **Tutor Management → Teaching Departments**
2. Click **Create**
3. Fill in the form:
   - **Department Name**: e.g., "Computer Science", "Mathematics"
   - **Code**: Optional department code (e.g., "CS", "MATH")
   - **Description**: Optional description
   - **Parent Department**: Optional - select if this is a sub-department
   - **Active**: Check to enable
4. Click **Save**

### Managing Users in Departments

1. Open a teaching department record
2. Go to the **Users** tab to see all users in this department
3. Go to the **Tutors** tab to see only tutors
4. You can filter users by type using the search filters

### Department Hierarchy

- Create parent departments (e.g., "Engineering")
- Create child departments (e.g., "Computer Engineering", "Electrical Engineering")
- Child departments automatically show counts from their parent's users

---

## User Management

### Setting User Type

1. Go to **Settings → Users & Companies → Users**
2. Open any user record
3. In the form, you'll see:
   - **User Type**: Select from dropdown:
     - **Student**: For student users
     - **Tutor**: For tutor/teacher users
     - **Operator**: For administrative staff
   - **Teaching Department**: Select the department this user belongs to
4. Click **Save**

⚠️ **Important**: Only users with `user_type='tutor'` can be assigned to tutor groups or have access rights.

### Tutor Information Tab

For users with `user_type='tutor'`, you'll see a new tab: **Tutor Information**

This tab shows:
- **Tutor Groups**: Groups this tutor belongs to
- **Access Rights**: All access rights granted to this tutor

### Changing User Type

⚠️ **Warning**: If you change a tutor's `user_type` to something other than 'tutor':
- They will be automatically removed from all tutor groups
- Their access rights will remain but won't be effective
- You'll receive a validation error if they still have tutor groups assigned

---

## Tutor Groups

### Creating a Tutor Group

1. Go to **Tutor Management → Tutor Groups**
2. Click **Create**
3. Fill in the form:
   - **Group Name**: e.g., "Advanced Math Tutors", "Programming Instructors"
   - **Description**: Optional description
   - **Teaching Department**: Optional - link to a teaching department
   - **Active**: Check to enable
4. Click **Save**

### Adding Tutors to a Group

1. Open a tutor group record
2. Go to the **Tutors** tab
3. Click **Add a line**
4. Select tutors from the dropdown
   - ⚠️ Only users with `user_type='tutor'` will appear in the list
5. Click **Save**

### Managing Group Resources

In a tutor group, you can link:

#### Products
1. Go to the **Products** tab
2. Click **Add a line**
3. Select products this group has access to
4. Products can be course enrollment products, materials, etc.

#### Courses
1. Go to the **Courses** tab
2. Click **Add a line**
3. Select courses (slide.channel) this group can access

### Stat Buttons

At the top of the tutor group form, you'll see buttons showing:
- **Access Rights**: Number of access rights defined for this group
- **Tutors**: Number of tutors in the group
- **Products**: Number of linked products
- **Courses**: Number of linked courses

Click any button to view the related records.

---

## Tutor Access Rights

### Creating an Access Right

1. Go to **Tutor Management → Tutor Access Rights**
2. Click **Create**
3. Fill in the form:

#### Basic Information
- **Tutor Group**: Select a tutor group (required)
- **Tutor**: Optionally select an individual tutor
  - ⚠️ Only tutors (`user_type='tutor'`) will appear
- **Access Type**: Select from:
  - **Read Only**: Can view but not modify
  - **Read/Write**: Can view and modify
  - **Full Access**: Complete access to the resource
  - **Instructor**: Can teach/manage the course

#### Resource Information
- **Product**: Link to a specific product
- **Product Template**: Link to a product template
- **Course**: Link to a course (slide.channel)

⚠️ **Note**: You can link to a product, product template, OR course. You don't need to link to all three.

#### Dates
- **Date Granted**: Automatically set to current date/time
- **Expiry Date**: Optional - set when access expires
  - Leave empty for no expiration
  - When expired, access is automatically deactivated

#### Additional
- **Active**: Check to enable this access right
- **Notes**: Optional notes about this access right

4. Click **Save**

### Access Right Name

The access right name is automatically computed from:
- Tutor Group name
- Tutor name (if individual tutor is specified)
- Resource name (product/course)
- Access type

Example: `Group: Math Tutors - Course: Calculus 101 - [Instructor]`

### Managing Access Rights

#### Viewing Access Rights
- From **Tutor Groups**: Click the **Access Rights** stat button
- From **Users**: Go to the **Tutor Information** tab → **Access Rights**
- From **Tutor Access Rights** menu: View all access rights in the system

#### Filtering Access Rights
Use the search filters:
- **Active/Inactive**: Filter by status
- **Expired/Not Expired**: Filter expired access rights
- **Group By**: Group by Tutor Group, Access Type, Date Granted, etc.

#### Expired Access Rights
- Expired access rights are automatically marked as inactive
- They appear in red in the list view
- You can reactivate them by setting a new expiry date and marking as active

---

## Linking Products and Courses

### Linking from Product

If you have the `product_course_link` module installed:
1. Open a product record
2. You'll see a **Courses** tab
3. Courses linked to product variants are shown here

### Linking from Course (slide.channel)

1. Open a course (slide.channel) record
2. Courses can be linked to products via the `product_id` field
3. Courses linked to tutor groups appear in the group's **Courses** tab

### Linking via Access Rights

The most flexible way to link is through **Tutor Access Rights**:

1. Create an access right
2. Link to either:
   - A **Product** (specific product variant)
   - A **Product Template** (all variants)
   - A **Course** (slide.channel)
3. Grant appropriate access type

---

## Common Workflows

### Workflow 1: Setting Up a New Department with Tutors

1. **Create Teaching Department**
   - Go to **Tutor Management → Teaching Departments**
   - Create department: "Computer Science"

2. **Assign Users to Department**
   - Go to **Settings → Users & Companies → Users**
   - For each tutor: Set `user_type='tutor'` and `teaching_department_id='Computer Science'`
   - For students: Set `user_type='student'` and `teaching_department_id='Computer Science'`

3. **Create Tutor Group**
   - Go to **Tutor Management → Tutor Groups**
   - Create group: "CS Instructors"
   - Set `teaching_department_id='Computer Science'`
   - Add tutors from the department

4. **Grant Access Rights**
   - Go to **Tutor Management → Tutor Access Rights**
   - Create access right for the tutor group
   - Link to relevant courses/products

### Workflow 2: Adding a New Course for Tutors

1. **Create/Open Course**
   - Go to **Website → eLearning → Courses**
   - Create or open a course (e.g., "Python Programming")

2. **Create Tutor Group** (if needed)
   - Go to **Tutor Management → Tutor Groups**
   - Create group: "Python Tutors"

3. **Grant Access**
   - Go to **Tutor Management → Tutor Access Rights**
   - Create access right:
     - Tutor Group: "Python Tutors"
     - Course: "Python Programming"
     - Access Type: "Instructor"

### Workflow 3: Temporary Access for a Tutor

1. **Create Individual Access Right**
   - Go to **Tutor Management → Tutor Access Rights**
   - Create access right:
     - Tutor Group: (select group)
     - Tutor: (select specific tutor)
     - Course/Product: (select resource)
     - Date Granted: (today)
     - **Expiry Date**: (set future date, e.g., 30 days from now)
     - Access Type: (appropriate level)

2. **Monitor Expiration**
   - Regularly check for expired access rights
   - Filter by "Expired" to see what needs renewal

### Workflow 4: Changing Tutor's Department

1. **Open User Record**
   - Go to **Settings → Users & Companies → Users**
   - Open the tutor's record

2. **Update Teaching Department**
   - Change `teaching_department_id` to new department

3. **Update Tutor Groups** (if needed)
   - If tutor groups are department-specific, update them
   - Or create new groups in the new department

---

## Troubleshooting

### Issue: "Only tutors can be assigned to tutor groups"

**Problem**: You're trying to assign a non-tutor user to a tutor group.

**Solution**:
1. Go to **Settings → Users & Companies → Users**
2. Open the user record
3. Change `user_type` to **'Tutor'**
4. Save and try again

### Issue: "Can't find tutors in dropdown"

**Problem**: No tutors appear when trying to add to a tutor group.

**Solutions**:
- Check that users have `user_type='tutor'`
- Verify users are active (`active=True`)
- Check that users are login users (`share=False`), not portal/public users

### Issue: "Access right not working"

**Problem**: Tutor can't access the resource despite having an access right.

**Solutions**:
- Check that the access right is **Active**
- Verify the **Expiry Date** hasn't passed
- Confirm the tutor is linked (either individually or through the tutor group)
- Check the **Access Type** matches the required permissions

### Issue: "Can't see Tutor Information tab"

**Problem**: User form doesn't show tutor-related information.

**Solution**:
- The tab only appears for users with `user_type='tutor'`
- Change the user's `user_type` to 'tutor'

### Issue: "Department counts are wrong"

**Problem**: Department shows incorrect tutor/student/operator counts.

**Solutions**:
- Check that users have the correct `user_type` set
- Verify users have `teaching_department_id` set correctly
- Refresh the page or reload the record

### Issue: "Can't create teaching department"

**Problem**: Permission error when creating departments.

**Solution**:
- Verify you have the required access rights
- Check that the module is properly installed
- Contact your system administrator

---

## Best Practices

1. **Organize by Department First**
   - Create teaching departments before assigning users
   - Use department hierarchy for better organization

2. **Use Tutor Groups for Teams**
   - Group tutors who work together
   - Makes it easier to manage access rights

3. **Set Expiry Dates**
   - For temporary access, always set expiry dates
   - Regularly review and renew expired access

4. **Name Conventions**
   - Use clear, descriptive names for departments and groups
   - Include department code in group names if helpful

5. **Regular Audits**
   - Periodically review access rights
   - Remove inactive or expired access
   - Verify tutors still need their current access levels

6. **Documentation**
   - Use the "Notes" field in access rights to document why access was granted
   - Add descriptions to tutor groups for clarity

---

## Field Reference

### User Type Field (`res.users.user_type`)
- **Values**: `'student'`, `'tutor'`, `'operator'`
- **Required**: Yes
- **Default**: `'student'`

### Access Type Field (`tutor.access.right.access_type`)
- **Values**: 
  - `'read'`: Read Only
  - `'write'`: Read/Write
  - `'full'`: Full Access
  - `'instructor'`: Instructor
- **Required**: Yes
- **Default**: `'read'`

---

## Support

For technical issues or questions:
- Check this user guide
- Review the module's code comments
- Consult your system administrator
- Check Odoo's official documentation

---

**Module Version**: 18.1.0.0.0  
**Last Updated**: 2024

