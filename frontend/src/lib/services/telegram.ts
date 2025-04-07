export class TelegramService {
  private static readonly BASE_URL = "https://api.telegram.org/bot";
  private static readonly botToken = process.env.NEXT_PUBLIC_TELEGRAM_BOT_TOKEN;

  /**
   * Validates a Telegram chat ID by attempting to send a test message
   */
  static async validateChatId(chatId: string | number): Promise<boolean> {
    try {
      // In development mode, always return true
      if (process.env.NODE_ENV === "development") {
        console.log("Development mode: Skipping Telegram validation");
        return true;
      }

      const response = await fetch(`${this.BASE_URL}${this.botToken}/getChat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          chat_id: chatId,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error("Telegram validation error:", error);
        return false;
      }

      return true;
    } catch (error) {
      console.error("Error validating Telegram chat ID:", error);
      return false;
    }
  }

  /**
   * Sends a message to a specific Telegram chat
   */
  static async sendMessage(
    chatId: string | number,
    message: string
  ): Promise<boolean> {
    try {
      // In development mode, just log the message
      if (process.env.NODE_ENV === "development") {
        console.log("Development mode: Would send Telegram message:", {
          chatId,
          message,
        });
        return true;
      }

      const response = await fetch(
        `${this.BASE_URL}${this.botToken}/sendMessage`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            chat_id: chatId,
            text: message,
            parse_mode: "HTML",
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.description || "Failed to send Telegram message");
      }

      return true;
    } catch (error) {
      console.error("Error sending Telegram message:", error);
      return false;
    }
  }

  /**
   * Tests the Telegram connection by sending a test message
   */
  static async testConnection(chatId: string | number): Promise<boolean> {
    const testMessage = `🎯 GullyGuru Test Message\n\nYour Telegram notifications are working correctly! You will receive updates about:\n\n• Match schedules\n• Team updates\n• Score updates\n• Important announcements`;
    return this.sendMessage(chatId, testMessage);
  }
}
