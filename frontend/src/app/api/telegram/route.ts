import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";
import { TelegramService } from "@/lib/services/telegram";

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const { action, chatId } = await request.json();

    switch (action) {
      case "test":
        const success = await TelegramService.testConnection(chatId);
        return NextResponse.json({ success });

      case "validate":
        const isValid = await TelegramService.validateChatId(chatId);
        return NextResponse.json({ isValid });

      default:
        return new NextResponse("Invalid action", { status: 400 });
    }
  } catch (error) {
    console.error("Error in Telegram API:", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
