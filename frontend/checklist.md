# GullyGuru Fantasy Cricket – UI-Based Replication Task Checklist

Below is a comprehensive set of UI categories and their corresponding tasks needed to replicate the Telegram-based GullyGuru functionality in a web-based application. The tech stack includes:

- **Next.js** (React framework)
- **TypeScript**
- **shadcn/ui** for component styling
- **Google Sign-In** for authentication
- **Dashboard components** for admin and user panels

Each category includes 20–30 tasks, subdivided into smaller steps, to guide the end-to-end development process. Use these checklists as you build each portion of the UI.

---

## 1. **User Onboarding & Authentication**

1. [ ] **Landing Page & Google Sign-In**
   - [ ] Add a “Sign in with Google” button using the official Google OAuth client.
   - [ ] Configure client-side OAuth flows and handle redirect URIs in Next.js.
   - [ ] Store user session tokens securely (HTTP-only cookies or secure local storage).
2. [ ] **Account Creation & Registration Flow**
   - [ ] After OAuth success, request additional user details (e.g., desired username).
   - [ ] Save user info to the backend via an API endpoint.
   - [ ] Redirect to the “Select or Create Gully” screen after successful registration.
3. [ ] **Profile Setup UI**
   - [ ] Display a form to let the user confirm/edit name, email, and optional avatar.
   - [ ] Ensure data validation (e.g., unique username, required fields).
   - [ ] Provide an option to skip or go back.
4. [ ] **Team Name Entry**
   - [ ] Present a prompt for “Team Name” the first time the user logs in.
   - [ ] Validate uniqueness to avoid name collisions within the Gully.
   - [ ] Provide real-time feedback if a team name is already taken.
5. [ ] **Responsive Design**
   - [ ] Ensure the onboarding flow is responsive across mobile, tablet, and desktop.
   - [ ] Use a consistent style from shadcn/ui components.
6. [ ] **Error Handling & Alerts**
   - [ ] Show inline error messages if the Google Sign-In fails.
   - [ ] Gracefully handle 400/401/500 errors from the backend.
   - [ ] Provide “Retry” or “Report Issue” options when applicable.
7. [ ] **Logout & Session Expiry**
   - [ ] Provide a logout button in the header or user menu.
   - [ ] On logout, revoke the session token and redirect to the landing page.
   - [ ] Handle session timeouts (e.g., token expiry) by prompting re-login.

---

## 2. **Gully (League) Management**

1. [ ] **Gully Dashboard Page**
   - [ ] List all gullies the user is part of (or can join if open).
   - [ ] Show Gully name, status (draft, auction, transfers, completed), and basic stats.
   - [ ] Provide “Create Gully” action (for users who can create new leagues).
2. [ ] **Create New Gully UI**
   - [ ] Modal or dedicated page for entering Gully name and optional description.
   - [ ] Validate uniqueness of Gully name if required by backend.
   - [ ] Capture Telegram group ID or skip if purely web-based (depending on design).
3. [ ] **Gully Details & Settings**
   - [ ] Page to view Gully info: name, status, participants, etc.
   - [ ] Display admin controls if the user is the Gully admin (e.g., change status).
   - [ ] Provide inline editing for Gully name or description (admin only).
4. [ ] **Invite & Join Gully Flow**
   - [ ] Generate shareable link or code for others to join.
   - [ ] When a new user clicks the invite link, show “Join Gully” confirmation.
   - [ ] On success, redirect them to the Gully Dashboard with their new membership.
5. [ ] **Gully Navigation**
   - [ ] A top-level nav or side menu listing the user’s gullies.
   - [ ] Clicking a Gully name navigates to its detail / scoreboard page.
   - [ ] Clear highlight of the currently active Gully context.
6. [ ] **Status Management**
   - [ ] Show a prominent label for the Gully’s current status (draft, auction, transfers, completed).
   - [ ] If user is an admin, add a button or dropdown to change the status.
   - [ ] Confirmations for status changes (e.g., “Move from DRAFT to AUCTION?”).
7. [ ] **Responsive Layout**
   - [ ] Gully list collapses into a dropdown on mobile.
   - [ ] Keep consistent spacing and typography from shadcn/ui.
8. [ ] **Edge Cases & Error Handling**
   - [ ] If a Gully is locked or completed, block certain edits.
   - [ ] Show user-friendly messages if Gully not found or user lacks permission.

---

## 3. **Admin Panel**

1. [ ] **Admin Dashboard**
   - [ ] Display a high-level overview (user count, number of gullies, etc.).
   - [ ] Provide quick links to manage gullies, users, and auctions.
   - [ ] Restrict access to users with “admin” role—redirect others to a 403 page.
2. [ ] **User Management**
   - [ ] List all users, with search by username/ID.
   - [ ] Actions: view details, reset password (if implementing), or change role (admin/member).
   - [ ] Confirmation dialogs for destructive actions (e.g., user deletion).
3. [ ] **Gully Management**
   - [ ] Provide an admin-only list of all gullies.
   - [ ] Ability to forcibly change status or rename a Gully.
   - [ ] Add or remove participants as an override (e.g., “Add Admin” function).
4. [ ] **Auction Controls**
   - [ ] Admin view of ongoing auctions: participants, highest bids, time left, etc.
   - [ ] Option to pause or restart an auction if needed.
   - [ ] Access logs for resolved or cancelled auctions.
5. [ ] **Monitoring & Logging**
   - [ ] Summaries of key events (e.g., user joins, auctions start/stop).
   - [ ] Real-time logs or at least a refresh button to poll the backend.
   - [ ] Filters by date, user, or Gully ID.
6. [ ] **Permissions & Roles UI**
   - [ ] Clear UI to promote or demote users as Gully admin or global admin.
   - [ ] Indicate current roles on a user’s profile page.
   - [ ] Show distinct warnings if attempting to remove the last admin from a Gully.
7. [ ] **Styling & UX**
   - [ ] Use a consistent admin layout with side navigation for each management section.
   - [ ] Keep data tables clean and scannable (paging, sorting, filtering).
   - [ ] Avoid clutter: Show only relevant actions per user’s role.

---

## 4. **Squad Creation & Management**

1. [ ] **Squad Dashboard**
   - [ ] Display user’s current squad with role filters (BAT, BOWL, ALL, WK).
   - [ ] Show how many players have been selected vs. total allowed (e.g., 3/18).
   - [ ] Provide “Edit Squad” or “Add/Remove Players” button.
2. [ ] **Player Selection Modal/Page**
   - [ ] List all available players in a scrollable container with pagination.
   - [ ] Filters: Team, Player Role, Price Range.
   - [ ] On selection, highlight the player and update the count (e.g., “You have selected 10 so far”).
3. [ ] **Budget & Credits**
   - [ ] Show current budget left vs. total credits (e.g., 100.0 credits).
   - [ ] When selecting a player, deduct their base price from the displayed budget.
   - [ ] Prevent selection if budget is not sufficient.
4. [ ] **Bulk Submit Mechanism**
   - [ ] Display a [Submit Squad] button that finalizes selections in bulk.
   - [ ] Confirm final selection in a summary popup (player list + total cost).
   - [ ] On submit, call the API to store the final squad for that user.
5. [ ] **Squad Editing**
   - [ ] If a user already has a partial squad, show it as “checked” or “selected” by default.
   - [ ] Toggling a selection removes or adds players from the squad in real time.
   - [ ] Provide error messages if removing too many or going over the limit.
6. [ ] **Visual Feedback**
   - [ ] Show each player with price, role, team, and a toggle icon.
   - [ ] Use color coding or icons (e.g., check mark for selected).
   - [ ] Show real-time budget updates as the user toggles players.
7. [ ] **Validation & Edge Cases**
   - [ ] Enforce minimum squad size (e.g., 15) upon submission.
   - [ ] Warn if the user tries to leave the page with unsaved changes.
   - [ ] Handle concurrency if the same player is contested (during Auction).

---

## 5. **Auction Interface**

1. [ ] **Auction Lobby / Waiting Screen**
   - [ ] Display next player to be auctioned (photo, stats, base price).
   - [ ] Timer for how long the user can place bids (countdown).
   - [ ] Indicate if the user has enough budget to bid.
2. [ ] **Bid Placement UI**
   - [ ] Provide a “Bid” button or incremental bid slider.
   - [ ] Show current highest bid and bidder.
   - [ ] If user attempts to bid beyond their budget, show an error.
3. [ ] **Skip Mechanism**
   - [ ] If a user has no interest, they can “Skip.”
   - [ ] Internally track skip counts—if all skip, the system moves to the next player automatically.
   - [ ] No need for skip confirmations in the public feed, but show a silent skip indicator for the user.
4. [ ] **Real-Time Updates**
   - [ ] Implement WebSocket or server-sent events to push new highest bid info to all participants immediately.
   - [ ] Display “@username bid X credits” or an equivalent real-time message.
   - [ ] Auction closes if no new bids after X seconds, awarding the player.
5. [ ] **Auction End Announcement**
   - [ ] Show a final screen or toast: “Player sold to @username for 2.5 credits!”
   - [ ] Update that user’s squad and budget in real time.
   - [ ] Immediately move on to the next available player or show an “Auction Completed” state if none remain.
6. [ ] **Admin Overrides**
   - [ ] If the user is an admin, allow them to pause or cancel an auction in progress.
   - [ ] Provide a reason prompt if canceling an auction.
   - [ ] Show a confirmation dialog for destructive actions to avoid accidental disruptions.
7. [ ] **Accessibility & Mobile Readiness**
   - [ ] Ensure the bid button and countdown are easily visible on smaller screens.
   - [ ] Keep chat/stream of bids scannable, possibly in a collapsible panel.
   - [ ] Provide fallback if WebSocket is not supported (periodic polling).

---

## 6. **Transfer Window & Weekly Updates**

1. [ ] **Transfer Market Overview**
   - [ ] Show players available for transfer with “fair price” or last sold price.
   - [ ] Provide filters (batters, bowlers, etc.) and searching by player name.
2. [ ] **Initiate Transfer**
   - [ ] Show a “Release Player” button if the user wants to free a squad slot.
   - [ ] Confirm the release, and add that player to the Transfer Market with a price suggestion.
   - [ ] Deduct or credit the user’s budget accordingly based on the app’s rules.
3. [ ] **Buy Player from Transfer Market**
   - [ ] Let user see player details, stats, and a “Buy” button.
   - [ ] If multiple users want the same player, move that player to a mini-auction flow.
   - [ ] Show updated budget and squad size if the purchase is successful.
4. [ ] **Weekly Transfer Limits**
   - [ ] Indicate how many transfers remain for the user this week.
   - [ ] Disable buy/release buttons if the user hits the weekly limit.
   - [ ] Provide an alert if the user tries to exceed the limit.
5. [ ] **Time-Sensitive UI**
   - [ ] Display the countdown for how long the weekly transfer window is open.
   - [ ] Gracefully disable “Release” or “Buy” once the window closes.
   - [ ] Show a banner “Transfers are currently closed!” if out of the transfer window.
6. [ ] **Notifications**
   - [ ] Show a success or error toast after each purchase or release.
   - [ ] Provide real-time group notifications or activity feed updates (like an “events” panel).
   - [ ] Summarize changes each user made when the window closes.
7. [ ] **Edge Cases**
   - [ ] If a user’s budget is insufficient, show a clear message.
   - [ ] Handle concurrency if multiple users attempt to buy the same player at the same time.
   - [ ] Confirm “undo” or “cancel” is not allowed once the transfer is final, if that is the rule.

---

## 7. **Live Scoring & Leaderboards**

1. [ ] **Live Scoreboard UI**
   - [ ] Display each participant’s total points and rank in real time.
   - [ ] Optionally, show top 3 or top 5 participants as highlight cards.
   - [ ] Provide quick filters (e.g., show only my friends, top 10, or entire Gully).
2. [ ] **Player Performance Popups**
   - [ ] When a user clicks a participant’s name, show their squad’s performance breakdown.
   - [ ] Display each player’s contribution to points (runs, wickets, bonus, etc.).
   - [ ] Update stats in real time (using either polling or server-sent events).
3. [ ] **Match & Team Filters**
   - [ ] If real-time match data is integrated, let users filter by current matches (e.g., “View only players in active match”).
   - [ ] Provide at-a-glance performance of the user’s squad for the day.
4. [ ] **Points Breakdown**
   - [ ] Show a detailed breakdown of how points are calculated: runs, wickets, boundaries, economy rate, etc.
   - [ ] Summation of points for each player to confirm total is correct.
   - [ ] Potential captain/vice-captain multipliers (2x or 1.5x).
5. [ ] **Pagination & Performance**
   - [ ] If the Gully has many participants, use a paginated leaderboard.
   - [ ] Optimize queries to avoid huge data loads.
   - [ ] Keep the UI responsive during rapid updates.
6. [ ] **Visual Indicators**
   - [ ] Use color-coded badges or icons to indicate players performing well, or failing.
   - [ ] Animate rank changes (e.g., “+2 positions” or “-1 position”).
   - [ ] Show “Live” label if a match is ongoing for a player.
7. [ ] **Caching & Offline**
   - [ ] Possibly cache partial data so the scoreboard can still show recent info if offline momentarily.
   - [ ] Show a small “disconnected” banner if live updates are lost, and revert to manual reload.

---

## 8. **Notifications & Activity Feed**

1. [ ] **In-App Notification Panel**
   - [ ] Display real-time updates for new auctions, transfers, or admin announcements.
   - [ ] Condense them in a popover or a dedicated “Notifications” page.
   - [ ] Mark notifications as read/unread so users can keep track.
2. [ ] **System Alerts**
   - [ ] Show ephemeral toasts for success (e.g., “Auction won”), errors, or warnings.
   - [ ] Ensure each toast is consistent in style, location, and duration.
3. [ ] **Push Notifications (Optional)**
   - [ ] If implementing push notifications, prompt the user for browser permission.
   - [ ] Send relevant alerts (auction ending soon, match about to start, etc.).
   - [ ] Provide a user settings panel to toggle or customize which notifications are received.
4. [ ] **Activity Feed**
   - [ ] Centralized feed of important events: who joined the Gully, who bought which player, etc.
   - [ ] Keep it chronological, with filters for event type.
   - [ ] Integrate infinite scroll or pagination for older events.
5. [ ] **Messaging or Chat Integration (Optional)**
   - [ ] If you want to replicate Telegram-like group chat, embed a chat system.
   - [ ] Display user avatars and messages in real time.
   - [ ] Provide minimal moderation tools for the Gully admin (mute, ban, pinned messages).
6. [ ] **Admin Broadcast**
   - [ ] Admins can send announcements to the entire Gully.
   - [ ] Display pinned announcements at the top of the feed or scoreboard page.
   - [ ] Option to schedule announcements for certain times.

---

## 9. **General UI/UX & Infrastructure**

1. [ ] **UI Components & Design System**
   - [ ] Use shadcn/ui for a cohesive style.
   - [ ] Create a library of reusable components: buttons, modals, alerts, etc.
   - [ ] Maintain a global theme (colors, typography, spacing).
2. [ ] **Routing & Navigation**
   - [ ] Set up Next.js pages for each major feature (Onboarding, Gully List, Auction, etc.).
   - [ ] Use dynamic routes (e.g., `/gully/[gullyId]`) to handle specific Gully pages.
   - [ ] Implement private routes and redirect unauthorized users to login.
3. [ ] **API Integration**
   - [ ] Use fetch or a library like axios to call your FastAPI endpoints (or whichever backend).
   - [ ] Provide reusable hooks/services for interacting with each domain (auction, squad, user).
   - [ ] Implement error boundary components for graceful fallback on critical errors.
4. [ ] **State Management**
   - [ ] Decide on a global store (e.g., Redux, Zustand, or React Query + Context).
   - [ ] Keep consistent patterns to store user session, Gully data, and live updates.
   - [ ] Minimize duplication between local state and server data.
5. [ ] **Performance & Caching**
   - [ ] Use SWR or React Query for data fetching and caching if polling is used frequently.
   - [ ] Optimize images and use Next.js image component where needed.
   - [ ] Pre-render or server-side render (SSR) critical pages for SEO/performance.
6. [ ] **Security & Roles**
   - [ ] Protect all admin routes behind role-based checks.
   - [ ] Implement CSRF protection if needed (depending on your auth approach).
   - [ ] Validate all user actions from the client with server checks (like budget constraints).
7. [ ] **Error & Logging**
   - [ ] Provide meaningful UI error states (404 gully not found, 500 server error, etc.).
   - [ ] Log user’s important actions in a server log or analytics system.
   - [ ] Catch any unhandled rejections or exceptions and show a fallback UI.

---

## 10. **Testing & Deployment**

1. [ ] **Unit Tests for Components**
   - [ ] Write tests for each UI component (e.g., auction timer, player selection).
   - [ ] Check interaction states (hover, click, disabled).
   - [ ] Use React Testing Library or Cypress for front-end tests.
2. [ ] **Integration Tests**
   - [ ] Combine front-end components with mock backend responses.
   - [ ] Test flows like “User creates squad → Submits → Verifies scoreboard.”
   - [ ] Ensure role-based restrictions are enforced (non-admin can’t see admin panel).
3. [ ] **Cross-Browser & Responsiveness**
   - [ ] Test in Chrome, Firefox, Safari, Edge.
   - [ ] Check mobile layouts on iOS and Android.
   - [ ] Fix any layout shifts or scroll issues in small screens.
4. [ ] **Performance Audits**
   - [ ] Run Lighthouse or similar tools for performance scores.
   - [ ] Identify bottlenecks or large bundle sizes and optimize.
5. [ ] **Staging & Production**
   - [ ] Set up environment variables for dev, staging, and production (API URLs, secrets).
   - [ ] Use Next.js “preview” or staging domain for final QA.
   - [ ] Deploy to your chosen hosting (Vercel, AWS, GCP) with CI/CD pipelines.
6. [ ] **Monitoring & Logging**
   - [ ] Integrate an error tracking tool (Sentry or similar).
   - [ ] Collect usage data to refine UX (Google Analytics or similar).
   - [ ] Watch logs for 500 errors or performance anomalies.

---

## 11. **Post-Launch & Ongoing Improvements**

1. [ ] **User Feedback Loop**
   - [ ] Provide a feedback form or an NPS prompt after key actions.
   - [ ] Collect user suggestions on confusion points or missing features.
2. [ ] **Feature Flags & A/B Testing**
   - [ ] Gradually roll out new features (e.g., new auction style) to a subset of users.
   - [ ] Compare performance or user satisfaction data between versions.
3. [ ] **Localization & Internationalization**
   - [ ] If needed, prepare to translate UI text for multiple languages.
   - [ ] Use Next.js i18n or similar library for multi-language support.
4. [ ] **Scalability & Optimization**
   - [ ] Evaluate usage patterns and scale the backend accordingly.
   - [ ] Introduce caching layers or message queues for heavy real-time tasks (like auctions).
5. [ ] **Additional Gamification**
   - [ ] Add trophies, badges, or seasonal achievements to increase engagement.
   - [ ] Expand the scoreboard with match predictions, polls, or advanced stats.
6. [ ] **Periodic Cleanup & Maintenance**
   - [ ] Archive completed gullies to reduce clutter in the database.
   - [ ] Remove or anonymize old user data to maintain GDPR or similar compliance.
   - [ ] Keep dependencies updated and address any security advisories promptly.

---

## Summary

By systematically completing the tasks in each category above, you can recreate and enhance the GullyGuru fantasy cricket experience on a Next.js web platform. The checklists encompass everything from initial user onboarding and Gully creation, to real-time auctions, live scoreboards, and robust admin panels.

1. **User Onboarding & Authentication**
2. **Gully Management**
3. **Admin Panel**
4. **Squad Creation & Management**
5. **Auction Interface**
6. **Transfer Window & Weekly Updates**
7. **Live Scoring & Leaderboards**
8. **Notifications & Activity Feed**
9. **General UI/UX & Infrastructure**
10. **Testing & Deployment**
11. **Post-Launch & Ongoing Improvements**
