# Implementation Notes

# Blog Platform

A modern Django-based platform enabling writers to publish articles and readers to engage with content through subscriptions, likes, and comments.

# ![Blog Platform Homepage](media/screenshots/homepage.png)

## 📋 Overview

Blog Platform is a full-featured content management system built with Django 5.2 that creates a community around written content. The platform supports multiple user roles, content visibility controls, and rich engagement features.

### Key Features

- **Bulletin System**: Writers can create personal bulletins to publish and organize their articles
- **Subscription Model**: Readers can subscribe to writers to access premium content
- **Rich Content Editing**: Integrated CKEditor for writing beautiful articles
- **Engagement Tools**: Comment, like, and save articles for later reading
- **Content Moderation**: Administrative tools for content verification
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## 🧑‍💻 User Roles & Permissions

The platform implements a three-tier permission system:

### Reader Role
- **Default role** for new registered users
- Can view all public articles
- Can subscribe to writers to access private content
- Can like articles and save them for later reading
- Can comment on accessible articles
- Can upgrade to writer role

### Writer Role
- Can create and manage a personal bulletin
- Can publish articles with public or private visibility
- Can manage article status (draft/published)
- Retains all reader capabilities
- Can access the Writer Dashboard to manage content

### Administrator Role
- Can review and moderate all content
- Can verify articles with an approval badge
- Can reject inappropriate content
- Has access to the Admin Dashboard
- Can view all content regardless of visibility settings

## 📱 Site Navigation

### Public Pages
- **Home** (`/`): Featured articles, popular bulletins, and notable writers
- **About** (`/about/`): Platform information
- **Q&A** (`/qa/`): Frequently asked questions

### Authentication
- **Sign Up** (`/accounts/signup/`): New user registration
- **Login** (`/accounts/login/`): User authentication
- **Logout** (`/accounts/logout/`): Session termination

### User Management
- **Profile** (`/accounts/profile/<username>/`): User information and activity
- **Profile Update** (`/accounts/profile/update/<username>/`): Edit user details
- **Activity View** (`/accounts/profile/<username>/activity/`): User interactions history

### Content Management
- **Articles List** (`/articles/`): Browse all public articles
- **Article Detail** (`/article/<id>/`): View a specific article
- **Article Create** (`/article/create/`): Create a new article (writers only)
- **Article Edit** (`/article/edit/<id>/`): Modify an article (owner only)
- **Article Delete** (`/article/delete/<id>/`): Remove an article (owner only)

### Bulletin Management
- **Bulletin Detail** (`/bulletin/<slug>/`): View a bulletin and its articles
- **Bulletin Create** (`/bulletin/create/`): Create a new bulletin (writers only)
- **Bulletin Edit** (`/bulletin/<slug>/edit/`): Modify a bulletin (owner only)
- **Bulletin Dashboard** (`/bulletin/<slug>/dashboard/`): Manage bulletin content (owner only)

### Engagement
- **Toggle Like** (`/like/<id>/`): Like or unlike an article
- **Toggle Read Later** (`/read-later/<id>/`): Save or unsave an article
- **Toggle Subscription** (`/subscribe/<slug>/`): Subscribe or unsubscribe to a bulletin

### Administration
- **Evaluation Dashboard** (`/evaluate/dashboard/`): Manage content moderation (admins only)
- **Article Evaluation** (`/evaluate/decision/<id>/`): Review specific articles (admins only)

## 🗄️ Content Structure

### User Profile
- **Bio & Avatar**: Personal information and image
- **Role Indicator**: Shows user permission level
- **Activity Feed**: Record of interactions and contributions
- **Subscription List**: Bulletins the user follows

![Profile Page](media/screenshots/profile.png)

### Bulletin
A bulletin is a writer's personal publication space:
- **Title & Description**: Identifies the bulletin's focus
- **Article Collection**: All content published by the writer
- **Subscription Count**: Number of followers
- **Dashboard**: Content management interface (for owners)

![Bulletin Page](media/screenshots/bulletin.png)

### Article
Articles are the primary content units:
- **Status**: Draft or Published
- **Visibility**: Public (visible to all) or Private (subscribers only)
- **Evaluation**: Content moderation state (Pending, Under Review, Approved, Rejected)
- **Rich Content**: Text editor with formatting options
- **Engagement**: Comment section, like button, read-later option

![Article Page](media/screenshots/article.png)

## 🔐 Authentication & Authorization

### Registration Process
1. Users sign up with username, email, and password
2. Accounts are created with default "reader" permissions
3. Users can later upgrade to "writer" role from their profile

### Role Promotion
- Readers can promote themselves to writers via their profile page
- Administrator role requires special permission

### Permission Enforcement
The platform enforces permissions across all views:
- Content visibility based on subscription status
- Write access limited to appropriate roles
- Administrative features restricted to admin users

## 💬 Engagement Features

### Comments
- Comment on articles you can access
- Author can see all comments on their content
- Comments are displayed chronologically

### Likes
- Express appreciation for articles
- Liked articles appear in your profile activity
- Like counts visible to article authors

### Read Later
- Bookmark articles to read in the future
- Access your reading list from your profile
- Easy management of saved content

## 🛠️ Technical Stack

- **Backend**: Django 5.2
- **Database**: SQLite (development)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Rich Text**: CKEditor integration
- **Forms**: Django Crispy Forms with Tailwind

