# Implementation Notes

### Primary Features Blog Plaform

- [x] Model for Profile based on User
- [x] Basic authentication views and urls (login, signup)
- [x] Models for Bulletin, Article, Subscription
- [x] Check relationships between models
- [x] Simple list and detail view for Articles
- [x] ArticleForm with CreateView, UpdateView, and DeleteView

- [x] ProfileDetailView 
- [ ] ProfileForm with create, update, delete
- [x] BulletinDetailView
- [ ] BulletinForm with create, update, delete
- [ ] Subscription functionality (view and manage)
  - [ ] Update article visibility logic based on subscriptions
  - [ ] Add subscription management to profile view

- [ ] Profile model with role field and role-checking methods
- [ ] Permission mixins (Writer, ArticleOwner)
- [ ] Update views to control access based on user role
- [ ] Update templates to show/hide UI elements based on permissions
- [ ] Promote to writer functionality

### Secondary Features

- [ ] Models for Comment, Like, ReadLater
- [ ] Like - mark article, profile list (manage and view)
- [ ] ReadLater - ...
- [ ] CommentForm and handling submission
- [ ] ArticleDetail includes comment form and list
- [ ] ProfileDetail includes profile activities

- [ ] Writer's dashboard to manage state of articles
- [ ] Writer's statistics section (subscribers, likes, comments)
- [ ] Search functionality for articles and bulletins on Homepage
- [ ] Pagination for article lists
- [ ] Filtering articles 
  - [ ] Homepage displays most popular articles
  - [ ] Homepage represents new articles based on Category (new model - admin management)
  - [ ] Writer's Bulletin can filter articles based on Tags (new model - writer management)

- [ ] Responsive Design for Mobile Users
- [ ] Dark Mode Support




## Implementation Plan based on URLs

- home/
- about/
- singin/
- login/
- logout/

**User Urls**
- accounts/
  - profile/<slug:username>
  - profile/edit 
- bulletin/<slug:bulletin-name>
  - bulletin/edit

**Article Urls**
- articles-list
- article-detail
  - article-create / edit
  - article-delete

**Article Urls** with relationships
- <slug:bulletin> ArticlesList
- <slug:bulletin>/<slug:article> ArticleDetail
    - ArticleForm 
    - /create - ArticleCreateView
    - /update - ArticleUpdateView
    - /delete - (Confirm Delete Form)

