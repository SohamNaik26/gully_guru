# onboarding.md

## Overview
This document details the **onboarding process** for your fantasy cricket platform. It includes **automatic Gully creation**, a **single-admin** approach, and a streamlined **user registration** flow. In this updated version:
- The **admin** can also **participate** in the game as a normal player.
- The admin tools are minimal, focusing on *managing the Gully* and *viewing participants*.
- All other users can register in a private chat to create their teams and play.

---

## Table of Contents
1. [Introduction & Goals](#introduction--goals)  
2. [Automatic Gully Creation](#automatic-gully-creation)  
3. [Single Admin Model](#single-admin-model)  
4. [Group Announcement & Deep Link](#group-announcement--deep-link)  
5. [Player (and Admin) Registration Flow](#player-and-admin-registration-flow)  
   - [Team Name Setup](#team-name-setup)  
   - [Inline Keyboards & Cancellation](#inline-keyboards--cancellation)  
6. [Admin Tools](#admin-tools)  
7. [Data Sync & Edge Cases](#data-sync--edge-cases)  
8. [Example Conversations](#example-conversations)  
9. [Conclusion](#conclusion)
10. [Implementation Status](#implementation-status)

---

## 1. Introduction & Goals
- **Objective**: Provide a **seamless** onboarding sequence where:
  1. The **Telegram group** is automatically recognized as a new Gully when the bot is added.
  2. The **group admin** (who adds the bot) is designated as Gully admin **but can also** play.
  3. **All group members** (including the admin) register in private chat, set a team name, and participate as managers.
  4. Utilize **inline keyboards** for user interactions, reducing slash commands.

---

## 2. Automatic Gully Creation
1. **Bot Added to Group**  
   - When the bot is added to a Telegram group, it automatically:
     - Retrieves the group's title (e.g., "IPL Fans United").
     - Calls an API method: `create_gully(name=<GroupTitle>, telegram_group_id=<group_id>)`.

2. **Gully Record**  
   - The new Gully is stored in the database with:
     - `name = <GroupTitle>`
     - `telegram_group_id = <group_id>`
   - No explicit user prompt for "Create Gully" is needed; it happens in the background.

---

## 3. Single Admin Model
1. **Admin Assignment**  
   - The user who invited the bot is marked as the **Gully admin**.  
   - This admin can still perform **all** standard player actions (submit squads, bid in auctions, etc.), plus some additional admin features.

2. **No Additional Admins**  
   - By default, there is **only one** admin. If you wish to allow admin transfer, that can be a separate process, but multiple simultaneous admins are not supported.

---

## 4. Group Announcement & Deep Link
After creation, the bot posts a **welcome message** in the group:
Hello everyone! This group is now set up as Gully "".
@UserX is the admin.
To participate in the game, please open a private chat with me:

**Inline Button**: `[ Register to Play ]`  
- This leads to a **deep link** (e.g., `t.me/YourBot?start=group_<group_id>`), so each user can start the registration flow in private.

---

## 5. Player (and Admin) Registration Flow
Whether **admin** or **regular** member, each person in the group must **register** in private to set a team name and become an active player in the Gully.

### 5.1 Start Command
- The user opens a private chat and taps `[ Register to Play ]` or types `/start`.  
- **Bot** checks if `telegram_id` is recognized.  
  - If new, the bot creates a new user record.  
  - If existing, the bot welcomes them back.

- The bot then **adds** the user to the Gully (if not already) with role `"member"` or `"admin"` (for the one user who added the bot). Everyone, including the admin, can proceed to form a team.

### 5.2 Team Name Setup
- **Bot**: "Welcome to Gully: `<GroupTitle>`. Let's set up your fantasy team!"  
- Inline keyboards:
[ Enter Team Name ]  [ Cancel ]
- If `[ Enter Team Name ]` → user either types a name or picks from suggestions.  
- The name is stored in `gully_participants.team_name`.

### 5.3 Inline Keyboards & Cancellation
- If the user **cancels**, the process stops. They can retry with `/start` or `[ Register to Play ]`.
- Once named, the user is fully recognized as a **manager** in the Gully.

---

## 6. Admin Tools
Even though the admin can play as a normal manager, they also get an **admin panel** with minimal features:

1. **Manage Gully**  
 - Could display high-level info, or any simple config you choose (like editing Gully name, if desired).

2. **View Participants**  
 - Shows who has joined, their team names, budgets, etc.

*(No "End Gully" or advanced features unless you add them.)*

---

## 7. Data Sync & Edge Cases
1. **Data Sync**  
 - Each newly registered user has:
   - An entry in `users` (with `telegram_id`, username, etc.).
   - A `gully_participants` record linked to the Gully, with a role (`"admin"` or `"member"`) and their `team_name`.

2. **Edge Cases**  
 - If the admin tries to register again or is already in the system, the bot simply updates their Gully participation if needed.  
 - If any user tries to re-init registration, the bot can confirm if they already have a team name set or let them rename if that's part of your design.

---

## 8. Example Conversations

### 8.1 Bot Joins Group
UserA (Group Owner) adds @YourBot

Bot (in group):
"Hello everyone!
A new Gully '' is set.
@UserA is the admin.
To play, tap [ Register to Play ]!"

### 8.2 Private Chat (Registration)
UserB taps [ Register to Play ].

Bot:
"Welcome to Gully ''.
Let's set up your fantasy team.
[ Enter Team Name ]  [ Cancel ]"
**If** `[ Enter Team Name ]` → user picks/enters `"Sunrisers"`:
Bot:
"Your team 'Sunrisers' is set!
Next steps:
[ Build Squad ]
[ Help / Commands ]"

### 8.3 Admin as a Player

UserA (admin) also taps [ Register to Play ] or types /start in private.

Bot:
"Welcome to Gully ''.
You're also the admin.
But let's set up your team as well!
[ Enter Team Name ]  [ Cancel ]"

After the admin chooses a name, they get additional admin tools:
Bot:
"Team 'Royal Tigers' is set!
Admin Tools:
[ Manage Gully ]  [ View Participants ]
Also as a player, you can:
[ Build Squad ]  [ Help / Commands ]"

---

## 9. Conclusion
By **auto-creating** the Gully upon bot addition, **assigning** a single admin who can **also** play, and giving everyone (including the admin) a streamlined registration in private chat, we achieve:

- Minimal friction: no explicit "create Gully" prompt needed.
- A single admin for any necessary league tasks, but who still competes normally.
- Simple, **inline keyboard**-driven flows for setting team names and getting started.  

With these steps, your users can quickly onboard, name their teams, and jump into squad-building or other features as soon as they register.

## 10. Implementation Status

The onboarding flow has been successfully implemented with the following components:

### Automatic Gully Creation
- ✅ Bot detects when it's added to a new group
- ✅ Automatically creates a Gully record with the group's name and ID
- ✅ Assigns the user who added the bot as the admin

### Welcome Message & Deep Link
- ✅ Bot sends a welcome message to the group when added
- ✅ Message includes a "Register to Play" button with a deep link
- ✅ Deep link contains the group ID for automatic association

### User Registration
- ✅ Users can start registration via deep link or `/start` command
- ✅ Bot creates user records for new users
- ✅ Bot adds users to the Gully with appropriate roles

### Team Name Setup
- ✅ Bot prompts users to set a team name
- ✅ Users can enter a custom team name
- ✅ Team names are stored in the database

### Admin & Member Flows
- ✅ Different welcome messages for admins vs. regular members
- ✅ Admins get additional admin tools
- ✅ Both admins and members can build squads

### Conversation Handling
- ✅ Proper conversation states for team name setup
- ✅ Cancel option to exit the registration flow
- ✅ Welcome back message for returning users

### Command Structure
- ✅ Different commands for private chats vs. group chats
- ✅ Admin-specific commands available to admins
- ✅ Core commands like `/start`, `/my_team`, and `/admin_panel`

### Current Limitations
- ⚠️ No team name validation or uniqueness check
- ⚠️ Limited admin functionality beyond viewing participants
- ⚠️ No way to transfer admin role to another user

## 11. Flow Diagram

                               ┌─────────────────────────────────────────────────────────────────────────┐
                               │           GROUP CHAT: Bot Added To Group                               │
                               └─────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌────────────────────────────────────────────────────────────┐
      │1) Bot checks if group has a linked Gully in the DB.       │
      │   - None -> auto-create Gully with name = group title,    │
      │     telegram_group_id = <group_id>                         │
      │   - The user who added the Bot becomes the Gully Admin.    │
      └────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌────────────────────────────────────────────────────────────────────────────────┐
      │2) Bot posts a message in the GROUP:                                          │
      │   "Hello everyone! Gully '<GroupTitle>' created automatically.               │
      │    @UserX is the admin.                                                      │
      │    Click [ Register to Play ] to open a private chat with me!"               │
      │                                                                              │
      │   Inline Keyboard:                                                           │
      │      [ Register to Play ] -> deep link: t.me/YourBot?start=group_<group_id>  │
      └────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                               ┌─────────────────────────────────────────────────────────────────────────┐
                               │         PRIVATE CHAT: Registration for ANY user (Admin or not)        │
                               └─────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌───────────────────────────────────────────────────────────────────────────────────────────┐
      │3) User taps "[ Register to Play ]" or manually opens the bot and types /start.          │
      │   - Bot checks if telegram_id already exists in `users`.                                │
      │   - If new -> create user record -> "User Created Successfully!"                        │
      │   - If existing -> "Welcome back!"                                                      │
      │   - Next, Bot adds user to Gully if not present (role = 'member' or 'admin').           │
      └───────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
      │4) Bot asks user to SET THEIR TEAM NAME (since they are now a manager in the Gully):         │
      │   "Welcome to Gully '<GroupTitle>'. Let's set up your fantasy team name."                  │
      │                                                                                            │
      │   Inline Keyboard:  [ Enter Team Name ]   [ Cancel ]                                       │
      │   - If 'Enter Team Name' -> user can type or pick from suggestions.                        │
      │   - If 'Cancel' -> flow ends (user can retry by /start or tapping [Register to Play]).     │
      └──────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
      │5) Bot stores the chosen team name in gully_participants.team_name.                          │
      │   Then displays:                                                                            │
      │   "Great, your team '<TeamName>' is set for Gully '<GroupTitle>'!"                          │
      │                                                                                            │
      │   Next inline keyboard might show next steps:                                              │
      │     [ Build Squad ]  [ View My Team ]  [ Help / Commands ]                                 │
      └──────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                               ┌─────────────────────────────────────────────────────────────────────────┐
                               │                      POST-REGISTRATION FLOW                           │
                               └─────────────────────────────────────────────────────────────────────────┘
                                                          │
      ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
      │6) If user (including Admin) selects [ Build Squad ] -> triggers Round 0 or relevant step:       │
      │   "You can pick your players or proceed to auctions, etc." (Implementation details vary)         │
      │   - This is typically shown via more inline keyboards:                                           │
      │       [ Select Batsmen ] [ Select Bowlers ] [ Check Squad ] etc.                                 │
      └──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                               ┌─────────────────────────────────────────────────────────────────────────┐
                               │                  ADMIN-SPECIFIC ACTIONS                               │
                               └─────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
      ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
      │7) Because the user who added the bot was designated 'admin', they also have admin tools:        │
      │   In PRIVATE CHAT, once they register a team, the Bot can show:                                 │
      │   "You are the admin of '<GroupTitle>'."                                                        │
      │   Inline Keyboard:                                                                              │
      │     [ Manage Gully ]   [ View Participants ]   [ Help ]                                         │
      │                                                                                                 │
      │   Where:                                                                                        │
      │   - [ Manage Gully ] might let them rename the gully or handle minimal settings, if desired.     │
      │   - [ View Participants ] shows a list of who has joined so far, team names, etc.               │
      │   - They can STILL do normal user actions (like building a squad, joining auctions) because      │
      │     admin can also play.                                                                        │
      └──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
   ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
   │8) End of Onboarding: Each user has a user record, a gully_participants row (role=member or admin),│
   │   and a team name. The group has one admin user. Everyone is ready to continue to the next phases. │
   └────────────────────────────────────────────────────────────────────────────────────────────────────┘