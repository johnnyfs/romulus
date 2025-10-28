import React from "react";
import { ResourceRow } from "./ResourceRow";
import type { ResourceCreateResponse } from "../../client";

interface RawResourceListProps {
  assets: ResourceCreateResponse[];
  onResourceClick?: (asset: ResourceCreateResponse) => void;
}

export const RawResourceList: React.FC<RawResourceListProps> = ({ assets, onResourceClick }) => {
  if (assets.length === 0) {
    return (
      <div
        style={{
          padding: "40px",
          textAlign: "center",
          color: "#666",
          border: "1px dashed #ddd",
          borderRadius: "4px",
        }}
      >
        No raw assets found. Upload some assets to get started!
      </div>
    );
  }

  // Separate unprocessed and processed assets (already sorted by API)
  const unprocessedResources = assets.filter((a) => !a.asset_data.processed);
  const processedResources = assets.filter((a) => a.asset_data.processed);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {unprocessedResources.length > 0 && (
        <>
          <div
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "#666",
              textTransform: "uppercase",
              marginTop: "8px",
              marginBottom: "4px",
            }}
          >
            Unprocessed ({unprocessedResources.length})
          </div>
          {unprocessedResources.map((asset) => (
            <ResourceRow key={asset.id} asset={asset} onClick={onResourceClick} />
          ))}
        </>
      )}

      {processedResources.length > 0 && (
        <>
          <div
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "#666",
              textTransform: "uppercase",
              marginTop: unprocessedResources.length > 0 ? "24px" : "8px",
              marginBottom: "4px",
            }}
          >
            Processed ({processedResources.length})
          </div>
          {processedResources.map((asset) => (
            <ResourceRow key={asset.id} asset={asset} onClick={onResourceClick} />
          ))}
        </>
      )}
    </div>
  );
};
