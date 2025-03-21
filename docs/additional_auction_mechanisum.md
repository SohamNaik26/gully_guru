📌 Updated Streamlined Auction Queue Flow with Requested Changes

Changes Implemented:
✅ Step 1 Validation is removed from bot logic; the API response itself determines whether the auction can proceed.
✅ Skipping Mechanism:
	•	Individual skips are not posted in the group chat.
	•	A skip counter is maintained internally.
	•	If all participants skip, the player is skipped, and the next player is fetched.

⸻

🚀 Streamlined Auction Queue Flow (Updated)

1️⃣ Step 1: Initiating the Next Player

Trigger:
	•	/next_player command is called in the Telegram group.

API Request:

GET /auction/gullies/{gully_id}/next-player

Bot UI Update:
	•	Display the player details (based on API response):

Player: Virat Kohli 🏏
Team: RCB
Player Type: BAT
Base Price: 2.0 CR


	•	Reply Keyboard (Telegram Inline Buttons):

[ 💰 Bid ]    [ ⏭️ Skip ]



✅ No additional validation is needed. The bot only uses API response for displaying the player.

⸻

2️⃣ Step 2: Handling Skips Efficiently

Trigger:
	•	A participant presses Skip.

Implementation:
	•	Do not post a “Skip” message in the group.
	•	Maintain a context variable to track who has skipped.

✅ Check for Full Skips:
	•	If all participants have pressed Skip, the bot does:

POST /auction/gullies/{gully_id}/skip-player

	•	This marks the player as skipped in the auction queue.
	•	Then, the bot automatically fetches the next player.

Bot UI Update (Only When All Participants Skip):

🚫 All participants skipped. Moving to the next player...

✅ Next Step: Fetch a new player via:

GET /auction/gullies/{gully_id}/next-player



⸻

3️⃣ Step 3: Bidding Process

Trigger:
	•	A participant presses Bid.

API Request:

POST /auction/bid

Bid Increment Logic:

Current Price (CR)	Increment (CR)
< 2	+0.1
2 - 5	+0.5
5 - 10	+1.0
> 10	+2.0

Bot UI Update:

💰 Bid of 2.5 CR placed by @username

✅ Bid Timer: Every bid resets a 15-second countdown.

⸻

4️⃣ Step 4: Winning a Bid

Trigger:
	•	No bids for 15 seconds, the last bid wins.

API Request:

POST /auction/resolve-contested/{player_id}/{winning_participant_id}

Bot UI Update:

🎉 @username won the bid for Virat Kohli at 2.5 CR!

✅ Next Step: Call /next_player to continue.

⸻


⸻

✅ Final API Endpoints Used

API Endpoint	Method	Purpose
/auction/gullies/{gully_id}/next-player	GET	Fetches the next player for auction
/auction/gullies/{gully_id}/skip-player	POST	Skips player if all participants press skip
/auction/bid	POST	Places a bid on the current player
/auction/resolve-contested/{player_id}/{winning_participant_id}	POST	Assigns a player to the winning participant