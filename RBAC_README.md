# Role-Based Access Control (RBAC) Implementation

This document describes the role-based access control system implemented in the Vehicle Inspection Web App.

## Overview

The system now supports three distinct user roles with different permission levels:

### 1. Admin Role
- **Full system access** - can do everything
- **Staff Management**: Can add, edit, and delete any staff member (except cannot delete themselves)
- **Company Settings**: Full access to company configuration
- **Reports**: Can create, edit, delete, and manage all reports
- **System Logs**: Exclusive access to view, search, and delete system logs
- **Data Management**: Can delete customers, vehicles, and all data

### 2. Manager Role
- **Staff Management**: Can add and remove workers only, can edit themselves and workers
- **Reports**: Can create, edit reports, and view completed/cancelled reports (cannot delete)
- **Appointments**: Full access to appointment management
- **Customers/Vehicles**: Can add and edit but cannot delete
- **Restrictions**: Cannot access company settings, cannot edit admin data, cannot add other managers

### 3. Worker Role
- **Reports**: Can create and edit reports, view completed/cancelled reports (cannot delete)
- **Appointments**: Full access to appointment management  
- **Customers/Vehicles**: Can add and edit but cannot delete
- **Profile**: Can only edit their own profile
- **Restrictions**: Cannot add/edit other staff, cannot access company settings

## Key Features

### Role Display
- User roles are displayed in the navbar next to the username: "John Doe (Admin)"
- Available in both desktop and mobile views

### Staff Management Restrictions
- **Admin**: Sees all staff members, can manage everyone
- **Manager**: Sees themselves and workers only, can manage workers
- **Worker**: Sees only themselves, can edit own profile only

### Navigation Restrictions
- **Company Settings**: Only visible to admin users
- **System Logs**: Only visible to admin users (new feature)
- **Add Staff**: Only visible to admin and manager users

### Report Management
- **Deletion**: Only admin can delete reports, customers, and vehicles
- **Editing**: All roles can edit open reports, but completed/cancelled reports cannot be edited by anyone
- **Creation**: All roles can create reports and appointments

### System Logging
- **Admin-only feature**: Comprehensive logging of all system actions
- **Searchable**: Logs can be searched by action or details
- **Deletable**: Admin can delete individual log entries
- **Tracked Actions**: Login/logout, staff management, report operations, company changes

## Technical Implementation

### Files Added/Modified

#### New Files:
- `app/rbac.py` - Role-based access control decorators and functions
- `app/models/system_log.py` - System logging model
- `app/services/log_service.py` - Logging service functions
- `app/routes/logs.py` - System logs management routes
- `app/templates/logs/system_logs.html` - System logs interface
- `setup_rbac.py` - Database setup script

#### Modified Files:
- `app/forms/staff_form.py` - Updated role field to use SelectField
- `app/templates/navbar.html` - Added role display and admin-only links
- `app/templates/staff/staff_list.html` - Role-based UI restrictions
- `app/routes/staffs.py` - Role-based staff management
- `app/routes/reports.py` - Role-based report restrictions
- `app/routes/companies.py` - Admin-only company settings
- `app/routes/auth.py` - Login/logout logging
- `app/__init__.py` - Registered logs blueprint

### Database Changes
- Added `system_logs` table for audit trail
- Migration script: `migrations/versions/add_system_logs_table.py`

### Permission Functions
- `has_role(required_role)` - Check if user has required role level
- `role_required(role)` - Decorator for route protection
- `can_edit_staff(target_id)` - Staff editing permissions
- `can_delete_staff(target_id)` - Staff deletion permissions
- `can_delete_reports()` - Report deletion permissions
- `can_access_company_settings()` - Company settings access
- `can_access_logs()` - System logs access

## Setup Instructions

1. **Run the setup script**:
   ```bash
   python setup_rbac.py
   ```

2. **Default admin account**:
   - Phone: `000-000-0000`
   - Password: `admin123`
   - Role: Admin

3. **Start the application**:
   ```bash
   python run.py
   ```

## Usage Guidelines

### For Admins:
- Access system logs via Settings > System Logs
- Manage all staff members and roles
- Configure company settings
- Monitor system activity through logs

### For Managers:
- Add worker accounts through Staff Management
- Manage appointments and reports
- Cannot access system configuration

### For Workers:
- Focus on inspection tasks and report creation
- Edit own profile information
- Cannot manage other users

## Security Features

- **Session-based authentication** with role validation
- **Action logging** for audit trails
- **Permission checks** on all sensitive operations
- **UI restrictions** based on user roles
- **Data protection** through role-based access

## Logging System

The system logs all important actions including:
- User login/logout events
- Staff creation, updates, and deletion
- Report creation, completion, and cancellation
- Company settings changes
- System configuration changes

Logs include:
- Timestamp
- User information
- Action type
- Detailed description
- IP address
- Searchable content

## Future Enhancements

Potential improvements for the RBAC system:
- Branch-based access control
- Custom role definitions
- Permission inheritance
- Advanced audit reporting
- Role-based dashboard customization