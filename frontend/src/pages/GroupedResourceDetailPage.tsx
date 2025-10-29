import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ResourcesService } from "../client/services/ResourcesService";
import type { ResourceCreateResponse } from "../client";

export default function GroupedResourceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<ResourceCreateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResource = async () => {
      if (!id) {
        setError("No resource ID provided");
        setLoading(false);
        return;
      }

      try {
        const response = await ResourcesService.getResourceResourcesResourceIdGet(id);
        setResource(response);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to fetch resource");
        setLoading(false);
      }
    };

    fetchResource();
  }, [id]);

  if (loading) {
    return (
      <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
        <p>Loading resource...</p>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
        <div
          style={{
            color: "red",
            padding: "10px",
            border: "1px solid red",
            borderRadius: "4px",
            backgroundColor: "#fee",
          }}
        >
          Error: {error || "Resource not found"}
        </div>
        <Link
          to="/resources/images/grouped"
          style={{
            display: "inline-block",
            marginTop: "20px",
            color: "#007bff",
            textDecoration: "none",
          }}
        >
          ← Back to Grouped Resources
        </Link>
      </div>
    );
  }

  const filename = resource.storage_key.split("/").pop() || "unknown";

  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      <div style={{ marginBottom: "20px" }}>
        <Link
          to="/resources/images/grouped"
          style={{
            color: "#007bff",
            textDecoration: "none",
            fontSize: "14px",
          }}
        >
          ← Back to Grouped Resources
        </Link>
      </div>

      <h1 style={{ margin: 0, fontSize: "24px", marginBottom: "24px" }}>{filename}</h1>

      <div style={{ display: "flex", gap: "24px", alignItems: "flex-start" }}>
        {/* Image Display */}
        <div
          style={{
            flex: "0 0 auto",
            maxWidth: "600px",
            border: "1px solid #ddd",
            borderRadius: "4px",
            padding: "16px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <img
            src={resource.download_url}
            alt={filename}
            style={{
              maxWidth: "100%",
              height: "auto",
              imageRendering: "pixelated",
              display: "block",
            }}
          />
        </div>

        {/* Metadata Sidebar */}
        <div
          style={{
            flex: "1",
            padding: "16px",
            border: "1px solid #ddd",
            borderRadius: "4px",
            backgroundColor: "white",
          }}
        >
          <h2 style={{ margin: "0 0 16px 0", fontSize: "18px" }}>Resource Details</h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div>
              <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
                Name
              </label>
              <div style={{ fontSize: "14px", fontWeight: "500" }}>{filename}</div>
            </div>

            <div>
              <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
                Type
              </label>
              <div style={{ fontSize: "14px", fontWeight: "500" }}>
                {resource.resource_data.image_type || "unknown"}
              </div>
            </div>

            <div>
              <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
                State
              </label>
              <div
                style={{
                  display: "inline-block",
                  fontSize: "12px",
                  padding: "4px 8px",
                  backgroundColor: "#007bff",
                  color: "white",
                  borderRadius: "3px",
                  fontWeight: "500",
                }}
              >
                {resource.resource_data.state}
              </div>
            </div>

            {resource.resource_data.source_url && (
              <div>
                <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
                  Source
                </label>
                <Link
                  to={`/resources/images/${resource.resource_data.source_url}`}
                  style={{
                    fontSize: "14px",
                    color: "#007bff",
                    textDecoration: "none",
                  }}
                >
                  View original resource
                </Link>
              </div>
            )}

            {resource.resource_data.tags && resource.resource_data.tags.length > 0 && (
              <div>
                <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
                  Tags
                </label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                  {resource.resource_data.tags.map((tag, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: "12px",
                        padding: "4px 8px",
                        backgroundColor: "#e9ecef",
                        borderRadius: "3px",
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
