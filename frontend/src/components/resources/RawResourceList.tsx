import React from "react";
import { ResourceRow } from "./ResourceRow";
import type { ResourceCreateResponse } from "../../client";

interface RawResourceListProps {
  resources: ResourceCreateResponse[];
  onResourceClick?: (resource: ResourceCreateResponse) => void;
}

export const RawResourceList: React.FC<RawResourceListProps> = ({ resources, onResourceClick }) => {
  if (resources.length === 0) {
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
        No raw resources found. Upload some resources to get started!
      </div>
    );
  }

  // Separate unprocessed and processed resources (already sorted by API)
  const unprocessedResources = resources.filter((r) => !r.resource_data.processed);
  const processedResources = resources.filter((r) => r.resource_data.processed);

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
          {unprocessedResources.map((resource) => (
            <ResourceRow key={resource.id} asset={resource} onClick={onResourceClick} />
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
          {processedResources.map((resource) => (
            <ResourceRow key={resource.id} asset={resource} onClick={onResourceClick} />
          ))}
        </>
      )}
    </div>
  );
};
