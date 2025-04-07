import { useEffect, useRef, useState } from "react";

type WebSocketMessage = {
  data: string;
  type: string;
  target: WebSocket;
};

export function useWebSocket(url: string) {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Convert relative URL to absolute WebSocket URL
    const wsUrl = url.startsWith("ws")
      ? url
      : `ws://${window.location.host}${url}`;

    // Create WebSocket connection
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    // Connection opened
    ws.addEventListener("open", () => {
      setReadyState(WebSocket.OPEN);
    });

    // Listen for messages
    ws.addEventListener("message", (event) => {
      const message = {
        data: event.data,
        type: event.type,
        target: event.target as WebSocket,
      };
      setLastMessage(message);
    });

    // Connection closed
    ws.addEventListener("close", () => {
      setReadyState(WebSocket.CLOSED);
    });

    // Connection error
    ws.addEventListener("error", (error) => {
      console.error("WebSocket error:", error);
      setReadyState(WebSocket.CLOSED);
    });

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  // Function to send messages
  const sendMessage = (data: string | object) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        typeof data === "string" ? data : JSON.stringify(data)
      );
    }
  };

  return {
    lastMessage,
    readyState,
    sendMessage,
  };
}
