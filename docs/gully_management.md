# Gully Management System

## Overview

The Gully Management System is responsible for handling the creation, configuration, and management of "gullies" - the fantasy cricket leagues within GullyGuru. Each gully represents a separate community of users competing against each other.

## Key Concepts

### What is a Gully?

In GullyGuru, a "gully" represents a cricket community group or league. The term comes from "gully cricket," a form of street cricket played in the Indian subcontinent. Key characteristics of a gully include:

1. **Community Structure**
   - A gully is a self-contained community with its own members, admins, and teams
   - Each gully can have its own rules, scoring systems, and competition formats

2. **Organizational Unit**
   - Gullies serve as the primary organizational unit within the system
   - All game activities, teams, and competitions exist within the context of a specific gully

3. **Telegram Integration**
   - Each gully is typically linked to a Telegram group for community interaction
   - The bot provides both group-wide and private command interfaces
   - Admins manage the gully through a combination of group and private commands

## Gully Creation Process

### 1. Create Telegram Group
- User creates a new Telegram group
- User adds GullyGuru bot to the group
- Bot automatically assigns admin role to the user who added it

### 2. Link Group to Gully
- Bot automatically creates a gully when added to a new group
- Bot assigns the user who added it as the gully admin
- Bot provides confirmation of successful gully creation

### 3. Add Users to Group
- Admin adds users to the Telegram group
- Users are automatically added to the gully
- Bot confirms successful joining

## Gully Participation

### Joining a Gully
- Users can join a gully by being added to the associated Telegram group
- The bot automatically registers new users and adds them to the gully
- Users can also join via invitation links or by using the `/start` command in the group

### Active Gully
- Users can participate in multiple gullies
- One gully is set as the "active" gully for each user
- Commands without explicit gully context operate on the active gully

### Switching Gullies
- Users can switch their active gully using the `/switch_gully` command
- The bot provides a list of gullies the user is part of
- User selects the gully they want to set as active

## Admin Management

### Admin Roles
- Each gully has one or more admins
- Admins have special privileges for managing the gully
- The original creator is automatically assigned as an admin

### Admin Commands
- Admins can use special commands to manage the gully
- Admin commands are only available to users with admin role
- Admin commands include starting auctions, managing users, etc.

### Admin Assignment
- The original creator can assign additional admins
- Admins can be assigned or removed using the admin panel
- Admin status is stored in the GullyParticipant table with the role field

## Technical Implementation

### Database Models
- `Gully` model stores basic information about the gully
- `GullyParticipant` model represents a user's participation in a gully
- The `role` field in GullyParticipant determines admin status

### API Endpoints
- Endpoints for creating, retrieving, and managing gullies
- Endpoints for managing gully participants
- Admin-specific endpoints with proper authorization

### Bot Commands
- Commands for creating and joining gullies
- Commands for switching active gully
- Admin commands for gully management

## Best Practices

1. **Automatic Registration**: Users should be automatically registered when added to a group
2. **Clear Feedback**: Provide clear feedback for all gully-related actions
3. **Permission Checks**: Always verify user permissions before allowing admin actions
4. **Context Awareness**: Commands should be aware of the current gully context
5. **Error Handling**: Provide helpful error messages for failed operations 