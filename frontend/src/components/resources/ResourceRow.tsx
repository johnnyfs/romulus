import React from "react";
import { ResourceImage } from "./ResourceImage";
import type { ResourceCreateResponse } from "../../client";

interface ResourceRowProps {
  asset: ResourceCreateResponse;
  onClick?: (asset: ResourceCreateResponse) => void;
}

export const ResourceRow: React.FC<ResourceRowProps> = ({ asset, onClick }) => {
  const filename = asset.storage_key.split("/").pop() || "unknown";
  const isProcessed = asset.resource_data.processed;

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
      <ResourceImage url={asset.download_url} alt={filename} size={64} />

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
          {asset.resource_data.image_type} • {asset.resource_data.tags?.join(", ") || "no tags"}
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
