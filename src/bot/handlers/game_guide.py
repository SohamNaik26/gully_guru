import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Configure logging
logger = logging.getLogger(__name__)


async def game_guide_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /game_guide command.
    Provides information about cricket terminology and game concepts.
    """
    # Get the user's query if any
    query = " ".join(context.args).lower() if context.args else ""

    # If a specific term was queried, show that term's explanation
    if query:
        explanation = get_term_explanation(query)
        if explanation:
            await update.message.reply_text(explanation, parse_mode="Markdown")
        else:
            # Term not found, suggest similar terms
            similar_terms = get_similar_terms(query)
            if similar_terms:
                text = (
                    f"I couldn't find an explanation for '*{query}*'. Did you mean:\n\n"
                )

                # Create keyboard with similar terms
                keyboard = []
                for term in similar_terms:
                    keyboard.append(
                        [InlineKeyboardButton(term, callback_data=f"term_{term}")]
                    )

                keyboard.append(
                    [InlineKeyboardButton("Show All Terms", callback_data="term_all")]
                )
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    text, reply_markup=reply_markup, parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"I couldn't find an explanation for '*{query}*'. "
                    f"Try using /game_guide without any terms to see all available explanations.",
                    parse_mode="Markdown",
                )
    else:
        # No specific term, show main guide with categories
        main_guide_text = (
            "🏏 *GullyGuru Game Guide* 🏏\n\n"
            "Welcome to GullyGuru! This guide will help you understand the game terminology and concepts.\n\n"
            "Select a category to learn more:"
        )

        # Create keyboard with categories
        keyboard = [
            [InlineKeyboardButton("What is a Gully?", callback_data="term_gully")],
            [InlineKeyboardButton("Teams & Players", callback_data="category_teams")],
            [
                InlineKeyboardButton(
                    "Auctions & Transfers", callback_data="category_auctions"
                )
            ],
            [InlineKeyboardButton("Scoring System", callback_data="category_scoring")],
            [
                InlineKeyboardButton(
                    "Matches & Predictions", callback_data="category_matches"
                )
            ],
            [
                InlineKeyboardButton(
                    "Admin & Group Management", callback_data="category_admin"
                )
            ],
            [InlineKeyboardButton("All Terminology", callback_data="term_all")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            main_guide_text, reply_markup=reply_markup, parse_mode="Markdown"
        )


def get_term_explanation(term: str) -> str:
    """Get explanation for a specific term."""
    terms = {
        "gully": (
            "*Gully*\n\n"
            "In GullyGuru, a 'gully' represents a cricket community group or league. "
            "The term comes from 'gully cricket,' a form of street cricket played in the Indian subcontinent.\n\n"
            "*Key characteristics:*\n"
            "• A self-contained community with its own members, admins, and teams\n"
            "• Each gully can have its own rules, scoring systems, and competition formats\n"
            "• Multiple gullies can exist independently, allowing users to participate in different communities\n"
            "• Each gully is typically linked to a Telegram group for community interaction\n"
            "• All game activities, teams, and competitions exist within the context of a specific gully"
        ),
        "team": (
            "*Team*\n\n"
            "Teams are groups of users within a gully who compete together.\n\n"
            "*Key characteristics:*\n"
            "• Teams have captains who manage team composition and strategy\n"
            "• Users can belong to only one team per gully\n"
            "• Teams compete against each other in matches and tournaments\n"
            "• Team performance is tracked on leaderboards"
        ),
        "season": (
            "*Season*\n\n"
            "Seasons are time-bounded competition periods within a gully.\n\n"
            "*Key characteristics:*\n"
            "• Seasons have defined start and end dates\n"
            "• Statistics and rankings reset between seasons\n"
            "• Winners are declared at the end of each season\n"
            "• Different seasons may have different rules or formats"
        ),
        "match": (
            "*Match*\n\n"
            "Individual cricket matches between teams.\n\n"
            "*Key characteristics:*\n"
            "• Matches have specific formats, teams, and scoring rules\n"
            "• Results contribute to season standings\n"
            "• Users can make predictions about match outcomes\n"
            "• Player performance in matches earns fantasy points"
        ),
        "prediction": (
            "*Prediction*\n\n"
            "User forecasts about match outcomes.\n\n"
            "*Key characteristics:*\n"
            "• Predictions earn points based on accuracy\n"
            "• Prediction points contribute to individual and team rankings\n"
            "• Users can predict various aspects of a match (winner, score, etc.)\n"
            "• Predictions must be made before match deadlines"
        ),
        "auction": (
            "*Auction*\n\n"
            "The process of bidding for players to add to your team.\n\n"
            "*Key characteristics:*\n"
            "• Players are auctioned one by one\n"
            "• Users bid virtual currency to acquire players\n"
            "• Each user has a limited budget for auctions\n"
            "• Auctions have time limits for bidding\n"
            "• Players go to the highest bidder when time expires"
        ),
        "transfer": (
            "*Transfer*\n\n"
            "The process of adding or removing players from your team outside of auctions.\n\n"
            "*Key characteristics:*\n"
            "• Transfers occur during designated transfer windows\n"
            "• Users can sell players to free up budget\n"
            "• Users can buy available players within their budget\n"
            "• Transfer limits may apply per window\n"
            "• Player values may change based on performance"
        ),
        "captain": (
            "*Captain*\n\n"
            "The player designated as the leader of your fantasy team.\n\n"
            "*Key characteristics:*\n"
            "• Captain's points are multiplied (typically 2×)\n"
            "• Only one captain can be designated per match\n"
            "• Captain can be changed before each match\n"
            "• Strategic captain selection is crucial for maximizing points"
        ),
        "vice-captain": (
            "*Vice-Captain*\n\n"
            "The secondary leader of your fantasy team.\n\n"
            "*Key characteristics:*\n"
            "• Vice-captain's points are multiplied (typically 1.5×)\n"
            "• Only one vice-captain can be designated per match\n"
            "• Vice-captain can be changed before each match\n"
            "• Provides a backup scoring boost if captain underperforms"
        ),
        "playing xi": (
            "*Playing XI*\n\n"
            "The 11 players from your squad selected to earn points in a match.\n\n"
            "*Key characteristics:*\n"
            "• Only players in your Playing XI earn points\n"
            "• Must be selected before match deadline\n"
            "• Must follow team composition rules (e.g., max players per team)\n"
            "• Includes captain and vice-captain designations"
        ),
        "budget": (
            "*Budget*\n\n"
            "The virtual currency available to spend on players.\n\n"
            "*Key characteristics:*\n"
            "• Each user starts with the same budget\n"
            "• Budget is spent during auctions and transfers\n"
            "• Selling players returns funds to your budget\n"
            "• Budget management is a key strategic element"
        ),
        "points": (
            "*Points*\n\n"
            "Fantasy points earned based on real player performances.\n\n"
            "*Key characteristics:*\n"
            "• Points are awarded for various cricket actions (runs, wickets, catches, etc.)\n"
            "• Only Playing XI players earn points\n"
            "• Captain and vice-captain points are multiplied\n"
            "• Total points determine rankings on leaderboards"
        ),
        "leaderboard": (
            "*Leaderboard*\n\n"
            "Rankings of users or teams based on fantasy points.\n\n"
            "*Key characteristics:*\n"
            "• Shows current standings in the competition\n"
            "• Updated after each match\n"
            "• May include daily, weekly, and season-long rankings\n"
            "• Tie-breakers apply for users with equal points"
        ),
        "admin": (
            "*Admin*\n\n"
            "Users with special permissions to manage a gully.\n\n"
            "*Key characteristics:*\n"
            "• Can configure gully settings\n"
            "• Can manage users and teams\n"
            "• Can create and manage auctions\n"
            "• Can set up matches and tournaments\n"
            "• Can make administrative announcements"
        ),
    }

    return terms.get(term.lower(), "")


def get_similar_terms(query: str) -> list:
    """Get terms similar to the query."""
    all_terms = list(get_all_terms().keys())
    return [term for term in all_terms if query in term or term in query]


def get_all_terms() -> dict:
    """Get all available terms and their explanations."""
    all_terms = {}

    # Add all individual terms
    for term in [
        "gully",
        "team",
        "season",
        "match",
        "prediction",
        "auction",
        "transfer",
        "captain",
        "vice-captain",
        "playing xi",
        "budget",
        "points",
        "leaderboard",
        "admin",
    ]:
        all_terms[term] = get_term_explanation(term)

    return all_terms


def get_category_terms(category: str) -> dict:
    """Get terms for a specific category."""
    categories = {
        "teams": ["team", "captain", "vice-captain", "playing xi"],
        "auctions": ["auction", "transfer", "budget"],
        "scoring": ["points", "leaderboard"],
        "matches": ["match", "prediction", "season"],
        "admin": ["admin", "gully"],
    }

    category_terms = {}
    for term in categories.get(category, []):
        category_terms[term] = get_term_explanation(term)

    return category_terms


async def handle_term_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callbacks for term explanations."""
    query = update.callback_query
    await query.answer()

    # Extract the term or category from the callback data
    callback_data = query.data

    if callback_data == "term_all":
        # Show all terms
        all_terms = get_all_terms()
        text = "*GullyGuru Terminology*\n\n"
        text += "Here are all the terms you can learn about. Use /game_guide [term] to get detailed information:\n\n"
        text += "• " + "\n• ".join(sorted(all_terms.keys()))

        await query.edit_message_text(text=text, parse_mode="Markdown")
    elif callback_data.startswith("term_"):
        # Show specific term
        term = callback_data[5:]  # Remove "term_" prefix
        explanation = get_term_explanation(term)

        if explanation:
            # Add back button
            keyboard = [
                [InlineKeyboardButton("« Back to Guide", callback_data="term_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text=explanation, reply_markup=reply_markup, parse_mode="Markdown"
            )
    elif callback_data.startswith("category_"):
        # Show terms in category
        category = callback_data[9:]  # Remove "category_" prefix
        category_terms = get_category_terms(category)

        text = f"*{category.capitalize()} Terminology*\n\n"
        text += "Select a term to learn more:\n"

        # Create keyboard with terms in this category
        keyboard = []
        for term in sorted(category_terms.keys()):
            keyboard.append(
                [InlineKeyboardButton(term.capitalize(), callback_data=f"term_{term}")]
            )

        keyboard.append(
            [InlineKeyboardButton("« Back to Guide", callback_data="term_back")]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    elif callback_data == "term_back":
        # Go back to main guide
        await game_guide_command(update, context)
