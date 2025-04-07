import React, { useState, useEffect } from 'react';
import ReactJson from 'react-json-view';

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

    // Cleanup function to close the WebSocket connection when the component unmounts
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []); // Empty dependency array ensures this effect runs only once after the initial render

  return (
    <div>
      <h1>WebSocket JSON Data</h1>
      <div style={{ width: '100%', height: '80vh', border: '1px solid lightgray', overflow: 'auto' }}>
        {jsonData && <ReactJson src={jsonData} theme="monokai" />}
        {!jsonData && <p>Waiting for WebSocket data...</p>}
      </div>
    </div>
  );
}

export default WebSocketDebugger;