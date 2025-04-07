import { useEffect, useRef, useState } from "react";

type WebSocketMessage = {
  data: string;
  type: string;
  target: WebSocket;
};

export function useWebSocket(url: string) {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!url) {
      setError(new Error("WebSocket URL is required"));
      return;
    }

    try {
      // Convert relative URL to absolute WebSocket URL
      const wsUrl = url.startsWith("ws")
        ? url
        : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${
            window.location.host
          }${url}`;

      // Log connection attempt in development
      if (process.env.NODE_ENV === "development") {
        console.info(`Attempting WebSocket connection to: ${wsUrl}`);
      }

      // Create WebSocket connection
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      // Connection opened
      ws.addEventListener("open", () => {
        setReadyState(WebSocket.OPEN);
        setError(null);
        console.info(`WebSocket connected to ${wsUrl}`);
      });

      // Listen for messages
      ws.addEventListener("message", (event) => {
        try {
          const message = {
            data: event.data,
            type: event.type,
            target: event.target as WebSocket,
          };
          setLastMessage(message);
        } catch (err) {
          console.warn("Error parsing WebSocket message:", err);
        }
      });

      // Connection closed
      ws.addEventListener("close", (event) => {
        setReadyState(WebSocket.CLOSED);
        if (!event.wasClean) {
          const closeError = new Error(
            `WebSocket connection closed unexpectedly. Code: ${event.code}`
          );
          setError(closeError);

          // In development, log as a warning rather than error since this might be expected
          if (process.env.NODE_ENV === "development") {
            console.warn(`WebSocket closed unexpectedly: ${wsUrl}`, {
              code: event.code,
              reason: event.reason || "No reason provided",
              wasClean: event.wasClean,
            });
          }
        } else {
          console.info(
            `WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`
          );
        }
      });

      // Connection error
      ws.addEventListener("error", (event) => {
        const errorMessage = "WebSocket connection error";
        setError(new Error(errorMessage));
        setReadyState(WebSocket.CLOSED);

        // In development, log as a warning rather than error to reduce console noise
        if (process.env.NODE_ENV === "development") {
          console.warn("WebSocket connection failed", {
            url: wsUrl,
            readyState: ws.readyState,
            message:
              "This is expected if there's no WebSocket server implemented.",
          });
        } else {
          console.error("WebSocket error:", {
            url: wsUrl,
            readyState: ws.readyState,
          });
        }
      });

      // Cleanup on unmount
      return () => {
        if (wsRef.current) {
          // Close code 1000 indicates normal closure
          wsRef.current.close(1000, "Component unmounted");
        }
      };
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error("Failed to create WebSocket connection");
      console.error("WebSocket initialization error:", error);
      setError(error);
      return () => {}; // Empty cleanup function
    }
  }, [url]);

  // Function to send messages
  const sendMessage = (data: string | object) => {
    if (!wsRef.current) {
      setError(new Error("WebSocket is not connected"));
      return false;
    }

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      setError(
        new Error(
          `WebSocket is not open (readyState: ${wsRef.current.readyState})`
        )
      );
      return false;
    }

    try {
      wsRef.current.send(
        typeof data === "string" ? data : JSON.stringify(data)
      );
      return true;
    } catch (err) {
      const error =
        err instanceof Error ? err : new Error("Failed to send message");
      setError(error);
      return false;
    }
  };

  // Add a reconnect function
  const reconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setReadyState(WebSocket.CONNECTING);
    setError(null);
  };

  return {
    lastMessage,
    readyState,
    sendMessage,
    reconnect,
    error,
    isConnecting: readyState === WebSocket.CONNECTING,
    isConnected: readyState === WebSocket.OPEN,
    isClosed:
      readyState === WebSocket.CLOSED || readyState === WebSocket.CLOSING,
  };
}
