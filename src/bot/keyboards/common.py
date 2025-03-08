from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_button(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """Create a keyboard with just a back button."""
    keyboard = [[InlineKeyboardButton("« Back", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    prefix: str,
    back_callback: str = "back_to_main",
    show_back: bool = True,
) -> InlineKeyboardMarkup:
    """Create a keyboard for pagination with previous and next buttons."""
    keyboard = []
    nav_row = []

    # Add previous button if not on first page
    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(
                "◀️ Previous", callback_data=f"{prefix}_page_{current_page - 1}"
            )
        )

    # Add page indicator
    nav_row.append(
        InlineKeyboardButton(
            f"Page {current_page + 1}/{total_pages}", callback_data=f"{prefix}_noop"
        )
    )

    # Add next button if not on last page
    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                "Next ▶️", callback_data=f"{prefix}_page_{current_page + 1}"
            )
        )

    keyboard.append(nav_row)

    # Add back button if requested
    if show_back:
        keyboard.append([InlineKeyboardButton("« Back", callback_data=back_callback)])

    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str = "back_to_main",
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
) -> InlineKeyboardMarkup:
    """Create a keyboard with confirm and cancel buttons."""
    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(cancel_text, callback_data=cancel_callback),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
