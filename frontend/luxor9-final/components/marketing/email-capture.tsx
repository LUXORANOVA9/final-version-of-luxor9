"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { ArrowRight, Check, Loader2 } from "lucide-react";

export function EmailCapture() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    if (email.includes("@")) {
      setStatus("success");
      setMessage("Welcome to the empire! Check your inbox for next steps.");
      setEmail("");
    } else {
      setStatus("error");
      setMessage("Please enter a valid email address.");
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {status === "success" ? (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-accent-success/10 border border-accent-success/30">
          <Check className="h-5 w-5 text-accent-success flex-shrink-0" />
          <p className="text-sm text-accent-success">{message}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <Input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
              required
            />
            <Button type="submit" disabled={status === "loading"}>
              {status === "loading" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Join <ArrowRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          </div>
          {status === "error" && (
            <p className="text-sm text-accent-error">{message}</p>
          )}
          <p className="text-xs text-dark-muted">
            Join 2,847 founders building their AI empires. No spam, ever.
          </p>
        </form>
      )}
    </div>
  );
}
