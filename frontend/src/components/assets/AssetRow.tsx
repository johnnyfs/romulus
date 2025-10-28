import React from "react";
import { AssetImage } from "./AssetImage";
import type { AssetCreateResponse } from "../../client";

interface AssetRowProps {
  asset: AssetCreateResponse;
  onClick?: (asset: AssetCreateResponse) => void;
}

export const AssetRow: React.FC<AssetRowProps> = ({ asset, onClick }) => {
  const filename = asset.storage_key.split("/").pop() || "unknown";
  const isProcessed = asset.asset_data.processed;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "16px",
        padding: "12px",
        border: "1px solid #ddd",
        borderRadius: "4px",
        backgroundColor: isProcessed ? "#f9f9f9" : "#fff",
        cursor: onClick ? "pointer" : "default",
        transition: "background-color 0.2s",
      }}
      onClick={() => onClick?.(asset)}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.backgroundColor = isProcessed ? "#f0f0f0" : "#f9f9f9";
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = isProcessed ? "#f9f9f9" : "#fff";
      }}
    >
      <AssetImage url={asset.download_url} alt={filename} size={64} />

      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: "14px",
            fontWeight: "500",
            color: "#333",
            marginBottom: "4px",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {filename}
        </div>
        <div style={{ fontSize: "12px", color: "#666" }}>
          {asset.asset_data.image_type} • {asset.asset_data.tags.join(", ") || "no tags"}
        </div>
      </div>

      {isProcessed && (
        <div
          style={{
            fontSize: "11px",
            padding: "4px 8px",
            backgroundColor: "#28a745",
            color: "white",
            borderRadius: "3px",
            fontWeight: "500",
          }}
        >
          Processed
        </div>
      )}
    </div>
  );
};
