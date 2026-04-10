"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Zap, Users, DollarSign, Activity, Shield, Rocket, Brain, Layers, ArrowRight } from "lucide-react";

const metrics = [
  { label: "AI Agents", value: "179", icon: Brain },
  { label: "Income Streams", value: "100", icon: Layers },
  { label: "Active Users", value: "2,847+", icon: Users },
  { label: "Revenue Generated", value: "$1.2M+", icon: DollarSign },
];

const features = [
  {
    icon: Brain,
    title: "Autonomous Decision Making",
    description: "179 intelligent agents working 24/7. From strategic planning to task execution, your AI empire never sleeps.",
  },
  {
    icon: Layers,
    title: "100 Income Streams",
    description: "Diversified revenue across 10 categories. AI Agency, SaaS, Creative, Finance, E-commerce, and more.",
  },
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description: "Multi-layer validation, sandboxed execution, and comprehensive audit trails. Your data stays protected.",
  },
  {
    icon: Rocket,
    title: "Parallel Execution",
    description: "All streams run simultaneously. Real-time monitoring with second-by-second updates.",
  },
  {
    icon: Activity,
    title: "Smart Orchestration",
    description: "5-tier hierarchy: Commander → C-Suite → VPs → Managers → Workers. Just like a real company.",
  },
  {
    icon: Users,
    title: "Built for Solo Founders",
    description: "One-person operation with enterprise-level output. No team required.",
  },
];

const steps = [
  {
    number: "01",
    title: "Deploy Your Empire",
    description: "One command boots all 179 agents. The hierarchy initializes automatically.",
  },
  {
    number: "02",
    title: "Configure Your Streams",
    description: "Enable any combination of 100 income streams across 10 business categories.",
  },
  {
    number: "03",
    title: "Monitor & Scale",
    description: "Watch real-time metrics. Let AI optimize while you focus on vision.",
  },
];

const pricingPlans = [
  {
    name: "Starter",
    description: "For solo founders getting started",
    price: 49,
    features: [
      "25 AI Agents",
      "10 Income Streams",
      "Basic Dashboard",
      "Email Support",
      "Community Access",
    ],
    cta: "Start Free Trial",
    popular: false,
  },
  {
    name: "Professional",
    description: "For growing businesses",
    price: 149,
    features: [
      "100 AI Agents",
      "50 Income Streams",
      "Advanced Dashboard",
      "Priority Support",
      "API Access",
      "Custom Integrations",
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    description: "For maximum scale",
    price: 499,
    features: [
      "179 AI Agents (Full)",
      "100 Income Streams",
      "Real-time Analytics",
      "Dedicated Support",
      "Custom Development",
      "SLA Guarantee",
      "On-premise Option",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

export function Hero() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background effects */}
      <div className="absolute inset-0 bg-dark-bg">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="flex justify-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 text-sm">
            <Zap className="h-4 w-4 text-primary" />
            <span className="text-primary font-medium">Now in Public Beta</span>
          </div>
        </motion.div>

        {/* Headline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center mb-8"
        >
          <h1 className="text-display sm:text-h1 lg:text-display font-heading font-extrabold tracking-tight mb-6">
            <span className="text-white">Build Your </span>
            <span className="gradient-text-primary">AI Empire</span>
          </h1>
          <p className="text-body-lg lg:text-h4 text-dark-muted max-w-3xl mx-auto mb-8">
            Deploy 179 intelligent agents to manage 100 income streams automatically. 
            The autonomous AI company operating system for solo founders.
          </p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
        >
          <button className="inline-flex items-center justify-center gap-2 h-12 px-6 text-base font-semibold rounded-lg bg-primary text-dark-bg hover:bg-primary-400 shadow-[0_0_30px_rgba(0,212,255,0.4)] transition-all duration-300 hover:scale-105">
            Start Building Free
            <ArrowRight className="h-5 w-5" />
          </button>
          <button className="inline-flex items-center justify-center gap-2 h-12 px-6 text-base font-semibold rounded-lg border border-dark-border text-white hover:bg-dark-surface transition-all duration-300">
            Watch Demo
          </button>
        </motion.div>

        {/* Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-8 mb-16"
        >
          {metrics.map((metric, index) => (
            <div
              key={metric.label}
              className="text-center p-6 rounded-xl bg-dark-surface/50 border border-dark-border backdrop-blur-sm"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <metric.icon className="h-8 w-8 text-primary mx-auto mb-3" />
              <div className="text-h2 lg:text-h3 font-heading font-bold text-white mb-1">
                {metric.value}
              </div>
              <div className="text-sm text-dark-muted">{metric.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="relative max-w-5xl mx-auto"
        >
          <div className="absolute inset-0 bg-gradient-to-t from-dark-bg via-transparent to-transparent z-10 pointer-events-none" />
          <div className="rounded-xl border border-dark-border bg-dark-surface overflow-hidden shadow-2xl">
            {/* Browser chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-dark-border bg-dark-elevated">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-accent-error/80" />
                <div className="w-3 h-3 rounded-full bg-accent-warning/80" />
                <div className="w-3 h-3 rounded-full bg-accent-success/80" />
              </div>
              <div className="flex-1 text-center">
                <span className="text-xs text-dark-muted font-mono">luxor9.app/dashboard</span>
              </div>
            </div>
            {/* Dashboard content */}
            <div className="p-6 bg-dark-bg min-h-[400px]">
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="col-span-2 bg-dark-surface rounded-lg p-4 border border-dark-border">
                  <div className="text-xs text-dark-muted mb-2">REVENUE TODAY</div>
                  <div className="text-h2 font-bold text-accent-success">$3,847.23</div>
                  <div className="text-xs text-accent-success mt-1">+12.4% from yesterday</div>
                </div>
                <div className="bg-dark-surface rounded-lg p-4 border border-dark-border">
                  <div className="text-xs text-dark-muted mb-2">ACTIVE AGENTS</div>
                  <div className="text-h2 font-bold text-primary">179/179</div>
                  <div className="text-xs text-primary mt-1">All systems nominal</div>
                </div>
              </div>
              <div className="grid grid-cols-5 gap-2 mb-4">
                {[...Array(100)].map((_, i) => (
                  <div
                    key={i}
                    className={`aspect-square rounded ${
                      i < 78 ? "bg-accent-success" : i < 90 ? "bg-primary" : "bg-dark-border"
                    }`}
                    style={{ opacity: i < 78 ? 0.8 : 1 }}
                  />
                ))}
              </div>
              <div className="text-xs text-dark-muted text-center">
                78 of 100 income streams active
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export { features, steps, pricingPlans };
