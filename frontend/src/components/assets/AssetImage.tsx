import React, { useState } from "react";

interface AssetImageProps {
  url: string;
  alt: string;
  size?: number;
}

export const AssetImage: React.FC<AssetImageProps> = ({ url, alt, size = 64 }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  return (
    <div
      style={{
        width: size,
        height: size,
        backgroundColor: loading ? "#e0e0e0" : error ? "#fee" : "transparent",
        border: "1px solid #ddd",
        borderRadius: "4px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        flexShrink: 0,
      }}
    >
      {loading && !error && (
        <div style={{ fontSize: "12px", color: "#666" }}>Loading...</div>
      )}
      {error && (
        <div style={{ fontSize: "10px", color: "#c00", textAlign: "center", padding: "4px" }}>
          Failed to load
        </div>
      )}
      <img
        src={url}
        alt={alt}
        style={{
          maxWidth: "100%",
          maxHeight: "100%",
          objectFit: "contain",
          display: loading || error ? "none" : "block",
        }}
        onLoad={() => setLoading(false)}
        onError={() => {
          setLoading(false);
          setError(true);
        }}
      />
    </div>
  );
};
