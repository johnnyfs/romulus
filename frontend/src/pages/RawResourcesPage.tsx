import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { RawResourceList } from "../components/resources/RawResourceList";
import { ResourcesService, ResourceType, ImageState } from "../client";
import type { ResourceCreateResponse } from "../client";

export const RawResourcesPage: React.FC = () => {
  const [resources, setResources] = useState<ResourceCreateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResources = async () => {
      try {
        // Fetch all image resources with state=raw
        const response = await ResourcesService.listResourcesResourcesGet(ResourceType.IMAGE, ImageState.RAW);
        setResources(response);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to fetch resources");
        setLoading(false);
      }
    };

    fetchResources();
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
        <h1 style={{ margin: 0, flex: 1 }}>Raw Image Resources</h1>
      </div>

      {loading && (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: "#666",
          }}
        >
          Loading resources...
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
        <RawResourceList
          resources={resources}
          onResourceClick={(resource) => {
            console.log("Clicked resource:", resource);
            // TODO: Navigate to detail page when we add routing
          }}
        />
      )}
    </div>
  );
};

export default RawResourcesPage;
