"use client";

import { features } from "./hero";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function Features() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section id="features" className="py-24 bg-dark-surface relative overflow-hidden">
      <div className="absolute inset-0 dot-pattern opacity-30" />
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-h2 lg:text-h1 font-heading font-bold text-white mb-4">
            Everything You Need to <span className="gradient-text-primary">Scale</span>
          </h2>
          <p className="text-body-lg text-dark-muted max-w-2xl mx-auto">
            A complete autonomous business platform. No team required, no limits on growth.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={mounted ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full bg-dark-bg/50 backdrop-blur-sm border-dark-border/50 hover:border-primary/30 transition-all duration-300 group">
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 border border-primary/30 mb-4 group-hover:shadow-glow-primary transition-all duration-300">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-white group-hover:text-primary transition-colors">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-dark-muted">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
