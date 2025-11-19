# Feature Specification: Admin User and Writer Management Interface

**Feature Branch**: `4-admin-users`
**Created**: 2025-11-19
**Status**: In Review
**Input**: Admin customization requirements for user and writer management

## User Scenarios & Testing

### User Story 1 - Admin Can View All Users with Role Information (Priority: P1)

Admins need a comprehensive list of all users showing their role (reader, writer, admin), allowing them to understand the user base and manage roles.

**Why this priority**: Critical for user management. Admins must see who is in the system and their role.

**Independent Test**: Can be verified by: (1) ProfileAdmin shows all users, (2) Role column displays in list view, (3) Users can be filtered by role, (4) Users can be searched by username, (5) List displays username, email, role, account status.

**Acceptance Scenarios**:

1. **Given** admin opens Django admin for Users/Profiles, **When** list view loads, **Then** all users are displayed with role visible in list
2. **Given** admin wants to see only writers, **When** they use role filter, **Then** only users with role='writer' are shown
3. **Given** admin wants to see only admins, **When** they use role filter, **Then** only users with role='admin' are shown
4. **Given** admin searches for username "john", **When** search is applied, **Then** user with username containing "john" is found and displayed

---

### User Story 2 - Admin Can Promote Users to Writer or Admin (Priority: P1)

Admins should be able to change user roles: promote readers to writers, promote writers to admins, or demote if needed.

**Why this priority**: Critical for user management workflow. Admins must be able to change roles.

**Independent Test**: Can be verified by: (1) Role field is editable in profile detail view, (2) Role dropdown shows all role options, (3) Role change is saved to database, (4) User gains/loses permissions based on new role.

**Acceptance Scenarios**:

1. **Given** a user with role='reader', **When** admin changes role to 'writer' and saves, **Then** user's profile is updated and they can create articles
2. **Given** a writer user, **When** admin changes role to 'admin' and saves, **Then** user's profile is updated and they can access admin panel
3. **Given** admin user, **When** admin changes role back to 'reader' and saves, **Then** user can no longer access admin panel
4. **Given** role is changed, **When** user logs out and logs back in, **Then** new permissions take effect immediately

---

### User Story 3 - Admin Can Manage User Accounts (Priority: P1)

Admins should be able to view, edit, and deactivate user accounts (mark as inactive) without deleting them.

**Why this priority**: Critical for account management. Admins need to disable problematic accounts.

**Independent Test**: Can be verified by: (1) UserAdmin shows is_active checkbox, (2) Unchecking is_active prevents login, (3) User data is preserved (not deleted), (4) User can be reactivated later.

**Acceptance Scenarios**:

1. **Given** admin opens user detail in admin, **When** they uncheck is_active box and save, **Then** user cannot log in
2. **Given** user is inactive, **When** they try to log in, **Then** authentication fails with appropriate message
3. **Given** inactive user, **When** admin checks is_active box again and saves, **Then** user can log in again
4. **Given** user account is deactivated, **When** admin inspects account, **Then** user's data (posts, comments, etc.) is still visible

---

### User Story 4 - Admin Can View Writer Bulletin Information (Priority: P2)

Admins should be able to see which writers have bulletins, how many articles each has, and access the bulletin information.

**Why this priority**: Important for understanding writer activity. Admin can see which writers are active.

**Independent Test**: Can be verified by: (1) WriterAdmin or ProfileAdmin shows bulletin link for writers, (2) Article count is displayed, (3) Admin can click to view writer's bulletin, (4) Article count is accurate and up-to-date.

**Acceptance Scenarios**:

1. **Given** admin views profile of a writer, **When** they look at the profile detail, **Then** they see: Bulletin Title, Article Count, Subscriber Count
2. **Given** writer has 42 articles, **When** admin views article count, **Then** count shows "42" (accurate)
3. **Given** admin clicks on bulletin link, **When** clicked, **Then** they're taken to bulletin detail or admin BulletinAdmin interface
4. **Given** new article is published by writer, **When** admin refreshes, **Then** article count is updated

---

### User Story 5 - Admin Can See User Engagement Metrics (Priority: P2)

Admins should be able to see user activity: how many articles they've written, how many likes/comments they've received, how many bulletins they're subscribed to.

**Why this priority**: Important for understanding user engagement. Admin can identify active/inactive users.

**Independent Test**: Can be verified by: (1) ProfileAdmin shows engagement metrics, (2) Metrics include: articles written, comments received, likes received, subscriptions, (3) Metrics are accurate and up-to-date.

**Acceptance Scenarios**:

1. **Given** admin views writer profile, **When** they look at metrics, **Then** they see: Articles Written (42), Likes Received (156), Comments Received (23), Subscribers (8)
2. **Given** reader's profile is viewed, **When** metrics are displayed, **Then** they see: Articles Liked (12), Comments Posted (5), Bulletins Subscribed (3)
3. **Given** new engagement happens (like, comment, subscription), **When** admin refreshes profile, **Then** metrics are updated
4. **Given** user is inactive for months, **When** admin looks at last activity date, **Then** timestamp shows when user was last active

---

### User Story 6 - Admin Can Filter Users by Role and Activity (Priority: P2)

Admins should be able to filter users to see: all writers, all admins, inactive users, users with no activity.

**Why this priority**: Important for user management at scale. Helps admin find specific user cohorts.

**Independent Test**: Can be verified by: (1) Role filter shows only selected role, (2) Activity filter shows only active/inactive users, (3) Multiple filters can be combined, (4) Results update immediately.

**Acceptance Scenarios**:

1. **Given** admin selects role='writer' filter, **When** filter is applied, **Then** only writer profiles are shown
2. **Given** admin selects is_active=False filter, **When** filter is applied, **Then** only inactive user profiles are shown
3. **Given** admin combines role='writer' AND is_active=True filters, **When** filters are applied, **Then** only active writers are shown
4. **Given** filters are applied, **When** admin clicks "Clear Filters", **Then** all users are shown again

---

### Edge Cases

- What if admin deactivates themselves? (Handled: Django allows it; they can still be reactivated by other admin via database)
- What if user has no bulletin (reader)? (Handled: Bulletin field is empty/null, displays as "None" or "-")
- What if writer has 0 articles? (Handled: Article count shows "0", not an error)
- What if user deletes their own account? (Out of scope: user management focuses on admin actions, not self-deletion)

---

## Requirements

### Functional Requirements

- **FR-001**: ProfileAdmin MUST display all users with role information visible in list view
- **FR-002**: ProfileAdmin MUST provide filter for role: reader, writer, admin
- **FR-003**: ProfileAdmin MUST provide filter for is_active: active, inactive
- **FR-004**: ProfileAdmin MUST allow editing role field in detail view (dropdown with role choices)
- **FR-005**: ProfileAdmin MUST allow editing is_active checkbox to deactivate/reactivate users
- **FR-006**: ProfileAdmin MUST show bulletin information for writers (bulletin name, article count, subscriber count)
- **FR-007**: ProfileAdmin MUST show engagement metrics: articles written, likes received, comments received, subscriptions
- **FR-008**: ProfileAdmin MUST display last login date (when user was last active)
- **FR-009**: ProfileAdmin MUST provide search by username and email
- **FR-010**: ProfileAdmin MUST show user creation date (when account was created)
- **FR-011**: BulletinAdmin MUST display writer bulletins with article count and subscriber count
- **FR-012**: BulletinAdmin MUST link to writer profile (reverse link to ProfileAdmin)
- **FR-013**: Both admins MUST restrict access to admin-only users (is_staff or is_superuser check)

### Key Entities

- **Profile**: User model extension with role information
- **Bulletin**: Writer's publishing space with article and subscriber relationships
- **Article**: Content authored by writers (counted in writer metrics)
- **Comment**: User engagement (counted in received metrics)
- **Like**: User engagement (counted in received metrics)
- **Subscription**: Reader's relationship to bulletin (counted in subscription metrics)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admin can view all users in admin interface within 2 seconds
- **SC-002**: Admin can filter by role and see results within 1 second
- **SC-003**: Admin can change user role and see new permissions take effect immediately
- **SC-004**: Inactive users cannot log in (0% successful logins for is_active=False)
- **SC-005**: Engagement metrics are accurate within 1 request (no stale data)
- **SC-006**: Admin can search for users by username and find results within 1 second
- **SC-007**: All profile fields display correctly (no truncation or missing data)
- **SC-008**: Bulk actions work if implemented (select multiple users, perform action on all)
- **SC-009**: Only admin users can access user admin interface (non-admins see 403)
- **SC-010**: User data is preserved when deactivated (no data loss)

---

## Assumptions

- Django's built-in admin interface is used for user management (no separate admin dashboard)
- Admin users have superuser or staff status with appropriate permissions
- Engagement metrics are computed from related models (articles, comments, likes, subscriptions)
- Last login date is tracked by Django's default User model
- Bulk actions use Django admin's standard action framework (if implemented)
- User deactivation sets is_active=False (soft delete, not hard delete)
- Metrics can be displayed as simple counts (not real-time analytics)
- Performance targets assume development environment

---

**Version**: 1.0.0 | **Status**: Ready for Planning
