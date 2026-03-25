# User Creation and Department Assignment Guide

## Overview

This guide explains who creates users and how to assign them to departments and groups in the Tutoring Module.

## Who Creates Users?

### Primary User Creators:

1. **System Administrators** (Administration Department)
   - Have full access to create any user
   - Can create users via: **Settings → Users & Companies → Users → Create**

2. **HR Personnel** (if they have user creation rights)
   - Typically in Administration or Operations departments
   - Can create users through the same interface

### Standard Odoo User Creation Process:

1. Navigate to **Settings → Users & Companies → Users**
2. Click **Create**
3. Fill in:
   - **Name**: User's full name
   - **Email**: User's email address
   - **Login**: Username for login
   - **Password**: Set initial password
   - **User Type**: Select Student, Tutor, or Operator
   - **Teaching Department**: Select the department (Administration, Marketing, Operations, or Teachers)
   - **Groups**: User groups (will be auto-assigned based on department)

4. Click **Save**

## Automatic Group Assignment

### How It Works:

When you assign a user to a department (`teaching_department_id`), the system **automatically**:

1. **Assigns the department's group** to the user
   - If department has a `group_id` linked, user is automatically added to that group
   - This happens automatically on user creation and when department is changed

2. **Enforces menu visibility** based on department:
   - **Administration**: Full access to all menus
   - **Marketing**: Only Marketing + Website (Restricted Content) menus
   - **Operations**: All menus except Admin + Marketing
   - **Teachers**: eLearning, Sale, Chatting, Website Restricted, Meeting, Appointment, Calendar, Tutoring

### Example Workflow:

```
1. Admin creates new user: "John Doe"
2. Sets User Type: "Tutor"
3. Sets Teaching Department: "Teachers"
4. System automatically:
   - Assigns user to "Department: Teachers" group
   - User can now see: eLearning, Sale, Chatting, Website, Meeting, Appointment, Calendar, Tutoring menus
```

## Manual Assignment Methods

### Method 1: From User Form

1. Go to **Settings → Users & Companies → Users**
2. Open a user record
3. Set **Teaching Department** field
4. Save → User is automatically assigned to department's group

### Method 2: Bulk Assignment via Wizard

1. **From Department View:**
   - Go to **Employees → Departments**
   - Open a department (e.g., "Teachers")
   - Click **"Assign Users to Department"** button
   - Select multiple users
   - Click **"Assign to Department"**

2. **From Users List:**
   - Select multiple users (checkboxes)
   - Use **Action → Assign Users to Department** (if menu item added)
   - Select department
   - Confirm

### Method 3: Direct Group Assignment (if needed)

If you need to manually assign groups:

1. Go to **Settings → Users & Companies → Users**
2. Open user record
3. Go to **Access Rights** tab
4. Edit **Groups** field
5. Add/remove groups as needed

⚠️ **Note**: Manual group assignment will be overridden if user's department changes!

## Department-Group Linking Setup

### Initial Setup (Done by Admin):

1. **Go to Employees → Departments**
2. Open each department:
   - **Administration**
   - **Marketing**
   - **Operations**
   - **Teachers**
3. For each department:
   - Set **Access Group** field
   - Link to the corresponding group:
     - Administration → `Department: Administration`
     - Marketing → `Department: Marketing`
     - Operations → `Department: Operations`
     - Teachers → `Department: Teachers`

### Automatic Setup on Module Install:

The module automatically:
- Creates 4 department groups
- Links existing departments to their groups (if departments named "Administration", "Marketing", "Operations", "Teachers" exist)

## Step-by-Step: Creating and Assigning a New User

### Scenario: Create a new Teacher

1. **Log in as Administrator**

2. **Create User:**
   - Go to **Settings → Users & Companies → Users**
   - Click **Create**
   - Fill in:
     - Name: "Jane Smith"
     - Email: jane.smith@example.com
     - Login: jane.smith
     - Password: (set password)
     - User Type: **Tutor**
     - Teaching Department: **Teachers**

3. **Save** → System automatically:
   - Assigns user to "Department: Teachers" group
   - User will see only: eLearning, Sale, Chatting, Website Restricted, Meeting, Appointment, Calendar, Tutoring menus

4. **User can now log in** with restricted menu access

### Scenario: Change User's Department

1. **Open User Record:**
   - Go to **Settings → Users & Companies → Users**
   - Find and open user "John Doe"

2. **Change Department:**
   - Change **Teaching Department** from "Operations" to "Teachers"
   - Save

3. **System automatically:**
   - Removes user from "Department: Operations" group
   - Adds user to "Department: Teachers" group
   - Updates menu visibility accordingly

## Troubleshooting

### User Not Getting Group Assigned

**Problem**: User assigned to department but not getting group.

**Solutions**:
1. Check if department has `group_id` set:
   - Go to **Employees → Departments**
   - Open department
   - Verify **Access Group** field is set

2. Manually trigger sync:
   - Remove user from department
   - Save
   - Re-add user to department
   - Save

3. Check user's groups manually:
   - Open user record
   - Go to **Access Rights** tab
   - Check if department group is listed

### Wrong Menu Visibility

**Problem**: User sees wrong menus for their department.

**Solutions**:
1. Verify department name matches exactly:
   - "Administration" (not "Admin" or "Administrative")
   - "Marketing" (exact match)
   - "Operations" (exact match)
   - "Teachers" or "Teacher" (both work)

2. Check user's department:
   - Open user record
   - Verify **Teaching Department** field

3. Clear browser cache and refresh

4. Check if user has other groups overriding visibility

### Bulk Assignment Not Working

**Problem**: Wizard not assigning users correctly.

**Solutions**:
1. Check wizard permissions
2. Ensure users are active (`active=True`)
3. Verify department has `group_id` set
4. Try assigning one user at a time first

## Best Practices

1. **Always set Teaching Department when creating users**
   - Don't create users without departments
   - Ensures proper access from the start

2. **Use the wizard for bulk assignments**
   - More efficient for multiple users
   - Less error-prone

3. **Verify department-group links**
   - Periodically check that departments have groups linked
   - Essential for automatic assignment to work

4. **Document department changes**
   - Keep track of when users change departments
   - Helps with auditing and troubleshooting

5. **Test with one user first**
   - Before bulk assignments, test with a single user
   - Verify menu visibility is correct

## Security Considerations

- **Only Administrators** should create users and assign departments
- **Department managers** may need read-only access to see their department users
- **Regular users** should NOT be able to change their own department
- Use **Access Rights** settings to control who can create/modify users

---

**Last Updated**: 2024  
**Module Version**: 18.1.0.0.0

