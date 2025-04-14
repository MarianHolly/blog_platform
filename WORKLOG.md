## Diary of Progress

### 2025-04-07

#### ✅ What I Have Done
- Wrote initial project documentation (clearer descriptions, better development).
- Created django project `blog_platform`.
- Created django app `content` with `home` and `about` templates, views, and URL configurations.

#### 🔜 What To Do Next
- Decide on frontend styling – can I integrate Tailwind CSS?
- Finish designing the database schema.
- Create an ER diagram to visualize model relationships.
- Define ORM models and check foreign key relations.
- Run initial migrations (`makemigrations` & `migrate`).
- Create a superuser and populate mock content.

### 2025-04-08

#### ✅ What I Have Done
- Created models on Article, Category and run migrations.
- Created superuser and wrote mock categories and articles.
- List articles on homepage and create detail page for single article.

#### 🔜 What To Do Next
- Resources to read on authentication and users management:
  - https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
- Create and develop custom model on user, profile and bulletin.

### 2025-04-11 / 2025-04-13

#### ✅ What I Have Done
- Planning blog platform structure and functionality.
- Drafting models and their relationships.
- Thinking through project.

### 2025-04-13
- 



- I was trying to upload image, but it didnt function, until i added to form this: `enctype="multipart/form-data"`