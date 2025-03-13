# Telegram UI-UX Flow

This document outlines the **Telegram user interface (UI) and user experience (UX)** for the GullyGuru fantasy cricket platform, separating **private chat** (DM) flows from **group chat** interactions. It presents the **Main Menu**, plus the major sub-menus (My Squad, Auctions, Transfers, Leaderboard, Help, Admin Panel), alongside notes on where each interaction occurs and which inline keyboards are used.

---

## Table of Contents

1. [Overview of Roles](#overview-of-roles)  
2. [Group Chat Flows](#group-chat-flows)  
   - [Announcements](#announcements)  
   - [Bot Added to Group (Onboarding Trigger)](#bot-added-to-group-onboarding-trigger)  
   - [Auction Live Updates (Optional)](#auction-live-updates-optional)  
3. [Private Chat (Main Menu)](#private-chat-main-menu)  
   - [Structure](#structure)  
   - [Navigation Conventions](#navigation-conventions)  
4. [Private Chat: Sub-Menus](#private-chat-sub-menus)  
   - [4.1 My Squad](#41-my-squad)  
   - [4.2 Auctions](#42-auctions)  
   - [4.3 Transfers](#43-transfers)  
   - [4.4 Leaderboard](#44-leaderboard)  
   - [4.5 Help](#45-help)  
   - [4.6 Admin Panel](#46-admin-panel)  
5. [Final User Flow Diagram](#final-user-flow-diagram)  
6. [Conclusion](#conclusion)

---

## 1. Overview of Roles

1. **Admin**: The user who added the bot to the group. Can also play the game, but sees an extra “[ Admin Panel ]” in private chat.  
2. **Regular Member**: Anyone else in the group. Joins the Gully, sets a team name, and uses the same private chat menu minus admin features.

---

## 2. Group Chat Flows

### Announcements
- The bot occasionally posts announcements (e.g., “Round 0 starts,” “Auction ends in 2 hours,” etc.).  
- Users can see these in the group but typically are directed to private chat for actions.

### Bot Added to Group (Onboarding Trigger)
1. **Bot** detects no existing Gully → automatically creates one.  
2. Bot posts: “Gully ‘<GroupTitle>’ created. @UserX is admin. Tap [ Register to Play ]!”  
   - Inline button: `[ Register to Play ]` → private chat link (deep link).

### Auction Live Updates (Optional)
- If you choose to show real-time auction updates in the group, the bot might say:  
  “Player X at 2.5 Cr. Highest bid by @UserB. 10 seconds remain.”  
- Actual bidding still occurs in private chat, or you can decide to allow group-based bidding.  
- For an MVP, you may keep auctions primarily in private.

---

## 3. Private Chat (Main Menu)

### Structure
After a user completes onboarding (registering and naming their team), the bot shows them a **Main Menu** in private:
[ My Squad ]
[ Auctions ]
[ Transfers ]
[ Leaderboard ]
[ Help ]
[ Admin Panel ]    <– Only if user is admin
[ Cancel ]

Whenever the user returns to private chat or types `/start`, they see this menu again.

### Navigation Conventions
- **Inline Keyboards**: Each menu option is an inline button.  
- **Cancel**: Cancels or ends the conversation flow. The user can type `/start` to see the menu again.  
- **Back**: Sub-menus can provide a `[ Back to Main Menu ]` (or `[ Back ]`) button.

---

## 4. Private Chat: Sub-Menus

### 4.1 My Squad
**When user taps `[ My Squad ]`:**  

“Team , Budget 
Players:
	1.	…
	2.	…
Points: 

[ Set Captain ] (if relevant)
[ Edit Squad ]  (only if Round 0 or Transfer Window is open)
[ Back to Main Menu ] [ Cancel ]

- **Set Captain**: Might show an inline list of the user’s squad.  
- **Edit Squad**: In Round 0 or Transfer Window, user can add/remove players. If not relevant, you can hide or remove this option.

---

### 4.2 Auctions
**When user taps `[ Auctions ]`:**  

[ Round 0: Submit Squad ]  (shown if Round 0 is ongoing)
[ Current Auction ]        (shown if there’s a live or upcoming auction)
[ Auction Status ]         (always, or only if an auction is scheduled)
[ Back to Main Menu ] [ Cancel ]

- **Round 0: Submit Squad**: Takes the user to a flow for picking initial players if they haven’t submitted yet.  
- **Current Auction**: Could handle contested players or weekly auctions.  
- **Auction Status**: E.g., “Next player up: Player X. Bidding at 3.0 Cr.”

---

### 4.3 Transfers
**When user taps `[ Transfers ]`:**  
[ List My Player for Sale ]
[ View Transfer Market ]
[ My Pending Bids ]
[ Back to Main Menu ] [ Cancel ]

If the **transfer** period isn’t active, either show an error or hide these options.

---

### 4.4 Leaderboard
**When user taps `[ Leaderboard ]`:**  
“Current Rankings:
	1.	…
	2.	…
…

[ View Detailed Stats ] [ Back to Main Menu ] [ Cancel ]

At a minimum, you can just list top teams. `[ View Detailed Stats ]` is optional.

---

### 4.5 Help
**When user taps `[ Help ]`:**  
“Need assistance?
	•	You can see your squad with [My Squad].
	•	To buy players, use [Auctions] or [Transfers].
	•	For admin tasks, see [Admin Panel].”

[ Back to Main Menu ] [ Cancel ]

Feel free to expand with an FAQ or commands list.

---

### 4.6 Admin Panel
**Only visible if the user is `admin`**:  

[ Manage Gully ]       (rename gully, if you want)
[ View Participants ]  (lists current teams, budgets)
[ Back to Main Menu ] [ Cancel ]

Keep it minimal for MVP.

---

## 5. Final User Flow Diagram

Below is a **combined text diagram** showing how the user enters private chat, sees the main menu, and drills into each sub-menu. **Group** chat steps are shown only where relevant.

GROUP CHAT:
(1) Bot is added -> Gully Created -> “Hello! Gully ‘’ created.
@UserA is admin. Everyone tap [ Register to Play ] to begin.”

PRIVATE CHAT:
(2) User taps [ Register to Play ] or /start
-> If new user, create record, ask team name, confirm.

MAIN MENU (private):

[ My Squad ]      [ Auctions ]         [ Transfers ]
[ Leaderboard ]   [ Help ]             [ Admin Panel ] (if admin)
[ Cancel ]

My Squad:
“Team , Budget , Players…, Points ”
[ Set Captain ] [ Edit Squad ] (if relevant)
[ Back to Main Menu ] [ Cancel ]

Auctions:
[ Round 0: Submit Squad ] (if relevant)
[ Current Auction ]
[ Auction Status ]
[ Back to Main Menu ] [ Cancel ]

Transfers:
[ List My Player ] [ View Transfer Market ] [ My Pending Bids ]
[ Back to Main Menu ] [ Cancel ]

Leaderboard:
“Standings…”
[ View Detailed Stats ]
[ Back to Main Menu ] [ Cancel ]

Help:
	•	Basic instructions or FAQ
[ Back to Main Menu ] [ Cancel ]

Admin Panel: (if user.role=“admin”)
[ Manage Gully ] [ View Participants ]
[ Back to Main Menu ] [ Cancel ]


At any **nested** level, the user can press `[ Back to Main Menu ]` to go up one level, or `[ Cancel ]` to completely end the flow.  

---

## 6. Conclusion

This **Telegram UI-UX Flow** document provides:

1. **Group Chat** usage for announcements and onboarding.  
2. A **private chat** **Main Menu** with minimal sub-menus:
   - **My Squad**, **Auctions**, **Transfers**, **Leaderboard**, **Help**, **Admin Panel**.  
3. **Hide** or **remove** items when not relevant to avoid confusion. For example, if Round 0 ended, remove `[ Round 0: Submit Squad ]`.  
4. **Consistent** `[ Cancel ]` or `[ Back ]` options at each level.  

This lean design keeps the bot interface simple while covering all essential features. You can expand sub-flows (Auctions, Transfers, etc.) as needed without complicating the overall user experience. 


# implement a plan for the flow 
Let us create an implementation plan for the overall main menu in public and private Kali, based on this design. And before doing any kind of implementation, let's just talk through the process and make sure we have critiqued all the loopholes you find within the overall process.