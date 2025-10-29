import React, { useState, useRef, useEffect } from "react";

interface Group {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ImageGroupingToolProps {
  imageUrl: string;
  resourceId: string;
  isProcessed: boolean;
}

type DragMode = 'none' | 'draw' | 'move' | 'resize-tl' | 'resize-tr' | 'resize-bl' | 'resize-br';

export const ImageGroupingTool: React.FC<ImageGroupingToolProps> = ({
  imageUrl,
  resourceId,
  isProcessed,
}) => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [dragMode, setDragMode] = useState<DragMode>('none');
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [draggedGroupStart, setDraggedGroupStart] = useState<Group | null>(null);
  const [currentDraw, setCurrentDraw] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(null);
  const [scale, setScale] = useState(1);
  const [showGrid, setShowGrid] = useState(false);
  const [snapToGrid, setSnapToGrid] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const GRID_SIZE = 8; // 8x8 pixel grid

  // Load the image and get its dimensions
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      setImageDimensions({ width: img.width, height: img.height });
      imageRef.current = img;

      // Calculate initial scale to fit in container
      if (containerRef.current) {
        const maxWidth = containerRef.current.clientWidth - 40;
        const maxHeight = 600;
        const scaleX = maxWidth / img.width;
        const scaleY = maxHeight / img.height;
        setScale(Math.min(scaleX, scaleY, 2)); // Cap at 2x zoom
      }
    };
    img.src = imageUrl;
  }, [imageUrl]);

  // Draw on canvas
  useEffect(() => {
    if (!canvasRef.current || !imageRef.current || !imageDimensions) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    canvas.width = imageDimensions.width;
    canvas.height = imageDimensions.height;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw image
    ctx.drawImage(imageRef.current, 0, 0);

    // Draw 8x8 grid when enabled
    if (showGrid) {
      ctx.strokeStyle = "rgba(0, 123, 255, 0.3)";
      ctx.lineWidth = 1 / scale;

      for (let x = 0; x <= imageDimensions.width; x += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, imageDimensions.height);
        ctx.stroke();
      }

      for (let y = 0; y <= imageDimensions.height; y += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(imageDimensions.width, y);
        ctx.stroke();
      }
    }

    // Draw pixel grid (only when zoomed in and 8x8 grid not shown)
    if (!showGrid && scale > 1.5) {
      ctx.strokeStyle = "rgba(150, 150, 150, 0.2)";
      ctx.lineWidth = 1 / scale;

      for (let x = 0; x <= imageDimensions.width; x++) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, imageDimensions.height);
        ctx.stroke();
      }

      for (let y = 0; y <= imageDimensions.height; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(imageDimensions.width, y);
        ctx.stroke();
      }
    }

    // Draw existing groups
    groups.forEach((group) => {
      const isSelected = group.id === selectedGroupId;

      // Draw group rectangle
      ctx.strokeStyle = isSelected ? "#007bff" : "#28a745";
      ctx.lineWidth = 2 / scale;
      ctx.strokeRect(group.x, group.y, group.width, group.height);

      // Draw semi-transparent fill
      ctx.fillStyle = isSelected ? "rgba(0, 123, 255, 0.1)" : "rgba(40, 167, 69, 0.1)";
      ctx.fillRect(group.x, group.y, group.width, group.height);

      // Draw resize handles for selected group
      if (isSelected) {
        const handleSize = 6 / scale;
        ctx.fillStyle = "#007bff";

        // Corner handles
        ctx.fillRect(group.x - handleSize / 2, group.y - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(group.x + group.width - handleSize / 2, group.y - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(group.x - handleSize / 2, group.y + group.height - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(group.x + group.width - handleSize / 2, group.y + group.height - handleSize / 2, handleSize, handleSize);
      }
    });

    // Draw current drawing
    if (currentDraw) {
      ctx.strokeStyle = "#ff6b6b";
      ctx.lineWidth = 2 / scale;
      ctx.setLineDash([4 / scale, 4 / scale]);
      ctx.strokeRect(currentDraw.x, currentDraw.y, currentDraw.width, currentDraw.height);
      ctx.setLineDash([]);

      ctx.fillStyle = "rgba(255, 107, 107, 0.1)";
      ctx.fillRect(currentDraw.x, currentDraw.y, currentDraw.width, currentDraw.height);
    }
  }, [groups, selectedGroupId, currentDraw, imageDimensions, scale]);

  const snapToPixel = (value: number): number => {
    if (snapToGrid) {
      return Math.round(value / GRID_SIZE) * GRID_SIZE;
    }
    return Math.round(value);
  };

  const getCanvasCoordinates = (clientX: number, clientY: number): { x: number; y: number } => {
    if (!canvasRef.current) return { x: 0, y: 0 };

    const rect = canvasRef.current.getBoundingClientRect();
    const x = (clientX - rect.left) / scale;
    const y = (clientY - rect.top) / scale;

    return {
      x: snapToPixel(x),
      y: snapToPixel(y),
    };
  };

  const getHandleAtPosition = (coords: { x: number; y: number }, group: Group): DragMode => {
    const handleSize = 6 / scale;
    const tolerance = handleSize * 2; // Make handles easier to click

    // Check corners
    if (Math.abs(coords.x - group.x) <= tolerance && Math.abs(coords.y - group.y) <= tolerance) {
      return 'resize-tl';
    }
    if (Math.abs(coords.x - (group.x + group.width)) <= tolerance && Math.abs(coords.y - group.y) <= tolerance) {
      return 'resize-tr';
    }
    if (Math.abs(coords.x - group.x) <= tolerance && Math.abs(coords.y - (group.y + group.height)) <= tolerance) {
      return 'resize-bl';
    }
    if (Math.abs(coords.x - (group.x + group.width)) <= tolerance && Math.abs(coords.y - (group.y + group.height)) <= tolerance) {
      return 'resize-br';
    }

    return 'none';
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const coords = getCanvasCoordinates(e.clientX, e.clientY);

    // Check if clicking on the selected group's handles
    if (selectedGroupId) {
      const selectedGroup = groups.find(g => g.id === selectedGroupId);
      if (selectedGroup) {
        const handleMode = getHandleAtPosition(coords, selectedGroup);
        if (handleMode !== 'none') {
          setDragMode(handleMode);
          setDragStart(coords);
          setDraggedGroupStart({ ...selectedGroup });
          return;
        }
      }
    }

    // Check if clicking inside an existing group
    const clickedGroup = groups.find(
      (g) =>
        coords.x >= g.x &&
        coords.x <= g.x + g.width &&
        coords.y >= g.y &&
        coords.y <= g.y + g.height
    );

    if (clickedGroup) {
      setSelectedGroupId(clickedGroup.id);
      setDragMode('move');
      setDragStart(coords);
      setDraggedGroupStart({ ...clickedGroup });
      return;
    }

    // Start drawing new group
    setSelectedGroupId(null);
    setDragMode('draw');
    setDragStart(coords);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!dragStart || dragMode === 'none') return;

    const coords = getCanvasCoordinates(e.clientX, e.clientY);
    const dx = coords.x - dragStart.x;
    const dy = coords.y - dragStart.y;

    if (dragMode === 'draw') {
      const x = Math.min(dragStart.x, coords.x);
      const y = Math.min(dragStart.y, coords.y);
      const width = Math.abs(coords.x - dragStart.x);
      const height = Math.abs(coords.y - dragStart.y);
      setCurrentDraw({ x, y, width, height });
    } else if (dragMode === 'move' && selectedGroupId && draggedGroupStart) {
      setGroups(groups.map(g =>
        g.id === selectedGroupId
          ? { ...g, x: snapToPixel(draggedGroupStart.x + dx), y: snapToPixel(draggedGroupStart.y + dy) }
          : g
      ));
    } else if (dragMode.startsWith('resize-') && selectedGroupId && draggedGroupStart) {
      setGroups(groups.map(g => {
        if (g.id !== selectedGroupId) return g;

        let newX = draggedGroupStart.x;
        let newY = draggedGroupStart.y;
        let newWidth = draggedGroupStart.width;
        let newHeight = draggedGroupStart.height;

        if (dragMode === 'resize-tl') {
          newX = snapToPixel(draggedGroupStart.x + dx);
          newY = snapToPixel(draggedGroupStart.y + dy);
          newWidth = snapToPixel(draggedGroupStart.width - dx);
          newHeight = snapToPixel(draggedGroupStart.height - dy);
        } else if (dragMode === 'resize-tr') {
          newY = snapToPixel(draggedGroupStart.y + dy);
          newWidth = snapToPixel(draggedGroupStart.width + dx);
          newHeight = snapToPixel(draggedGroupStart.height - dy);
        } else if (dragMode === 'resize-bl') {
          newX = snapToPixel(draggedGroupStart.x + dx);
          newWidth = snapToPixel(draggedGroupStart.width - dx);
          newHeight = snapToPixel(draggedGroupStart.height + dy);
        } else if (dragMode === 'resize-br') {
          newWidth = snapToPixel(draggedGroupStart.width + dx);
          newHeight = snapToPixel(draggedGroupStart.height + dy);
        }

        // Prevent negative dimensions
        if (newWidth < 1 || newHeight < 1) return g;

        return { ...g, x: newX, y: newY, width: newWidth, height: newHeight };
      }));
    }
  };

  const handleMouseUp = () => {
    if (dragMode === 'draw' && currentDraw && currentDraw.width > 0 && currentDraw.height > 0) {
      const newGroup: Group = {
        id: `group-${Date.now()}`,
        ...currentDraw,
      };
      setGroups([...groups, newGroup]);
      setSelectedGroupId(newGroup.id);
    }

    setDragMode('none');
    setDragStart(null);
    setDraggedGroupStart(null);
    setCurrentDraw(null);
  };

  const handleAddGroup = () => {
    if (!imageDimensions) return;

    // Add a default group in the center
    const size = Math.min(imageDimensions.width, imageDimensions.height) / 4;
    const newGroup: Group = {
      id: `group-${Date.now()}`,
      x: snapToPixel((imageDimensions.width - size) / 2),
      y: snapToPixel((imageDimensions.height - size) / 2),
      width: snapToPixel(size),
      height: snapToPixel(size),
    };

    setGroups([...groups, newGroup]);
    setSelectedGroupId(newGroup.id);
  };

  const handleDeleteGroup = (groupId: string) => {
    setGroups(groups.filter((g) => g.id !== groupId));
    if (selectedGroupId === groupId) {
      setSelectedGroupId(null);
    }
  };

  const handleUpdateGroup = (groupId: string, updates: Partial<Group>) => {
    setGroups(
      groups.map((g) =>
        g.id === groupId
          ? {
              ...g,
              ...updates,
              x: snapToPixel(updates.x ?? g.x),
              y: snapToPixel(updates.y ?? g.y),
              width: snapToPixel(updates.width ?? g.width),
              height: snapToPixel(updates.height ?? g.height),
            }
          : g
      )
    );
  };

  const handleSubmit = () => {
    // TODO: Implement submission to backend
    console.log("Submitting groups:", groups.length === 0 ? "entire image" : groups);
    alert(`Groups ready for processing:\n${groups.length === 0 ? "Entire image (no groups defined)" : `${groups.length} groups defined`}`);
  };

  return (
    <div style={{ opacity: isProcessed ? 0.5 : 1 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "16px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "18px" }}>Image Grouping</h3>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => setScale(Math.max(0.5, scale - 0.25))}
            style={{
              padding: "6px 12px",
              fontSize: "14px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              backgroundColor: "white",
              cursor: "pointer",
            }}
          >
            Zoom Out
          </button>
          <button
            onClick={() => setScale(Math.min(4, scale + 0.25))}
            style={{
              padding: "6px 12px",
              fontSize: "14px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              backgroundColor: "white",
              cursor: "pointer",
            }}
          >
            Zoom In
          </button>
          <span style={{ padding: "6px 12px", fontSize: "14px", color: "#666" }}>
            {Math.round(scale * 100)}%
          </span>
        </div>
      </div>

      <div
        ref={containerRef}
        style={{
          border: "2px solid #ddd",
          borderRadius: "4px",
          padding: "20px",
          backgroundColor: "#f5f5f5",
          overflow: "auto",
          maxHeight: "700px",
        }}
      >
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          style={{
            display: "block",
            cursor: dragMode === 'draw' ? "crosshair" : dragMode === 'move' ? "move" : dragMode.startsWith('resize-') ? "nwse-resize" : "default",
            imageRendering: scale > 2 ? "pixelated" : "auto",
            transform: `scale(${scale})`,
            transformOrigin: "top left",
          }}
        />
      </div>

      <div
        style={{
          marginTop: "16px",
          padding: "16px",
          border: "1px solid #ddd",
          borderRadius: "4px",
          backgroundColor: "#f9f9f9",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "12px",
          }}
        >
          <h4 style={{ margin: 0, fontSize: "16px" }}>
            Groups ({groups.length})
          </h4>
          <button
            onClick={handleAddGroup}
            disabled={!imageDimensions}
            style={{
              padding: "6px 12px",
              fontSize: "14px",
              border: "1px solid #007bff",
              borderRadius: "4px",
              backgroundColor: "#007bff",
              color: "white",
              cursor: imageDimensions ? "pointer" : "not-allowed",
              fontWeight: "500",
            }}
          >
            + Add Group
          </button>
        </div>

        {groups.length === 0 ? (
          <div style={{ fontSize: "14px", color: "#666", fontStyle: "italic" }}>
            No groups defined. The entire image will be processed as one group.
            <br />
            Draw on the image or click "+ Add Group" to create groups.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {groups.map((group) => (
              <div
                key={group.id}
                style={{
                  padding: "12px",
                  border: `2px solid ${group.id === selectedGroupId ? "#007bff" : "#ddd"}`,
                  borderRadius: "4px",
                  backgroundColor: "white",
                  cursor: "pointer",
                }}
                onClick={() => setSelectedGroupId(group.id)}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <div style={{ fontSize: "14px", flex: 1 }}>
                    <div style={{ fontWeight: "500", marginBottom: "8px" }}>
                      {group.id}
                    </div>
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(2, 1fr)",
                        gap: "8px",
                        fontSize: "13px",
                      }}
                    >
                      <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>X:</label>
                        <input
                          type="number"
                          value={group.x}
                          onChange={(e) =>
                            handleUpdateGroup(group.id, { x: parseInt(e.target.value) || 0 })
                          }
                          style={{
                            width: "100%",
                            padding: "4px",
                            border: "1px solid #ddd",
                            borderRadius: "3px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Y:</label>
                        <input
                          type="number"
                          value={group.y}
                          onChange={(e) =>
                            handleUpdateGroup(group.id, { y: parseInt(e.target.value) || 0 })
                          }
                          style={{
                            width: "100%",
                            padding: "4px",
                            border: "1px solid #ddd",
                            borderRadius: "3px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Width:</label>
                        <input
                          type="number"
                          value={group.width}
                          onChange={(e) =>
                            handleUpdateGroup(group.id, { width: parseInt(e.target.value) || 0 })
                          }
                          style={{
                            width: "100%",
                            padding: "4px",
                            border: "1px solid #ddd",
                            borderRadius: "3px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Height:</label>
                        <input
                          type="number"
                          value={group.height}
                          onChange={(e) =>
                            handleUpdateGroup(group.id, { height: parseInt(e.target.value) || 0 })
                          }
                          style={{
                            width: "100%",
                            padding: "4px",
                            border: "1px solid #ddd",
                            borderRadius: "3px",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteGroup(group.id);
                    }}
                    style={{
                      marginLeft: "8px",
                      padding: "4px 8px",
                      fontSize: "12px",
                      border: "1px solid #dc3545",
                      borderRadius: "3px",
                      backgroundColor: "#dc3545",
                      color: "white",
                      cursor: "pointer",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={isProcessed}
          style={{
            marginTop: "16px",
            width: "100%",
            padding: "10px",
            fontSize: "16px",
            fontWeight: "600",
            border: "none",
            borderRadius: "4px",
            backgroundColor: isProcessed ? "#6c757d" : "#28a745",
            color: "white",
            cursor: isProcessed ? "not-allowed" : "pointer",
          }}
        >
          {isProcessed ? "Already Processed" : "Submit Groups for Processing"}
        </button>
      </div>
    </div>
  );
};
