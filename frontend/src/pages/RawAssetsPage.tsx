import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { RawAssetList } from "../components/assets/RawAssetList";
import { AssetsService } from "../client";
import type { AssetCreateResponse } from "../client";

export const RawAssetsPage: React.FC = () => {
  const [assets, setAssets] = useState<AssetCreateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        // Fetch all image assets with state=raw
        const response = await AssetsService.listAssetsAssetsGet("image", "raw");
        setAssets(response);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to fetch assets");
        setLoading(false);
      }
    };

    fetchAssets();
  }, []);

  return (
    <div style={{ padding: "20px", maxWidth: "1000px", margin: "0 auto" }}>
      <div style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
        <Link
          to="/"
          style={{
            padding: "8px 16px",
            backgroundColor: "#6c757d",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
            fontSize: "14px",
          }}
        >
          ← Back
        </Link>
        <h1 style={{ margin: 0, flex: 1 }}>Raw Image Assets</h1>
      </div>

      {loading && (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: "#666",
          }}
        >
          Loading assets...
        </div>
      )}

      {error && (
        <div
          style={{
            color: "red",
            padding: "10px",
            border: "1px solid red",
            borderRadius: "4px",
            backgroundColor: "#fee",
          }}
        >
          Error: {error}
        </div>
      )}

      {!loading && !error && (
        <RawAssetList
          assets={assets}
          onAssetClick={(asset) => {
            console.log("Clicked asset:", asset);
            // TODO: Navigate to detail page when we add routing
          }}
        />
      )}
    </div>
  );
};

export default RawAssetsPage;
