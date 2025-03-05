from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz
from decimal import Decimal

from src.db.session import get_session
from src.db.models import User, Player, TransferWindow, TransferListing, TransferBid, UserPlayerLink
from src.api.schemas.transfers import (
    TransferWindowResponse,
    TransferListingCreate,
    TransferListingResponse,
    TransferBidCreate,
    TransferBidResponse
)
from src.api.dependencies import get_current_user

router = APIRouter()

@router.get("/current", response_model=TransferWindowResponse)
async def get_current_transfer_window(session: Session = Depends(get_session)):
    """Get the current transfer window."""
    # Get the most recent transfer window
    transfer_window = session.exec(
        select(TransferWindow)
        .order_by(TransferWindow.start_time.desc())
        .limit(1)
    ).first()
    
    if not transfer_window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transfer window found"
        )
    
    # Check if the window is active
    now = datetime.now(pytz.UTC)
    if transfer_window.start_time <= now <= transfer_window.end_time:
        transfer_window.status = "active"
    elif now > transfer_window.end_time:
        transfer_window.status = "closed"
    else:
        transfer_window.status = "pending"
    
    session.add(transfer_window)
    session.commit()
    
    return transfer_window

@router.get("/listings", response_model=List[TransferListingResponse])
async def get_transfer_listings(
    window_id: int = None,
    status: str = "available",
    session: Session = Depends(get_session)
):
    """Get all available transfer listings."""
    query = select(TransferListing).where(TransferListing.status == status)
    
    if window_id:
        query = query.where(TransferListing.transfer_window_id == window_id)
    else:
        # Get current window
        current_window = session.exec(
            select(TransferWindow)
            .order_by(TransferWindow.start_time.desc())
            .limit(1)
        ).first()
        
        if current_window:
            query = query.where(TransferListing.transfer_window_id == current_window.id)
    
    listings = session.exec(query).all()
    return listings

@router.post("/list", response_model=TransferListingResponse)
async def create_transfer_listing(
    listing: TransferListingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List a player for transfer."""
    # Check if transfer window is active
    current_window = session.exec(
        select(TransferWindow)
        .order_by(TransferWindow.start_time.desc())
        .limit(1)
    ).first()
    
    if not current_window or current_window.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active transfer window"
        )
    
    # Check if user owns the player
    user_player = session.exec(
        select(UserPlayerLink)
        .where(
            UserPlayerLink.user_id == current_user.id,
            UserPlayerLink.player_id == listing.player_id
        )
    ).first()
    
    if not user_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't own this player"
        )
    
    # Check if player is already listed
    existing_listing = session.exec(
        select(TransferListing)
        .where(
            TransferListing.player_id == listing.player_id,
            TransferListing.transfer_window_id == current_window.id,
            TransferListing.status == "available"
        )
    ).first()
    
    if existing_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already listed for transfer"
        )
    
    # Create new listing
    new_listing = TransferListing(
        transfer_window_id=current_window.id,
        player_id=listing.player_id,
        seller_id=current_user.id,
        min_price=listing.min_price
    )
    
    session.add(new_listing)
    session.commit()
    session.refresh(new_listing)
    
    return new_listing

@router.post("/bid", response_model=TransferBidResponse)
async def create_transfer_bid(
    bid: TransferBidCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Place a bid on a listed player."""
    # Check if transfer window is active
    current_window = session.exec(
        select(TransferWindow)
        .order_by(TransferWindow.start_time.desc())
        .limit(1)
    ).first()
    
    if not current_window or current_window.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active transfer window"
        )
    
    # Get the listing
    listing = session.exec(
        select(TransferListing)
        .where(
            TransferListing.id == bid.listing_id,
            TransferListing.status == "available"
        )
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available"
        )
    
    # Check if user is trying to bid on their own player
    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot bid on your own player"
        )
    
    # Check if bid meets minimum price
    if bid.bid_amount < listing.min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bid must be at least {listing.min_price} cr"
        )
    
    # Check if user has enough budget
    if bid.bid_amount > current_user.budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient budget"
        )
    
    # Check if this is a free bid or paid bid
    is_free_bid = current_user.free_bids_used < 4
    
    # If it's a paid bid, check if user has enough budget for the fee
    if not is_free_bid and current_user.budget < (bid.bid_amount + Decimal('0.1')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient budget for bid fee"
        )
    
    # Create new bid
    new_bid = TransferBid(
        transfer_listing_id=listing.id,
        bidder_id=current_user.id,
        bid_amount=bid.bid_amount,
        is_free_bid=is_free_bid
    )
    
    session.add(new_bid)
    
    # Update free bids used if this is a free bid
    if is_free_bid:
        current_user.free_bids_used += 1
        session.add(current_user)
    
    session.commit()
    session.refresh(new_bid)
    
    return new_bid

@router.post("/accept-bid/{bid_id}", response_model=Dict[str, Any])
async def accept_transfer_bid(
    bid_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Accept a bid on a listed player."""
    # Get the bid
    bid = session.exec(
        select(TransferBid)
        .where(
            TransferBid.id == bid_id,
            TransferBid.status == "pending"
        )
    ).first()
    
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bid not found or not pending"
        )
    
    # Get the listing
    listing = session.exec(
        select(TransferListing)
        .where(
            TransferListing.id == bid.transfer_listing_id,
            TransferListing.status == "available"
        )
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available"
        )
    
    # Check if user is the seller
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the seller of this player"
        )
    
    # Get the bidder
    bidder = session.exec(select(User).where(User.id == bid.bidder_id)).first()
    
    if not bidder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bidder not found"
        )
    
    # Check if bidder has enough budget
    total_cost = bid.bid_amount
    if not bid.is_free_bid:
        total_cost += Decimal('0.1')  # Add 10 Lakhs fee for paid bids
    
    if bidder.budget < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bidder has insufficient budget"
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
    seller_link = session.exec(
        select(UserPlayerLink)
        .where(
            UserPlayerLink.user_id == current_user.id,
            UserPlayerLink.player_id == listing.player_id
        )
    ).first()
    
    if seller_link:
        session.delete(seller_link)
    
    # Then, add to buyer
    buyer_link = UserPlayerLink(
        user_id=bidder.id,
        player_id=listing.player_id
    )
    session.add(buyer_link)
    
    # 4. Update budgets
    # Deduct from buyer
    bidder.budget -= total_cost
    session.add(bidder)
    
    # Add to seller
    current_user.budget += bid.bid_amount
    session.add(current_user)
    
    # 5. Reject all other bids
    other_bids = session.exec(
        select(TransferBid)
        .where(
            TransferBid.transfer_listing_id == listing.id,
            TransferBid.id != bid.id,
            TransferBid.status == "pending"
        )
    ).all()
    
    for other_bid in other_bids:
        other_bid.status = "rejected"
        session.add(other_bid)
    
    session.commit()
    
    return {
        "success": True,
        "message": "Transfer completed successfully",
        "transfer": {
            "player_id": listing.player_id,
            "seller_id": current_user.id,
            "buyer_id": bidder.id,
            "amount": float(bid.bid_amount)
        }
    }

@router.post("/cancel-listing/{listing_id}", response_model=Dict[str, Any])
async def cancel_transfer_listing(
    listing_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Cancel a transfer listing."""
    # Get the listing
    listing = session.exec(
        select(TransferListing)
        .where(
            TransferListing.id == listing_id,
            TransferListing.status == "available"
        )
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available"
        )
    
    # Check if user is the seller
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the seller of this player"
        )
    
    # Cancel the listing
    listing.status = "cancelled"
    session.add(listing)
    
    # Reject all bids
    bids = session.exec(
        select(TransferBid)
        .where(
            TransferBid.transfer_listing_id == listing.id,
            TransferBid.status == "pending"
        )
    ).all()
    
    for bid in bids:
        bid.status = "rejected"
        session.add(bid)
    
    session.commit()
    
    return {
        "success": True,
        "message": "Listing cancelled successfully"
    }

@router.post("/create-window", response_model=TransferWindowResponse)
async def create_transfer_window(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new transfer window (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create transfer windows"
        )
    
    # Get the latest window to determine week number
    latest_window = session.exec(
        select(TransferWindow)
        .order_by(TransferWindow.week_number.desc())
        .limit(1)
    ).first()
    
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
        status="pending"
    )
    
    session.add(new_window)
    session.commit()
    session.refresh(new_window)
    
    return new_window

@router.post("/reset-free-bids", response_model=Dict[str, Any])
async def reset_free_bids(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Reset free bids for all users (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reset free bids"
        )
    
    # Reset free bids for all users
    users = session.exec(select(User)).all()
    
    for user in users:
        user.free_bids_used = 0
        session.add(user)
    
    session.commit()
    
    return {
        "success": True,
        "message": f"Free bids reset for {len(users)} users"
    }

@router.post("/process-deadline", response_model=Dict[str, Any])
async def process_transfer_deadline(
    window_id: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Process all transfers at the end of the transfer window."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can process the transfer deadline"
        )
    
    # Get the transfer window
    if window_id:
        transfer_window = session.exec(
            select(TransferWindow).where(TransferWindow.id == window_id)
        ).first()
    else:
        # Get the most recent window
        transfer_window = session.exec(
            select(TransferWindow)
            .order_by(TransferWindow.start_time.desc())
            .limit(1)
        ).first()
    
    if not transfer_window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer window not found"
        )
    
    # Check if window is closed
    now = datetime.now(pytz.UTC)
    if now < transfer_window.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer window is still active"
        )
    
    # Update window status
    transfer_window.status = "closed"
    session.add(transfer_window)
    
    # Get all available listings
    listings = session.exec(
        select(TransferListing)
        .where(
            TransferListing.transfer_window_id == transfer_window.id,
            TransferListing.status == "available"
        )
    ).all()
    
    # Process each listing
    transfers_processed = 0
    for listing in listings:
        # Get highest bid for this listing
        highest_bid = session.exec(
            select(TransferBid)
            .where(
                TransferBid.transfer_listing_id == listing.id,
                TransferBid.status == "pending"
            )
            .order_by(TransferBid.bid_amount.desc())
            .limit(1)
        ).first()
        
        if highest_bid:
            # Process the transfer
            
            # 1. Get the player
            player = session.exec(
                select(Player).where(Player.id == listing.player_id)
            ).first()
            
            if not player:
                continue
            
            # 2. Get seller and buyer
            seller = session.exec(
                select(User).where(User.id == listing.seller_id)
            ).first()
            
            buyer = session.exec(
                select(User).where(User.id == highest_bid.bidder_id)
            ).first()
            
            if not seller or not buyer:
                continue
            
            # 3. Remove player from seller's team
            seller_link = session.exec(
                select(UserPlayerLink)
                .where(
                    UserPlayerLink.user_id == seller.id,
                    UserPlayerLink.player_id == player.id
                )
            ).first()
            
            if seller_link:
                session.delete(seller_link)
            
            # 4. Add player to buyer's team
            buyer_link = UserPlayerLink(
                user_id=buyer.id,
                player_id=player.id,
                is_captain=False,
                is_vice_captain=False,
                is_playing_xi=False,
                round_number=transfer_window.week_number
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
            other_bids = session.exec(
                select(TransferBid)
                .where(
                    TransferBid.transfer_listing_id == listing.id,
                    TransferBid.id != highest_bid.id,
                    TransferBid.status == "pending"
                )
            ).all()
            
            for bid in other_bids:
                bid.status = "rejected"
                session.add(bid)
            
            transfers_processed += 1
        else:
            # No bids, cancel the listing
            listing.status = "cancelled"
            session.add(listing)
    
    # Reset free bids for all users
    users = session.exec(select(User)).all()
    for user in users:
        user.free_bids_used = 0
        session.add(user)
    
    session.commit()
    
    return {
        "success": True,
        "message": f"Transfer deadline processed. {transfers_processed} transfers completed.",
        "transfers_processed": transfers_processed
    } 