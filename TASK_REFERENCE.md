# Quick Task Reference Guide

**Use this for daily task selection based on your energy level**

---

## 🟢 Low Energy Tasks (1-2 hours)

### Frontend
- [ ] Add CSS variables for colors
- [ ] Create button components
- [ ] Design badges/tags
- [ ] Add loading spinners
- [ ] Create footer
- [ ] Add social media icons
- [ ] Typography improvements
- [ ] Hover effects
- [ ] Fix spacing/alignment
- [ ] Add favicon

### Backend
- [ ] Write simple tests
- [ ] Add docstrings
- [ ] Update README
- [ ] Fix linting errors
- [ ] Add validation messages
- [ ] Create simple management command

### DevOps
- [ ] Update requirements.txt
- [ ] Add environment variable documentation
- [ ] Create .env.example
- [ ] Update CHANGELOG

---

## 🟡 Medium Energy Tasks (3-5 hours)

### Frontend
- [ ] Redesign homepage hero
- [ ] Create article cards grid
- [ ] Navbar with dropdown
- [ ] Profile page layout
- [ ] Form styling improvements
- [ ] Mobile menu
- [ ] Dashboard layout
- [ ] Add animations/transitions

### Backend
- [ ] Create API serializers
- [ ] Add database indexes
- [ ] Implement caching for views
- [ ] Create search endpoint
- [ ] Add file upload handling
- [ ] Email template creation
- [ ] Add rate limiting
- [ ] Optimize database queries

### DevOps
- [ ] Configure CI/CD pipeline
- [ ] Add security headers
- [ ] Setup monitoring
- [ ] Create backup scripts

---

## 🔴 High Energy Tasks (5-8 hours)

### Frontend
- [ ] Complete article detail page redesign
- [ ] Build analytics dashboard with charts
- [ ] Full mobile responsiveness
- [ ] Interactive comment system
- [ ] Real-time notifications UI

### Backend
- [ ] Configure Celery
- [ ] Implement full-text search
- [ ] Build notification system
- [ ] OAuth2 authentication
- [ ] Analytics data models
- [ ] WebSocket notifications
- [ ] Complex API viewsets with permissions

### DevOps
- [ ] Hetzner + Coolify deployment
- [ ] Database migration strategy
- [ ] Load testing with locust
- [ ] Performance optimization

---

## Daily Planning Template

```markdown
## [Date] - Energy Level: ___/10

### Morning (High Energy)
- [ ] 1x 🔴 Hard Task: ___________________

### Afternoon (Medium Energy)
- [ ] 1x 🟡 Medium Task: ___________________

### Evening (Low Energy)
- [ ] 2x 🟢 Easy Tasks: ___________________

### Notes
- Learned: ___________________
- Blocked by: ___________________
- Tomorrow priority: ___________________
```

---

## Task Dependencies

**Must Do First (Part 1)**:
1. Fix requirements.txt encoding
2. Fix CI/CD Python versions
3. Install DRF
4. Create serializers
5. Create API views
6. Configure API URLs

**Frontend Prerequisites**:
- Design system (colors, typography) → All other frontend tasks

**Backend Prerequisites**:
- API layer complete → Celery tasks, notifications
- Tag models → Search implementation
- Notification models → Email tasks

---

## Time-Boxed Tasks

**30 Minutes**:
- Fix one bug
- Add one test
- Update documentation
- Code formatting

**1 Hour**:
- Create CSS component
- Write API endpoint test
- Add form validation
- Update template

**2 Hours**:
- Design homepage section
- Create serializer + tests
- Add caching to view
- Mobile responsive fix

**Half Day (4 hours)**:
- Complete article page redesign
- Build search functionality
- Configure Celery
- Create analytics models

---

## Priority Matrix

| Urgent | Important | Task Type |
|--------|-----------|-----------|
| ✅ | ✅ | **DO NOW**: Critical bugs, blocking issues |
| ✅ | ❌ | **SCHEDULE**: Quick wins, easy tasks |
| ❌ | ✅ | **PLAN**: Core features, long-term value |
| ❌ | ❌ | **SKIP**: Nice-to-have, optional |

**Part 1 (Week 1)**: Everything is urgent + important
**Part 2 & 3**: Follow energy level, not urgency

---

## Switching Between Frontend/Backend

**Stuck on backend?** → Switch to frontend
- Style existing pages
- Add CSS improvements
- Work on layout

**Tired from frontend?** → Switch to backend
- Write tests
- Add API endpoint
- Database optimization

**Brain fried?** → Do easy tasks
- Update docs
- Fix CSS spacing
- Add comments
- Organize imports

---

## Weekly Goals Template

```markdown
## Week of [Date]

### Must Complete (MVP)
- [ ] ___________________
- [ ] ___________________

### Should Complete
- [ ] ___________________
- [ ] ___________________

### Nice to Have
- [ ] ___________________

### Learning Goals
- [ ] ___________________

### Deployment Plan
- [ ] Test all features locally
- [ ] Run full test suite
- [ ] Deploy to Hetzner
- [ ] Verify production works
```

---

## Motivation Tracker

**Completed This Week**:
- ✅ ___________________
- ✅ ___________________
- ✅ ___________________

**What I Learned**:
- 💡 ___________________
- 💡 ___________________

**Portfolio Screenshots**:
- 📸 ___________________
- 📸 ___________________

---

## Emergency Break Glass

**Feeling overwhelmed?**
1. Do one 🟢 easy task
2. Commit the change
3. Take a 15-minute break
4. Celebrate the win
5. Repeat

**Can't focus?**
- Work on CSS (visual feedback is motivating)
- Write documentation (productive, low stress)
- Organize code (satisfying cleanup)

**Impostor syndrome?**
- Review what you've built (check git log)
- Read your completed tasks
- Remember: employers want to see growth, not perfection

---

## Daily Momentum

**Morning Routine**:
1. Review yesterday's work (git log -3)
2. Choose today's tasks (based on energy)
3. Set timer (Pomodoro)
4. Start with easiest task (build momentum)

**Evening Routine**:
1. Commit all changes
2. Update task list
3. Plan tomorrow
4. Take screenshot if UI work done

---

## Productivity Hacks

**For Backend Work**:
- Use Django shell to test code snippets
- Keep docs open (DRF, Celery)
- Test in Postman as you build
- Write tests first (TDD)

**For Frontend Work**:
- Keep browser DevTools open
- Use Tailwind playground
- Test responsive in browser
- Take before/after screenshots

**For Both**:
- One feature branch at a time
- Commit every 30-60 minutes
- Push to GitHub daily (backup)
- Ask AI when stuck (don't waste 2 hours)

---

## Red Flags (Time to Take Break)

- [ ] Staring at screen for 10+ min without progress
- [ ] Same error for >30 min
- [ ] Feeling frustrated/angry
- [ ] Can't focus for even 5 minutes
- [ ] Making silly mistakes

**Break Activities**:
- Walk (best)
- Coffee/tea
- Stretch
- Quick game
- Different task type
