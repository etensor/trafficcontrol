import React from 'react';

const MatrixJSONViewer = ({ data, level = 0 }) => {
  const containerStyle = {
    marginLeft: level * 16,
    fontFamily: 'monospace',
    color: '#00FF41', // Matrix green
    whiteSpace: 'pre-wrap',
  };

  if (typeof data !== 'object' || data === null) {
    return <span style={containerStyle}>{String(data)}</span>;
  }

  return (
    <div style={containerStyle}>
      {Array.isArray(data) ? (
        data.map((item, index) => (
          <div key={index}>
            <span style={{ color: '#00FF41' }}>[{index}]: </span>
            <MatrixJSONViewer data={item} level={level + 1} />
          </div>
        ))
      ) : (
        Object.entries(data).map(([key, value]) => (
          <div key={key}>
            <span style={{ color: '#00FF41', fontWeight: 'bold' }}>{key}: </span>
            <MatrixJSONViewer data={value} level={level + 1} />
          </div>
        ))
      )}
    </div>
  );
};

export default MatrixJSONViewer;
