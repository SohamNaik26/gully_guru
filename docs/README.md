# GullyGuru Documentation

## Overview

This directory contains comprehensive documentation for the GullyGuru fantasy cricket platform. The documentation is organized into core functional areas to provide clear guidance for implementation.

## Core Documentation

### [User Management System](user_management.md)
Comprehensive documentation covering:
- User registration and authentication
- Profile management
- Group setup and administration
- Gully creation and management
- Role-based permissions
- Information visibility and privacy considerations

### [Auction Management System](auction_management.md)
Detailed documentation covering:
- Round 0: Initial squad submission
- Round 1: Contested players auction
- Bidding system
- Player allocation
- Auction scheduling and management
- Information visibility and privacy considerations

## Technical Documentation

### [Database Migration](db_migration.md)
Information about database schema migrations and management.

### [API Documentation](api.md)
General API design principles and patterns.

### [API Schemas](api_schemas.md)
Detailed information about API request and response schemas.

## Conceptual Documentation

### [Game Plan](gameplan.md)
High-level overview of the GullyGuru fantasy cricket game mechanics.

### [Group Management](group_management.md)
Conceptual overview of the gully management system.

## Implementation Approach

The implementation follows a modular approach with clear separation of concerns:

1. **Database Layer**: SQLModel-based models with proper relationships
2. **Service Layer**: Business logic encapsulated in service classes
3. **API Layer**: FastAPI endpoints with proper validation
4. **Bot Layer**: Telegram bot commands and callbacks

Each functional area is implemented across all layers, ensuring consistency and maintainability.

## Getting Started

For new developers, we recommend starting with:
1. Review the [Game Plan](gameplan.md) to understand the overall concept
2. Study the [User Management System](user_management.md) documentation
3. Explore the [Auction Management System](auction_management.md) documentation
4. Refer to technical docs as needed during implementation 