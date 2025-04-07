import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);

    if (!session) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    // TODO: In a real app, fetch these settings from your database
    // For now, we'll return mock data
    return NextResponse.json({
      settings: {
        emailNotifications: true,
        telegramNotifications: false,
        telegramChatId: process.env.DEFAULT_TELEGRAM_CHAT_ID || "",
        theme: "system",
        publicProfile: true,
        showStats: true,
        language: "en",
      },
    });
  } catch (error) {
    console.error("Error fetching settings:", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const settings = await request.json();

    // Validate settings
    const requiredFields = [
      "emailNotifications",
      "telegramNotifications",
      "telegramChatId",
      "theme",
      "publicProfile",
      "showStats",
    ];

    const missingFields = requiredFields.filter(
      (field) => settings[field] === undefined
    );

    if (missingFields.length > 0) {
      return new NextResponse(
        `Missing required fields: ${missingFields.join(", ")}`,
        { status: 400 }
      );
    }

    // Validate theme value
    const validThemes = ["light", "dark", "system"];
    if (!validThemes.includes(settings.theme)) {
      return new NextResponse("Invalid theme value", { status: 400 });
    }

    // Validate Telegram chat ID if notifications are enabled
    if (settings.telegramNotifications && !settings.telegramChatId) {
      return new NextResponse(
        "Telegram chat ID is required when notifications are enabled",
        { status: 400 }
      );
    }

    // TODO: In a real app, save these settings to your database
    // For now, we'll just return success

    return NextResponse.json({
      message: "Settings updated successfully",
      settings,
    });
  } catch (error) {
    console.error("Error updating settings:", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
