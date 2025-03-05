# GullyGuru Fantasy Cricket

A Telegram bot for fantasy cricket with auction, transfers, and live scoring.

## Features

- User registration and team management
- Player auctions with real-time bidding
- Weekly transfer windows
- Match predictions and polls
- Live scoring and leaderboards
- Multi-group support with separate gully leagues
- Admin controls for gully management

## Recent Updates

### Gully Management System
We've implemented a comprehensive gully management system that allows:
- Creating multiple fantasy cricket gullies across different Telegram groups
- Users can participate in multiple gullies simultaneously
- Each gully has its own auction, transfers, and leaderboard
- Automatic context switching based on group interactions
- Easy navigation between different gullies

For detailed documentation on the gully system, see [Gully Management Documentation](docs/group_management.md).

## TODO

### High Priority
1. **Playing XI Selection**
   - Implement daily lineup selection (11 players + Captain + Vice-Captain)
   - Add vice-captain designation functionality
   - Create UI for easy team selection before match deadlines
   - Add validation for team composition rules

2. **Scoring System**
   - Implement Dream11-style scoring rules
   - Add point calculations for batting (runs, boundaries, strike rate)
   - Add point calculations for bowling (wickets, economy rate, dot balls)
   - Implement captain (2×) and vice-captain (1.5×) point multipliers
   - Create daily and match-wise point summaries

### Medium Priority
1. **Notifications**
   - Add match start/end notifications
   - Create reminders for lineup submission deadlines
   - Implement transfer window opening/closing alerts

2. **Leaderboards**
   - Develop daily, weekly, and season-long leaderboards
   - Add tie-breaking logic based on total wickets, runs, etc.
   - Create head-to-head comparison between users

### Low Priority
1. **UI Improvements**
   - Enhance player cards with more statistics
   - Add graphical elements for team performance
   - Improve navigation in the bot interface

## Installation

[Installation instructions here]

## Usage

### Basic Commands
- `/start` - Register with the bot
- `/create_gully` - Create a new gully in a group (admin only)
- `/join_gully` - Join a gully in the current group
- `/my_gullies` - View all gullies you're participating in
- `/switch_gully` - Switch between different gullies
- `/gully_info` - View information about the current gully

### Team Management
- `/myteam` - View your current team
- `/players` - Browse available players
- `/captain` - Set your team captain

### Auction Commands
- `/bid` - Place a bid in an active auction
- `/auction_status` - Check the status of the current auction

## Contributing

[Contribution guidelines here]

## License

[License information here]



