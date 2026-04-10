import React, { useState, useRef, useEffect } from 'react';
import { useSpatialStore } from '@/lib/spatialStore';
import { Terminal, Send, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const EmpirePrompt: React.FC = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    updateAgentState,
    addLog,
    selectedAgentId,
    agents,
    setViewport
  } = useSpatialStore();

  useEffect(() => {
    // Auto-focus the prompt on mount
    inputRef.current?.focus();
  }, []);

  const handleCommand = (cmd: string) => {
    const trimmed = cmd.trim();
    if (!trimmed) return;

    const [command, ...args] = trimmed.split(' ');
    const argString = args.join(' ');

    // Log the command to the system/history
    setHistory(prev => [...prev, trimmed]);
    setHistoryIndex(-1);

    switch (command) {
      case '/intercept': {
        const targetId = args[0] || selectedAgentId;
        if (targetId && agents[targetId]) {
          updateAgentState(targetId, 'intercepted');
          addLog(targetId, `SOVEREIGN INTERCEPT: ${trimmed}`);
        } else {
          addLog('system', 'Error: No valid agent target for intercept');
        }
        break;
      }
      case '/resume': {
        const targetId = args[0] || selectedAgentId;
        if (targetId && agents[targetId]) {
          updateAgentState(targetId, 'idle');
          addLog(targetId, `SOVEREIGN RELEASE: Agent resumed`);
        }
        break;
      }
      case '/broadcast': {
        const message = argString;
        if (message) {
          Object.keys(agents).forEach(id => {
            addLog(id, `BROADCAST: ${message}`);
          });
        }
        break;
      }
      case '/halt': {
        Object.keys(agents).forEach(id => {
          updateAgentState(id, 'idle');
        });
        // Add a global log to everyone
        Object.keys(agents).forEach(id => addLog(id, 'SYSTEM HALT: Swarm paused by Sovereign'));
        break;
      }
      case '/snap': {
        const targetId = args[0] || selectedAgentId;
        if (targetId && agents[targetId]) {
          const agent = agents[targetId];
          // Snap viewport to agent (negative of agent position)
          setViewport(-agent.x, -agent.y, 1);
        }
        break;
      }
      default:
        console.log('Unknown command:', command);
    }
    setInput('');
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCommand(input);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < history.length - 1) {
        const nextIndex = historyIndex + 1;
        setHistoryIndex(nextIndex);
        setInput(history[history.length - 1 - nextIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const nextIndex = historyIndex - 1;
        setHistoryIndex(nextIndex);
        setInput(history[history.length - 1 - nextIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-3xl px-4 z-[1000]">
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative group"
      >
        {/* Glow Effect */}
        <div className="absolute -inset-1 bg-primary-500/20 rounded-lg blur-lg opacity-50 group-focus-within:opacity-100 transition-opacity" />

        <div className="relative flex items-center bg-black border-2 border-primary-500/50 rounded-lg overflow-hidden shadow-2xl shadow-primary-500/10">
          <div className="p-3 bg-primary-500/10 border-r border-primary-500/30">
            <Terminal size={18} className="text-primary-500" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Enter Sovereign Command (e.g. /intercept agent-1)..."
            className="flex-1 bg-transparent py-4 px-4 font-mono text-sm text-white placeholder-dark-text-muted outline-none"
          />

          <div className="p-3">
            <button
              onClick={() => handleCommand(input)}
              className="p-2 rounded-md bg-primary-500 text-black hover:bg-primary-400 transition-colors"
            >
              <Send size={16} />
            </button>
          </div>
        </div>

        {/* Quick Hint */}
        <div className="absolute -top-8 left-0 right-0 flex justify-center gap-4 pointer-events-none">
          <div className="flex items-center gap-1 px-2 py-1 rounded bg-black/80 border border-primary-500/30 text-[10px] font-mono text-primary-500/70 backdrop-blur-sm">
            <Zap size={8} />
            <span>/intercept [id]</span>
          </div>
          <div className="flex items-center gap-1 px-2 py-1 rounded bg-black/80 border border-primary-500/30 text-[10px] font-mono text-primary-500/70 backdrop-blur-sm">
            <Zap size={8} />
            <span>/broadcast [msg]</span>
          </div>
          <div className="flex items-center gap-1 px-2 py-1 rounded bg-black/80 border border-primary-500/30 text-[10px] font-mono text-primary-500/70 backdrop-blur-sm">
            <Zap size={8} />
            <span>/snap [id]</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
