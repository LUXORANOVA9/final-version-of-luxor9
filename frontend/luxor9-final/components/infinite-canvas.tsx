import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { useSpatialStore } from '@/lib/spatialStore';
import { AgentWindow } from './agent-window';
import { EmpirePrompt } from './empire-prompt';

interface InfiniteCanvasProps {
  children?: React.ReactNode;
}

export const InfiniteCanvas: React.FC<<InfiniteInfiniteCanvasProps> = ({ children }) => {
  const { viewport, setViewport, agents } = useSpatialStore();
  const [isDragging, setIsDragging] = useState(false);
  const lastMousePos = useRef({ x: 0, y: 0 });

  // Smooth spring physics for the viewport
  const springX = useSpring(viewport.x, { stiffness: 300, damping: 30 });
  const springY = useSpring(viewport.y, { stiffness: 300, damping: 30 });
  const springZoom = useSpring(viewport.zoom, { stiffness: 300, damping: 30 });

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) { // Only drag if clicking the canvas background
      setIsDragging(true);
      lastMousePos.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;

    const dx = e.clientX - lastMousePos.current.x;
    const dy = e.clientY - lastMousePos.current.y;

    setViewport(viewport.x + dx, viewport.y + dy, viewport.zoom);
    lastMousePos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomSpeed = 0.001;
    const newZoom = Math.min(Math.max(viewport.zoom - e.deltaY * zoomSpeed, 0.2), 2);

    // Zoom towards cursor logic could be added here
    setViewport(viewport.x, viewport.y, newZoom);
  };

  return (
    <<divdiv
      className="w-full h-full overflow-hidden bg-dark-bg cursor-grab active:cursor-grabbing relative"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Background Grid Layer */}
      <<divdiv
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(0, 212, 255, 0.05) 1px, transparent 0)`,
          backgroundSize: `${40 * viewport.zoom}px ${40 * viewport.zoom}px`,
          transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.zoom})`,
          transformOrigin: '0 0'
        }}
      />

      {/* World Coordinate System */}
      <<motionmotion.div
        className="absolute inset-0 pointer-events-none"
        style={{
          x: springX,
          y: springY,
          scale: springZoom,
          transformOrigin: '0 0'
        }}
      >
        <<divdiv className="pointer-events-auto relative">
          {/* Render all agents from spatial store */}
          {Object.entries(agents).map(([id, agent]) => (
            <<AgentAgentWindow key={id} agentId={id} />
          ))}

          {children}
        </div>
      </motion.div>

      {/* Viewport HUD */}
      <<divdiv className="absolute bottom-6 right-6 p-3 bg-dark-surface/80 border border-dark-border rounded-md backdrop-blur-md font-mono text-tiny text-dark-text-muted pointer-events-none">
        <<divdiv className="flex flex-col gap-1">
          <div>X: {Math.round(viewport.x)}</div>
          <div>Y: {Math.round(viewport.y)}</div>
          <div>ZOOM: {Math.round(viewport.zoom * 100)}%</div>
        </div>
      </div>

      <<EmpireEmpirePrompt />
    </div>
  );
};
