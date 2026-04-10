"use client";

import { steps } from "./hero";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

export function HowItWorks() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section id="how-it-works" className="py-24 bg-dark-bg relative overflow-hidden">
      <div className="absolute inset-0 grid-pattern opacity-30" />
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-h2 lg:text-h1 font-heading font-bold text-white mb-4">
            How It <span className="gradient-text-primary">Works</span>
          </h2>
          <p className="text-body-lg text-dark-muted max-w-2xl mx-auto">
            From zero to fully operational AI empire in three simple steps.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting line */}
          <div className="hidden lg:block absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-12">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 20 }}
                animate={mounted ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="relative"
              >
                <div className="text-center lg:text-left">
                  {/* Step number */}
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 border border-primary/30 text-primary font-mono font-bold mb-6">
                    {step.number}
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-h3 font-heading font-bold text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-dark-muted">
                    {step.description}
                  </p>
                  
                  {/* Arrow (desktop only) */}
                  {index < steps.length - 1 && (
                    <div className="hidden lg:flex justify-end mt-8">
                      <ArrowRight className="h-6 w-6 text-primary/50" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Code snippet */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-16 max-w-2xl mx-auto"
        >
          <div className="rounded-xl border border-dark-border bg-dark-surface overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-dark-border bg-dark-elevated">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-accent-error/80" />
                <div className="w-3 h-3 rounded-full bg-accent-warning/80" />
                <div className="w-3 h-3 rounded-full bg-accent-success/80" />
              </div>
              <span className="text-xs text-dark-muted font-mono ml-2">terminal</span>
            </div>
            <div className="p-6 font-mono text-sm">
              <p className="text-dark-muted mb-2"># Deploy your AI empire</p>
              <p className="text-primary mb-4">luxor9 deploy --all --agents 179</p>
              <p className="text-dark-subtle mb-2">Booting LUXOR-PRIME...</p>
              <p className="text-dark-subtle mb-2">Initializing C-Suite agents...</p>
              <p className="text-dark-subtle mb-2">Deploying 100 income streams...</p>
              <p className="text-accent-success">
                <span className="text-primary">✓</span> Empire deployed successfully!
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
