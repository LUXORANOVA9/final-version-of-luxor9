"use client";

import { pricingPlans } from "./hero";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";

export function Pricing() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section id="pricing" className="py-24 bg-dark-surface relative overflow-hidden">
      <div className="absolute inset-0 dot-pattern opacity-20" />
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-h2 lg:text-h1 font-heading font-bold text-white mb-4">
            Simple, <span className="gradient-text-primary">Transparent</span> Pricing
          </h2>
          <p className="text-body-lg text-dark-muted max-w-2xl mx-auto">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={mounted ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className={`relative h-full ${
                plan.popular 
                  ? "bg-dark-bg border-primary/50 shadow-[0_0_40px_rgba(0,212,255,0.15)]" 
                  : "bg-dark-bg/50"
              }`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge variant="default" className="px-4 py-1">
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <CardHeader>
                  <CardTitle className="text-white">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="mb-6">
                    <span className="text-h1 font-heading font-bold text-white">
                      ${plan.price}
                    </span>
                    <span className="text-dark-muted">/month</span>
                  </div>
                  
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-3">
                        <Check className="h-5 w-5 text-accent-success flex-shrink-0" />
                        <span className="text-sm text-dark-text">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                
                <CardFooter>
                  <Button 
                    className={`w-full ${plan.popular ? "" : "variant-outline"}`}
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.cta}
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Enterprise callout */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 text-center"
        >
          <p className="text-dark-muted">
            Need a custom solution?{" "}
            <a href="/contact" className="text-primary hover:underline">
              Contact our sales team
            </a>{" "}
            for enterprise pricing.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
