import React, { useState, useEffect } from 'react';
import JsonView from '@uiw/react-json-view';
import { githubDarkTheme } from '@uiw/react-json-view/githubDark';

function WebSocketDebugger() {
  const [jsonData, setJsonData] = useState(null);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/simulation/ws");

    socket.onopen = () => {
      console.log("[open] WebSocket connection established");
    };

    socket.onmessage = (event) => {
      console.log(`[message] Data received from server: ${event.data}`);
      try {
        const parsedData = JSON.parse(event.data);
        setJsonData(parsedData);
      } catch (error) {
        console.error("Error parsing JSON:", error);
      }
    };

    socket.onclose = (event) => {
      if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
      } else {
        console.error('[close] Connection died');
      }
    };

    socket.onerror = (error) => {
      console.error(`[error] ${error.message}`);
    };

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  return (
    <div
      style={{
        backgroundColor: "#1e1e1e",
        color: "#ccc",
        padding: "1rem",
        minHeight: "100vh",
        fontFamily: "monospace",
      }}
    >
      <h1 style={{ color: "#fff", marginBottom: "1rem" }}>WebSocket JSON Data</h1>
      {jsonData ? (
        <JsonView
          value={jsonData}
          style={githubDarkTheme}
          displayDataTypes={false}
          indentWidth={3}
        />
      ) : (
        <p style={{ color: "#aaa" }}>Waiting for WebSocket data...</p>
      )}
    </div>
  );
}

export default WebSocketDebugger;
