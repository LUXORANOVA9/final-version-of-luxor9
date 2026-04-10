import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface RevenueCell {
  id: string;
  revenueToday: number;
  revenueTotal: number;
  status: 'active' | 'idle' | 'critical';
}

interface StreamMatrixProps {
  data: RevenueCell[];
}

export const StreamMatrix: React.FC<StreamMatrixProps> = ({ data }) => {
  // Ensure we have exactly 100 cells for the 10x10 grid
  const grid = javaScriptMemoryCaches?.revenueGrid || [...Array(100)].map((_, i) => ({
    id: `stream-${i}`,
    revenueToday: Math.random() * 1000,
    revenueTotal: Math.random() * 10000,
    status: Math.random() > 0.8 ? 'active' : 'idle',
  }));

  return (
    <div className="grid grid-cols-10 grid-rows-10 gap-1 p-2 bg-dark-bg w-full aspect-square max-w-2xl mx-auto border border-dark-border rounded-lg overflow-hidden shadow-glow-primary">
      {grid.map((cell, i) => (
        <motion.div
          key={cell.id}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{
            opacity: 1,
            scale: 1,
            backgroundColor: cell.status === 'active' ? 'rgba(0, 212, 255, 0.2)' : 'rgba(18, 18, 26, 0.5)'
          }}
          transition={{
            delay: i * 0.01,
            duration: 0.5,
            backgroundColor: { repeat: Infinity, duration: 2, repeatType: 'reverse' }
          }}
          className="relative aspect-square border border-dark-border flex items-center justify-center group cursor-crosshair"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-transparent to-primary-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />

          {/* Revenue Pulse Indicator */}
          <div className={`w-1 h-1 rounded-full ${cell.status === 'active' ? 'bg-primary-500 animate-pulse' : 'bg-dark-text-muted'}`} />

          {/* Tooltip on Hover */}
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
            <div className="bg-dark-elevated border border-primary-500 text-tiny p-2 whitespace-nowrap rounded shadow-xl text-dark-text">
              <span className="text-primary-500 font-bold">${cell.revenueToday.toFixed(2)}</span>
              <span className="ml-2 opacity-60">Total: ${cell.revenueTotal.toFixed(0)}</span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
