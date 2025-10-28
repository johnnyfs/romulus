import React from "react";
import { AssetRow } from "./AssetRow";
import type { AssetCreateResponse } from "../../client";

interface RawAssetListProps {
  assets: AssetCreateResponse[];
  onAssetClick?: (asset: AssetCreateResponse) => void;
}

export const RawAssetList: React.FC<RawAssetListProps> = ({ assets, onAssetClick }) => {
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
  const unprocessedAssets = assets.filter((a) => !a.asset_data.processed);
  const processedAssets = assets.filter((a) => a.asset_data.processed);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {unprocessedAssets.length > 0 && (
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
            Unprocessed ({unprocessedAssets.length})
          </div>
          {unprocessedAssets.map((asset) => (
            <AssetRow key={asset.id} asset={asset} onClick={onAssetClick} />
          ))}
        </>
      )}

      {processedAssets.length > 0 && (
        <>
          <div
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "#666",
              textTransform: "uppercase",
              marginTop: unprocessedAssets.length > 0 ? "24px" : "8px",
              marginBottom: "4px",
            }}
          >
            Processed ({processedAssets.length})
          </div>
          {processedAssets.map((asset) => (
            <AssetRow key={asset.id} asset={asset} onClick={onAssetClick} />
          ))}
        </>
      )}
    </div>
  );
};
