import { create } from 'zustand';

export type AgentState = 'idle' | 'thinking' | 'executing' | 'intercepted' | 'error';

export interface AgentSpatialData {
  id: string;
  name: string;
  tier: number;
  role: string;
  x: number;
  y: number;
  z: number;
  scale: number;
  state: AgentState;
  lastUpdate: number;
  logs: string[];
}

interface SpatialState {
  agents: Record<string, AgentSpatialData>;
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
  selectedAgentId: string | null;

  // Actions
  updateAgentPosition: (id: string, x: number, y: number, z: number) => void;
  updateAgentState: (id: string, state: AgentState) => void;
  addLog: (id: string, log: string) => void;
  setViewport: (x: number, y: number, zoom: number) => void;
  selectAgent: (id: string | null) => void;
  spawnAgent: (agent: AgentSpatialData) => void;
}

export const useSpatialStore = create<SpatialState>((set) => ({
  agents: {},
  viewport: {
    x: 0,
    y: 0,
    zoom: 1,
  },
  selectedAgentId: null,

  updateAgentPosition: (id, x, y, z) => set((state) => ({
    agents: {
      ...state.agents,
      [id]: state.agents[id]
        ? { ...state.agents[id], x, y, z, lastUpdate: Date.now() }
        : state.agents[id]
    }
  })),

  updateAgentState: (id, state) => set((state) => ({
    agents: {
      ...state.agents,
      [id]: state.agents[id] ? { ...state.agents[id], state, lastUpdate: Date.now() } : state.agents[id]
    }
  })),

  addLog: (id, log) => set((state) => ({
    agents: {
      ...state.agents,
      [id]: state.agents[id]
        ? { ...state.agents[id], logs: [...state.agents[id].logs, log].slice(-50), lastUpdate: Date.now() }
        : state.agents[id]
    }
  })),

  setViewport: (x, y, zoom) => set({
    viewport: { x, y, zoom }
  }),

  selectAgent: (id) => set({ selectedAgentId: id }),

  spawnAgent: (agent) => set((state) => ({
    agents: {
      ...state.agents,
      [agent.id]: agent
    }
  })),
}));
