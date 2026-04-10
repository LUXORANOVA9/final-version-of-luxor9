import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

interface AgentNode {
  id: string;
  name: string;
  tier: number;
  role: string;
  children?: AgentNode[];
}

interface NeuralMapProps {
  data: AgentNode | AgentNode[];
  onAgentClick?: (agent: AgentNode) => void;
}

const NODE_WIDTH = 140;
const NODE_HEIGHT = 40;
const LEVEL_SPACING = 120;
const SIBLING_SPACING = 60;

const AgentNodeComponent = ({ agent, x, y, onAgentClick }: {
  agent: AgentNode;
  x: number;
  y: number;
  onAgentClick?: (agent: AgentNode) => void
}) => {
  const tierColors: Record<number, string> = {
    0: '#FFFFFF', // LUXOR-PRIME
    1: '#00d4ff', // C-Suite
    2: '#8b5cf6', // VP
    3: '#3b82f6', // Managers
    4: '#64748b', // Workers
  };

  return (
    <motion.g
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.1 }}
      onClick={() => onAgentClick?.(agent)}
      style={{ cursor: 'pointer' }}
    >
      <rect
        x={x - NODE_WIDTH / 2}
        y={y - NODE_HEIGHT / 2}
        width={NODE_WIDTH}
        height={NODE_HEIGHT}
        rx="4"
        fill="rgba(18, 18, 26, 0.8)"
        stroke={tierColors[agent.tier] || '#00d4ff'}
        strokeWidth="2"
        className="drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]"
      />
      <text
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#e2e8f0"
        fontSize="10"
        fontWeight="600"
        className="font-mono"
      >
        {agent.name}
      </text>
      <text
        x={x}
        y={y + 12}
        textAnchor="middle"
        dominantBaseline="middle"
        fill={tierColors[agent.tier] || '#00d4ff'}
        fontSize="8"
        className="font-mono opacity-80"
      >
        T{agent.tier} | {agent.role}
      </text>
    </motion.g>
  );
};

export const NeuralMap: React.FC<NeuralMapProps> = ({ data, onAgentClick }) => {
  const { nodes, edges } = useMemo(() => {
    const allNodes: { agent: AgentNode; x: number; y: number }[] = [];
    const allEdges: { x1: number; y1: number; x2: number; y2: number }[] = [];

    const calculatePositions = (node: AgentNode, x: number, y: number, width: number) => {
      allNodes.push({ agent: node, x, y });

      if (node.children && node.children.length > 0) {
        const childCount = node.children.length;
        const totalWidth = (childCount - 1) * SIBLING_SPACING;
        const startX = x - totalWidth / 2;

        node.children.forEach((child, i) => {
          const childX = startX + i * SIBLING_SPACING;
          const childY = y + LEVEL_SPACING;

          allEdges.push({ x1: x, y1: y, x2: childX, y2: childY });
          calculatePositions(child, childX, childY, 0);
        });
      }
    };

    if (Array.isArray(data)) {
      data.forEach((root, i) => calculatePositions(root, i * 500, 50, 0));
    } else {
      calculatePositions(data, 0, 50, 0);
    }

    return { nodes: allNodes, edges: allEdges };
  }, [data]);

  return (
    <div className="w-full h-full overflow-auto bg-dark-bg relative">
      <svg
        width="5000"
        height="5000"
        className="absolute top-0 left-0"
        style={{ zoom: '0.5' }}
      >
        <defs>
          <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.2" />
          </linearGradient>
        </defs>

        {edges.map((edge, i) => (
          <line
            key={i}
            x1={edge.x1}
            y1={edge.y1}
            x2={edge.x2}
            y2={edge.y2}
            stroke="url(#edgeGradient)"
            strokeWidth="1"
            className="opacity-40"
          />
        ))}

        {nodes.map((node, i) => (
          <AgentNodeComponent
            key={node.agent.id}
            agent={node.agent}
            x={node.x}
            y={node.y}
            onAgentClick={onAgentClick}
          />
        ))}
      </svg>
    </div>
  );
};
