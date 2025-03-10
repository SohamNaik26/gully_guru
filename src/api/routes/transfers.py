from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz
from decimal import Decimal

from src.db.session import get_session
from src.db.models import (
    User,
    Player,
    TransferWindow,
    TransferListing,
    TransferBid,
    UserPlayer,
)
from src.api.schemas.transfers import (
    TransferWindowResponse,
    TransferListingCreate,
    TransferListingResponse,
    TransferBidCreate,
    TransferBidResponse,
)
from src.api.dependencies import get_current_user

router = APIRouter()


@router.get("/current", response_model=TransferWindowResponse)
async def get_current_transfer_window(session: AsyncSession = Depends(get_session)):
    """Get the current transfer window."""
    # Get the most recent transfer window
    result = await session.execute(
        select(TransferWindow).order_by(TransferWindow.start_time.desc()).limit(1)
    )
    transfer_window = result.scalars().first()

    if not transfer_window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No transfer window found"
        )

    # Check if the window is active
    now = datetime.now(pytz.UTC)
    if transfer_window.start_time <= now <= transfer_window.end_time:
        transfer_window.status = "active"
    elif now > transfer_window.end_time:
        transfer_window.status = "closed"
    else:
        transfer_window.status = "pending"

    return transfer_window


@router.get("/listings", response_model=List[TransferListingResponse])
async def get_transfer_listings(
    window_id: int = None,
    status: str = "available",
    session: AsyncSession = Depends(get_session),
):
    """Get all available transfer listings."""
    query = select(TransferListing).where(TransferListing.status == status)

    if window_id:
        query = query.where(TransferListing.transfer_window_id == window_id)
    else:
        # Get current window
        result = await session.execute(
            select(TransferWindow).order_by(TransferWindow.start_time.desc()).limit(1)
        )
        current_window = result.scalars().first()

        if current_window:
            query = query.where(TransferListing.transfer_window_id == current_window.id)

    result = await session.execute(query)
    listings = result.scalars().all()
    return listings


@router.post("/list", response_model=TransferListingResponse)
async def create_transfer_listing(
    listing: TransferListingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List a player for transfer."""
    # Check if transfer window is active
    result = await session.execute(
        select(TransferWindow).order_by(TransferWindow.start_time.desc()).limit(1)
    )
    current_window = result.scalars().first()

    if not current_window or current_window.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No active transfer window"
        )

    # Check if user owns the player
    result = await session.execute(
        select(UserPlayer).where(
            UserPlayer.user_id == current_user.id,
            UserPlayer.player_id == listing.player_id,
        )
    )
    user_player = result.scalars().first()

    if not user_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You don't own this player"
        )

    # Check if player is already listed
    result = await session.execute(
        select(TransferListing).where(
            TransferListing.player_id == listing.player_id,
            TransferListing.transfer_window_id == current_window.id,
            TransferListing.status == "available",
        )
    )
    existing_listing = result.scalars().first()

    if existing_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already listed for transfer",
        )

    # Create new listing
    new_listing = TransferListing(
        transfer_window_id=current_window.id,
        player_id=listing.player_id,
        seller_id=current_user.id,
        min_price=listing.min_price,
    )

    session.add(new_listing)
    await session.commit()
    await session.refresh(new_listing)

    return new_listing


@router.post("/bid", response_model=TransferBidResponse)
async def create_transfer_bid(
    bid: TransferBidCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Place a bid on a listed player."""
    # Check if transfer window is active
    result = await session.execute(
        select(TransferWindow).order_by(TransferWindow.start_time.desc()).limit(1)
    )
    current_window = result.scalars().first()

    if not current_window or current_window.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No active transfer window"
        )

    # Get the listing
    result = await session.execute(
        select(TransferListing).where(
            TransferListing.id == bid.listing_id, TransferListing.status == "available"
        )
    )
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available",
        )

    # Check if user is trying to bid on their own player
    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot bid on your own player",
        )

    # Check if bid meets minimum price
    if bid.bid_amount < listing.min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bid must be at least {listing.min_price} cr",
        )

    # Check if user has enough budget
    if bid.bid_amount > current_user.budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient budget"
        )

    # Check if this is a free bid or paid bid
    is_free_bid = current_user.free_bids_used < 4

    # If it's a paid bid, check if user has enough budget for the fee
    if not is_free_bid and current_user.budget < (bid.bid_amount + Decimal("0.1")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient budget for bid fee",
        )

    # Create new bid
    new_bid = TransferBid(
        transfer_listing_id=listing.id,
        bidder_id=current_user.id,
        bid_amount=bid.bid_amount,
        is_free_bid=is_free_bid,
    )

    session.add(new_bid)

    # Update free bids used if this is a free bid
    if is_free_bid:
        current_user.free_bids_used += 1
        session.add(current_user)

    await session.commit()
    await session.refresh(new_bid)

    return new_bid


@router.post("/accept-bid/{bid_id}", response_model=Dict[str, Any])
async def accept_transfer_bid(
    bid_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Accept a bid on a listed player."""
    # Get the bid
    result = await session.execute(
        select(TransferBid).where(
            TransferBid.id == bid_id, TransferBid.status == "pending"
        )
    )
    bid = result.scalars().first()

    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found or not pending"
        )

    # Get the listing
    result = await session.execute(
        select(TransferListing).where(
            TransferListing.id == bid.transfer_listing_id,
            TransferListing.status == "available",
        )
    )
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available",
        )

    # Check if user is the seller
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the seller of this player",
        )

    # Get the bidder
    result = await session.execute(select(User).where(User.id == bid.bidder_id))
    bidder = result.scalars().first()

    if not bidder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bidder not found"
        )

    # Check if bidder has enough budget
    total_cost = bid.bid_amount
    if not bid.is_free_bid:
        total_cost += Decimal("0.1")  # Add 10 Lakhs fee for paid bids

    if bidder.budget < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bidder has insufficient budget",
        )

    # Process the transfer
    # 1. Update the bid status
    bid.status = "accepted"
    session.add(bid)

    # 2. Update the listing status
    listing.status = "sold"
    session.add(listing)

    # 3. Transfer the player
    # First, remove from seller
    result = await session.execute(
        select(UserPlayer).where(
            UserPlayer.user_id == current_user.id,
            UserPlayer.player_id == listing.player_id,
        )
    )
    seller_link = result.scalars().first()

    if seller_link:
        session.delete(seller_link)

    # Then, add to buyer
    buyer_link = UserPlayer(user_id=bidder.id, player_id=listing.player_id)
    session.add(buyer_link)

    # 4. Update budgets
    # Deduct from buyer
    bidder.budget -= total_cost
    session.add(bidder)

    # Add to seller
    current_user.budget += bid.bid_amount
    session.add(current_user)

    # 5. Reject all other bids
    result = await session.execute(
        select(TransferBid).where(
            TransferBid.transfer_listing_id == listing.id,
            TransferBid.id != bid.id,
            TransferBid.status == "pending",
        )
    )
    other_bids = result.scalars().all()

    for other_bid in other_bids:
        other_bid.status = "rejected"
        session.add(other_bid)

    await session.commit()

    return {
        "success": True,
        "message": "Transfer completed successfully",
        "transfer": {
            "player_id": listing.player_id,
            "seller_id": current_user.id,
            "buyer_id": bidder.id,
            "amount": float(bid.bid_amount),
        },
    }


@router.post("/cancel-listing/{listing_id}", response_model=Dict[str, Any])
async def cancel_transfer_listing(
    listing_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Cancel a transfer listing."""
    # Get the listing
    result = await session.execute(
        select(TransferListing).where(
            TransferListing.id == listing_id, TransferListing.status == "available"
        )
    )
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available",
        )

    # Check if user is the seller
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the seller of this player",
        )

    # Cancel the listing
    listing.status = "cancelled"
    session.add(listing)

    # Reject all bids
    result = await session.execute(
        select(TransferBid).where(
            TransferBid.transfer_listing_id == listing.id,
            TransferBid.status == "pending",
        )
    )
    bids = result.scalars().all()

    for bid in bids:
        bid.status = "rejected"
        session.add(bid)

    await session.commit()

    return {"success": True, "message": "Listing cancelled successfully"}


@router.post("/create-window", response_model=TransferWindowResponse)
async def create_transfer_window(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new transfer window (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create transfer windows",
        )

    # Get the latest window to determine week number
    result = await session.execute(
        select(TransferWindow).order_by(TransferWindow.week_number.desc()).limit(1)
    )
    latest_window = result.scalars().first()

    week_number = 1
    if latest_window:
        week_number = latest_window.week_number + 1

    # Create start time (next Friday at 11 PM)
    now = datetime.now(pytz.UTC)
    days_until_friday = (4 - now.weekday()) % 7  # 4 is Friday
    if days_until_friday == 0 and now.hour >= 23:
        days_until_friday = 7  # If it's Friday after 11 PM, go to next Friday

    start_time = now + timedelta(days=days_until_friday)
    start_time = start_time.replace(hour=23, minute=0, second=0, microsecond=0)

    # End time is 48 hours later
    end_time = start_time + timedelta(hours=48)

    # Create new window
    new_window = TransferWindow(
        week_number=week_number,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )

    session.add(new_window)
    await session.commit()
    await session.refresh(new_window)

    return new_window


@router.post("/reset-free-bids", response_model=Dict[str, Any])
async def reset_free_bids(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Reset free bids for all users (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reset free bids",
        )

    # Reset free bids for all users
    result = await session.execute(select(User))
    users = result.scalars().all()

    for user in users:
        user.free_bids_used = 0
        session.add(user)

    await session.commit()

    return {"success": True, "message": f"Free bids reset for {len(users)} users"}


@router.post("/process-deadline", response_model=Dict[str, Any])
async def process_transfer_deadline(
    window_id: int = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Process all transfers at the end of the transfer window."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can process the transfer deadline",
        )

    # Get the transfer window
    if window_id:
        result = await session.execute(
            select(TransferWindow).where(TransferWindow.id == window_id)
        )
        transfer_window = result.scalars().first()
    else:
        # Get the most recent window
        result = await session.execute(
            select(TransferWindow).order_by(TransferWindow.start_time.desc()).limit(1)
        )
        transfer_window = result.scalars().first()

    if not transfer_window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transfer window not found"
        )

    # Check if window is closed
    now = datetime.now(pytz.UTC)
    if now < transfer_window.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer window is still active",
        )

    # Update window status
    transfer_window.status = "closed"
    session.add(transfer_window)

    # Get all available listings
    result = await session.execute(
        select(TransferListing).where(
            TransferListing.transfer_window_id == transfer_window.id,
            TransferListing.status == "available",
        )
    )
    listings = result.scalars().all()

    # Process each listing
    transfers_processed = 0
    for listing in listings:
        # Get highest bid for this listing
        result = await session.execute(
            select(TransferBid)
            .where(
                TransferBid.transfer_listing_id == listing.id,
                TransferBid.status == "pending",
            )
            .order_by(TransferBid.bid_amount.desc())
            .limit(1)
        )
        highest_bid = result.scalars().first()

        if highest_bid:
            # Process the transfer

            # 1. Get the player
            result = await session.execute(
                select(Player).where(Player.id == listing.player_id)
            )
            player = result.scalars().first()

            if not player:
                continue

            # 2. Get seller and buyer
            result = await session.execute(
                select(User).where(User.id == listing.seller_id)
            )
            seller = result.scalars().first()

            result = await session.execute(
                select(User).where(User.id == highest_bid.bidder_id)
            )
            buyer = result.scalars().first()

            if not seller or not buyer:
                continue

            # 3. Remove player from seller's team
            result = await session.execute(
                select(UserPlayer).where(
                    UserPlayer.user_id == seller.id,
                    UserPlayer.player_id == player.id,
                )
            )
            seller_link = result.scalars().first()

            if seller_link:
                session.delete(seller_link)

            # 4. Add player to buyer's team
            buyer_link = UserPlayer(
                user_id=buyer.id,
                player_id=player.id,
                is_captain=False,
                is_vice_captain=False,
                is_playing_xi=False,
                round_number=transfer_window.week_number,
            )

            session.add(buyer_link)

            # 5. Update budgets
            seller.budget += highest_bid.bid_amount
            buyer.budget -= highest_bid.bid_amount

            # If it was a paid bid, deduct the bid fee
            if not highest_bid.is_free_bid:
                buyer.budget -= Decimal("0.1")  # 10 Lakhs fee

            session.add(seller)
            session.add(buyer)

            # 6. Update listing and bid status
            listing.status = "sold"
            highest_bid.status = "accepted"

            session.add(listing)
            session.add(highest_bid)

            # 7. Reject all other bids
            result = await session.execute(
                select(TransferBid).where(
                    TransferBid.transfer_listing_id == listing.id,
                    TransferBid.id != highest_bid.id,
                    TransferBid.status == "pending",
                )
            )
            other_bids = result.scalars().all()

            for bid in other_bids:
                bid.status = "rejected"
                session.add(bid)

            transfers_processed += 1
        else:
            # No bids, cancel the listing
            listing.status = "cancelled"
            session.add(listing)

    # Reset free bids for all users
    result = await session.execute(select(User))
    users = result.scalars().all()
    for user in users:
        user.free_bids_used = 0
        session.add(user)

    await session.commit()

    return {
        "success": True,
        "message": f"Transfer deadline processed. {transfers_processed} transfers completed.",
        "transfers_processed": transfers_processed,
    }
