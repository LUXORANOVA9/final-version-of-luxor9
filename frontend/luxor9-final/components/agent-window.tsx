import React from 'react';
import { motion } from 'framer-motion';
import { useSpatialStore } from '@/lib/spatialStore';
import { Terminal, Activity, ShieldAlert, Cpu } from 'lucide-react';

interface AgentWindowProps {
  agentId: string;
}

export const AgentWindow: React.FC<AgentWindowProps> = ({ agentId }) => {
  const agent = useSpatialStore((state) => state.agents[agentId]);
  const selectAgent = useSpatialStore((state) => state.selectAgent);
  const selectedAgentId = useSpatialStore((state) => state.selectedAgentId);

  if (!agent) return null;

  const isSelected = selectedAgentId === agentId;
  const isIntercepted = agent.state === 'intercepted';

  const tierColors: Record<number, string> = {
    0: '#FFFFFF', // LUXOR-PRIME
    1: '#00d4ff', // C-Suite
    2: '#8b5cf6', // VP
    3: '#3b82f6', // Managers
    4: '#64748b', // Workers
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{
        opacity: 1,
        scale: 1,
        x: agent.x,
        y: agent.y,
        zIndex: isSelected ? 100 : agent.z,
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      animate={{
        opacity: 1,
        scale: isIntercepted ? 1.05 : 1,
        x: agent.x,
        y: agent.y,
        zIndex: isSelected ? 100 : agent.z,
      }}
      onClick={() => selectAgent(agentId)}
      className={`absolute w-72 h-48 rounded-lg border-2 transition-all duration-300 cursor-pointer
        ${isSelected ? 'border-primary-500 shadow-glow-primary' : 'border-dark-border shadow-lg'}
        ${isIntercepted ? 'border-yellow-400 animate-pulse shadow-glow-secondary' : ''}
        bg-dark-surface/90 backdrop-blur-md overflow-hidden`}
    >
      {/* Title Bar */}
      <div className={`flex items-center justify-between px-3 py-2 border-b border-dark-border
        ${isSelected ? 'bg-primary-500/20' : 'bg-dark-bg/50'}`}>
        <div className="flex items-center gap-2">
          <Cpu size={12} className="text-primary-500" />
          <span className="text-tiny font-mono text-dark-text uppercase tracking-wider">
            {agent.name}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${agent.state === 'executing' ? 'bg-primary-500 animate-pulse' : 'bg-dark-text-muted'}`} />
          <span className="text-tiny font-mono opacity-60">T{agent.tier}</span>
        </div>
      </div>

      {/* Window Content */}
      <div className="p-3 h-full flex flex-col gap-2">
        <div className="flex items-center justify-between text-tiny font-mono">
          <div className="flex items-center gap-1 text-dark-text-muted">
            <Activity size={10} />
            <span>STATE: {agent.state.toUpperCase()}</span>
          </div>
          {isIntercepted && (
            <div className="flex items-center gap-1 text-yellow-400 animate-pulse font-bold">
              <ShieldAlert size={10} />
              <span className="tracking-tighter">NEURAL LOCK ACTIVE</span>
            </div>
          )}
        </div>

        {/* Terminal Log */}
        <div className="flex-1 bg-black/40 rounded border border-dark-border p-2 overflow-y-auto font-mono text-[10px] text-primary-400/80 space-y-1 custom-scrollbar">
          {agent.logs.length === 0 ? (
            <span className="opacity-40">Awaiting neural handshake...</span>
          ) : (
            agent.logs.map((log, i) => (
              <div key={i} className="flex gap-2">
                <span className="text-dark-text-muted opacity-50">[{new Date().toLocaleTimeString([], {hour12: false, hour:'2-digit', minute:'2-digit', second:'2-digit'})}]</span>
                <span>{log}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Bottom Accent Line */}
      <div
        className="absolute bottom-0 left-0 h-0.5 w-full transition-all duration-500"
        style={{ backgroundColor: tierColors[agent.tier], opacity: isSelected ? 1 : 0.4 }}
      />
    </motion.div>
  );
};
