Final API Specification with Auction Queue ID for Faster DB Queries

I have updated all responses to include auction_queue_id, ensuring faster lookups and better performance during database transactions.

⸻

1️⃣ GET /auction/gullies/{gully_id}/next-player

Purpose

Fetch the next player from the auction queue and provide current budget & team details for all participants in the Gully.

Input

Parameter	Type	Required	Description
gully_id	int	✅ Yes	The ID of the Gully for which the auction is ongoing.

Output

{
  "player": {
    "auction_queue_id": 501,  
    "player_id": 205,
    "name": "Shubman Gill",
    "team": "GT",
    "player_type": "BAT",
    "base_price": 80.0
  },
  "participants": [
    {
      "participant_id": 101,
      "team_name": "Team Alpha",
      "budget": 60.0,
      "players_owned": 15,
      "players_remaining": 3,
      "team": [
        {
          "player_id": 201,
          "name": "Virat Kohli",
          "purchase_price": 120.0
        },
        {
          "player_id": 301,
          "name": "Rohit Sharma",
          "purchase_price": 140.0
        }
      ]
    },
    {
      "participant_id": 102,
      "team_name": "Team Beta",
      "budget": 90.0,
      "players_owned": 13,
      "players_remaining": 5,
      "team": [
        {
          "player_id": 305,
          "name": "MS Dhoni",
          "purchase_price": 110.0
        }
      ]
    }
  ]
}



⸻

State Changes in Database

🔹 No state changes occur in this route. This is a read-only operation.

⸻



⸻

2️⃣ POST /auction/resolve-contested/{player_id}/{winning_participant_id}

Purpose

Assigns a contested player to the winning participant, updates the participant’s budget, registers the final bid in the Bid table, and removes the player from the auction queue.

Input

Parameter	Type	Required	Description
player_id	int	✅ Yes	The ID of the contested player being auctioned.
winning_participant_id	int	✅ Yes	The ID of the participant who won the bid.

Request Body

{
  "auction_queue_id": 501,
  "bid_amount": 120.0
}

Output

{
  "status": "success",
  "auction_queue_id": 501,
  "message": "Player successfully assigned."
}



⸻

Steps Executed by this Route

1️⃣ Validate Inputs
	•	Ensure that player_id exists in AuctionQueue and has status "bidding".
	•	Ensure that winning_participant_id exists in GullyParticipant.
	•	Ensure that bid_amount is within the winning participant’s budget.

2️⃣ Register the Final Bid in Bid Table
	•	Insert the winning bid into the Bid table:

INSERT INTO Bid (auction_queue_id, gully_participant_id, bid_amount, bid_time)
VALUES (:auction_queue_id, :winning_participant_id, :bid_amount, NOW());



3️⃣ Assign Player to the Participant
	•	Insert a new row in ParticipantPlayer:

INSERT INTO ParticipantPlayer (gully_participant_id, player_id, purchase_price, purchase_date, status)
VALUES (:winning_participant_id, :player_id, :bid_amount, NOW(), "owned");



4️⃣ Deduct the Winning Amount from Budget
	•	Update the budget in GullyParticipant:

UPDATE GullyParticipant
SET budget = budget - :bid_amount
WHERE id = :winning_participant_id;



5️⃣ Remove Player from the Auction Queue
	•	Update AuctionQueue to mark this player’s auction as "completed":

UPDATE AuctionQueue
SET status = "completed"
WHERE id = :auction_queue_id;



6️⃣ Return Success Response
	•	Send a minimal response confirming the transaction.

⸻

State Changes in Database

Table	Action
Bid	INSERT: Stores the final bid details.
ParticipantPlayer	INSERT: Adds the player to the winning participant’s team.
GullyParticipant	UPDATE: Deducts the bid amount from the participant’s budget.
AuctionQueue	UPDATE: Marks the auction as "completed".



⸻



⸻

3️⃣ POST /auction/revert/{player_id}/{winning_participant_id}

Purpose

Reverts a previously assigned auctioned player, restoring the auction queue and refunding the bid amount.

Input

Parameter	Type	Required	Description
player_id	int	✅ Yes	The ID of the player whose assignment should be reverted.
winning_participant_id	int	✅ Yes	The ID of the participant to whom the player was assigned.

Request Body

{
  "auction_queue_id": 501
}

Output

{
  "status": "success",
  "auction_queue_id": 501,
  "message": "Auction result reverted. Player returned to auction queue."
}



⸻

Steps Executed by this Route

1️⃣ Validate Inputs
	•	Ensure the player_id is currently owned by winning_participant_id in ParticipantPlayer.
	•	Ensure that a bid was registered in Bid for this player_id.

2️⃣ Refund the Winning Participant’s Budget
	•	Retrieve the bid_amount from the Bid table.
	•	Update the budget in GullyParticipant:

UPDATE GullyParticipant
SET budget = budget + :bid_amount
WHERE id = :winning_participant_id;



3️⃣ Remove Player from ParticipantPlayer
	•	Delete the player from ParticipantPlayer:

DELETE FROM ParticipantPlayer
WHERE gully_participant_id = :winning_participant_id AND player_id = :player_id;



4️⃣ Restore the Player to AuctionQueue
	•	Update the AuctionQueue table to set the status back to "pending":

UPDATE AuctionQueue
SET status = "pending"
WHERE id = :auction_queue_id;



5️⃣ Return Success Response
	•	Send a minimal response confirming the reversion.

⸻

State Changes in Database

Table	Action
GullyParticipant	UPDATE: Restores the refunded amount.
ParticipantPlayer	DELETE: Removes the player from the participant’s squad.
AuctionQueue	UPDATE: Restores player to the auction queue.



⸻

Final Summary

Route	HTTP Method	Purpose	State Changes
/auction/gullies/{gully_id}/next-player	GET	Fetches the next player for auction	❌ No state changes
/auction/resolve-contested/{player_id}/{winning_participant_id}	POST	Assigns the player & registers bid	✅ Updates bid, budget, player ownership, auction queue
/auction/revert/{player_id}/{winning_participant_id}	POST	Reverts auction result	✅ Restores budget, removes player, resets auction queue
