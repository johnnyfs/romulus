import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ResourcesService } from "../client/services/ResourcesService";
import type { ResourceCreateResponse } from "../client";
import { ImageGroupingTool } from "../components/resources/ImageGroupingTool";

export default function ResourceDetailPage() {
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
          to="/resources/images/raw"
          style={{
            display: "inline-block",
            marginTop: "20px",
            color: "#007bff",
            textDecoration: "none",
          }}
        >
          ← Back to Resources
        </Link>
      </div>
    );
  }

  const filename = resource.storage_key.split("/").pop() || "unknown";
  const isProcessed = resource.resource_data.processed ?? false;

  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      <div style={{ marginBottom: "20px", display: "flex", justifyContent: "space-between" }}>
        <Link
          to="/resources/images/raw"
          style={{
            color: "#007bff",
            textDecoration: "none",
            fontSize: "14px",
          }}
        >
          ← Back to Resources
        </Link>
        <Link
          to="/resources/images/grouped"
          style={{
            color: "#007bff",
            textDecoration: "none",
            fontSize: "14px",
          }}
        >
          Forward to Grouped →
        </Link>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "24px" }}>{filename}</h1>
        {isProcessed && (
          <div
            style={{
              fontSize: "12px",
              padding: "6px 12px",
              backgroundColor: "#28a745",
              color: "white",
              borderRadius: "4px",
              fontWeight: "500",
            }}
          >
            Processed
          </div>
        )}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "250px 1fr",
          gap: "24px",
        }}
      >
        <div>
          <div
            style={{
              padding: "16px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              backgroundColor: "#f9f9f9",
            }}
          >
            <h3 style={{ marginTop: 0, fontSize: "16px" }}>Metadata</h3>
            <div style={{ fontSize: "14px", lineHeight: "1.8" }}>
              <div>
                <strong>Type:</strong> {resource.resource_data.image_type}
              </div>
              <div>
                <strong>State:</strong> {resource.resource_data.state}
              </div>
              <div>
                <strong>Tags:</strong>{" "}
                {resource.resource_data.tags?.join(", ") || "none"}
              </div>
              {resource.resource_data.source_url && (
                <div>
                  <strong>Source:</strong>{" "}
                  <a
                    href={resource.resource_data.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#007bff", wordBreak: "break-all" }}
                  >
                    {resource.resource_data.source_url}
                  </a>
                </div>
              )}
              {resource.resource_data.license && (
                <div>
                  <strong>License:</strong> {resource.resource_data.license}
                </div>
              )}
            </div>
          </div>
        </div>

        <div>
          <ImageGroupingTool
            imageUrl={resource.download_url}
            resourceId={resource.id}
            isProcessed={isProcessed}
          />
        </div>
      </div>
    </div>
  );
}
