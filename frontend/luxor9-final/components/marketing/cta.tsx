"use client";

import { EmailCapture } from "./email-capture";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Zap } from "lucide-react";

export function CTA() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section className="py-24 bg-dark-bg relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-dark-bg via-primary/5 to-dark-bg" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
      </div>

      <div className="relative z-10 mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 border border-primary/30 mb-8">
            <Zap className="h-8 w-8 text-primary" />
          </div>
          
          <h2 className="text-h2 lg:text-h1 font-heading font-bold text-white mb-6">
            Ready to Build Your <span className="gradient-text-primary">AI Empire</span>?
          </h2>
          
          <p className="text-body-lg text-dark-muted mb-12 max-w-xl mx-auto">
            Join thousands of founders already building their autonomous businesses. 
            Get started in minutes.
          </p>

          <EmailCapture />

          <p className="mt-8 text-sm text-dark-subtle">
            No credit card required. Free 14-day trial. Cancel anytime.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
