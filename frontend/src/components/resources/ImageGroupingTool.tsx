import React, { useState, useRef, useEffect } from "react";
import { ResourcesService, ImageType, ImageState, ImageTag } from "../../client";

interface Group {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  imageType: ImageType;
  tags: ImageTag[];
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
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0, status: '' });

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
  }, [groups, selectedGroupId, currentDraw, imageDimensions, scale, showGrid]);

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
        name: `Group ${groups.length + 1}`,
        ...currentDraw,
        imageType: ImageType.SPRITE, // Default to sprite
        tags: [],
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
      name: `Group ${groups.length + 1}`,
      x: snapToPixel((imageDimensions.width - size) / 2),
      y: snapToPixel((imageDimensions.height - size) / 2),
      width: snapToPixel(size),
      height: snapToPixel(size),
      imageType: ImageType.SPRITE, // Default to sprite
      tags: [],
    };

    setGroups([...groups, newGroup]);
    setSelectedGroupId(newGroup.id);
  };

  const handleSelectAll = () => {
    if (!imageDimensions) return;

    const newGroup: Group = {
      id: `group-${Date.now()}`,
      name: 'Full Image',
      x: 0,
      y: 0,
      width: imageDimensions.width,
      height: imageDimensions.height,
      imageType: ImageType.SPRITE,
      tags: [],
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

  const handleSubmit = async () => {
    if (!imageRef.current || !canvasRef.current) return;
    if (groups.length === 0) {
      console.warn('No groups to submit');
      return;
    }

    setIsUploading(true);

    try {
      setUploadProgress({ current: 0, total: groups.length, status: 'Starting...' });

      for (let i = 0; i < groups.length; i++) {
        const group = groups[i];

        setUploadProgress({
          current: i,
          total: groups.length,
          status: `Uploading ${group.name} (${i + 1}/${groups.length})...`
        });

        // Step 1: Slice the image
        const sliceCanvas = document.createElement('canvas');
        sliceCanvas.width = group.width;
        sliceCanvas.height = group.height;
        const sliceCtx = sliceCanvas.getContext('2d');

        if (!sliceCtx) continue;

        // Draw the sliced portion of the image
        sliceCtx.drawImage(
          imageRef.current,
          group.x, group.y, group.width, group.height,
          0, 0, group.width, group.height
        );

        // Step 2: Convert to blob
        const blob = await new Promise<Blob | null>((resolve) => {
          sliceCanvas.toBlob(resolve, 'image/png');
        });

        if (!blob) continue;

        // Step 3: Get upload ticket
        // Sanitize the group name for use in filename
        const safeName = group.name.replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
        const filename = `${safeName}_${group.width}x${group.height}.png`;

        const ticketResponse = await ResourcesService.getUploadTicketResourcesUploadPost({
          filename,
          resource_data: {
            type: 'image',
            state: ImageState.GROUPED,
            image_type: group.imageType,
            tags: group.tags,
            source_url: resourceId, // Reference to the original raw resource
          }
        });

        // Step 4: Upload to MinIO
        const uploadResponse = await fetch(ticketResponse.upload_url, {
          method: 'PUT',
          body: blob,
          headers: {
            'Content-Type': 'image/png',
          },
        });

        if (!uploadResponse.ok) {
          throw new Error(`Upload failed for group ${i + 1}`);
        }

        // Step 5: Finalize the resource
        await ResourcesService.createResourceResourcesPost({
          storage_key: ticketResponse.storage_key,
          resource_data: {
            type: 'image',
            state: ImageState.GROUPED,
            image_type: group.imageType,
            tags: group.tags,
            source_url: resourceId, // Reference to the original raw resource
          }
        });
      }

      // Mark the original resource as processed
      setUploadProgress({
        current: groups.length,
        total: groups.length,
        status: 'Marking original as processed...'
      });

      await ResourcesService.updateResourceResourcesResourceIdPut(resourceId, {
        resource_data: {
          type: 'image',
          state: ImageState.RAW,
          image_type: ImageType.SPRITE, // Keep original type
          processed: true,
        }
      });

      setUploadProgress({
        current: groups.length,
        total: groups.length,
        status: 'Complete!'
      });

      // Reset after a moment
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress({ current: 0, total: 0, status: '' });
      }, 2000);

    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadProgress({ current: 0, total: 0, status: `Error: ${error.message || 'Unknown error'}` });
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress({ current: 0, total: 0, status: '' });
      }, 3000);
    }
  };

  return (
    <div style={{ opacity: isProcessed ? 0.5 : 1, display: "flex", flexDirection: "column", height: "100%" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "16px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "18px" }}>Image Grouping</h3>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "14px" }}>
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
            />
            Show 8x8 Grid
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "14px" }}>
            <input
              type="checkbox"
              checked={snapToGrid}
              onChange={(e) => setSnapToGrid(e.target.checked)}
            />
            Snap to Grid
          </label>
          <div style={{ width: "1px", height: "24px", backgroundColor: "#ddd", margin: "0 4px" }} />
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
          flex: 1,
          border: "2px solid #ddd",
          borderRadius: "4px",
          padding: "20px",
          backgroundColor: "#f5f5f5",
          overflow: "auto",
          minHeight: "400px",
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
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={handleSelectAll}
              disabled={!imageDimensions}
              style={{
                padding: "6px 12px",
                fontSize: "14px",
                border: "1px solid #28a745",
                borderRadius: "4px",
                backgroundColor: "#28a745",
                color: "white",
                cursor: imageDimensions ? "pointer" : "not-allowed",
                fontWeight: "500",
              }}
            >
              Select All
            </button>
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
        </div>

        {groups.length === 0 ? (
          <div style={{ fontSize: "14px", color: "#666", fontStyle: "italic" }}>
            No groups defined. Draw on the image or click "Select All" to select the entire image, or "+ Add Group" to create a custom group.
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
                    <input
                      type="text"
                      value={group.name}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleUpdateGroup(group.id, { name: e.target.value });
                      }}
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        width: "100%",
                        fontWeight: "500",
                        marginBottom: "8px",
                        padding: "4px 8px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        fontSize: "14px",
                      }}
                      placeholder="Group name"
                    />
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
                    <div style={{ marginTop: "8px" }}>
                      <label style={{ fontSize: "11px", color: "#666", display: "block", marginBottom: "4px" }}>
                        Image Type:
                      </label>
                      <select
                        value={group.imageType}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleUpdateGroup(group.id, { imageType: e.target.value as ImageType });
                        }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          width: "100%",
                          padding: "4px",
                          border: "1px solid #ddd",
                          borderRadius: "3px",
                          fontSize: "13px",
                        }}
                      >
                        {Object.values(ImageType).map((type) => (
                          <option key={type} value={type}>
                            {type}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div style={{ marginTop: "8px" }}>
                      <label style={{ fontSize: "11px", color: "#666", display: "block", marginBottom: "4px" }}>
                        Tags:
                      </label>
                      {/* Tag pills */}
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginBottom: "6px" }}>
                        {group.tags.map((tag, idx) => (
                          <div
                            key={idx}
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "4px",
                              padding: "3px 8px",
                              backgroundColor: "#e7f3ff",
                              border: "1px solid #b3d9ff",
                              borderRadius: "12px",
                              fontSize: "11px",
                              fontWeight: "500",
                              color: "#0066cc",
                            }}
                          >
                            {tag}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                const newTags = group.tags.filter((_, i) => i !== idx);
                                handleUpdateGroup(group.id, { tags: newTags });
                              }}
                              style={{
                                border: "none",
                                background: "none",
                                cursor: "pointer",
                                padding: 0,
                                display: "flex",
                                alignItems: "center",
                                color: "#0066cc",
                                fontSize: "14px",
                                lineHeight: 1,
                              }}
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                      {/* Dropdown to add tags */}
                      <select
                        value=""
                        onChange={(e) => {
                          e.stopPropagation();
                          const newTag = e.target.value as ImageTag;
                          if (newTag && !group.tags.includes(newTag)) {
                            handleUpdateGroup(group.id, { tags: [...group.tags, newTag] });
                          }
                        }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          width: "100%",
                          padding: "4px",
                          border: "1px solid #ddd",
                          borderRadius: "3px",
                          fontSize: "11px",
                          color: "#666",
                        }}
                      >
                        <option value="">+ Add tag...</option>
                        {Object.values(ImageTag)
                          .filter(tag => !group.tags.includes(tag))
                          .map((tag) => (
                            <option key={tag} value={tag}>
                              {tag}
                            </option>
                          ))}
                      </select>
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

        {isUploading && (
          <div style={{ marginTop: "16px" }}>
            <div style={{ marginBottom: "8px", fontSize: "14px", color: "#666" }}>
              {uploadProgress.status}
            </div>
            <div style={{
              width: "100%",
              height: "24px",
              backgroundColor: "#e9ecef",
              borderRadius: "4px",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: uploadProgress.total > 0 ? `${(uploadProgress.current / uploadProgress.total) * 100}%` : "0%",
                backgroundColor: "#28a745",
                transition: "width 0.3s ease",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontSize: "12px",
                fontWeight: "600"
              }}>
                {uploadProgress.total > 0 && `${uploadProgress.current}/${uploadProgress.total}`}
              </div>
            </div>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={isProcessed || isUploading}
          style={{
            marginTop: "16px",
            width: "100%",
            padding: "10px",
            fontSize: "16px",
            fontWeight: "600",
            border: "none",
            borderRadius: "4px",
            backgroundColor: isProcessed || isUploading ? "#6c757d" : "#28a745",
            color: "white",
            cursor: isProcessed || isUploading ? "not-allowed" : "pointer",
          }}
        >
          {isProcessed ? "Already Processed" : isUploading ? "Processing..." : "Submit Groups for Processing"}
        </button>
      </div>
    </div>
  );
};
