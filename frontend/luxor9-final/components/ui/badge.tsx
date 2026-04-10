import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary/20 text-primary border border-primary/30",
        secondary: "bg-secondary/20 text-secondary border border-secondary/30",
        success: "bg-accent-success/20 text-accent-success border border-accent-success/30",
        warning: "bg-accent-warning/20 text-accent-warning border border-accent-warning/30",
        error: "bg-accent-error/20 text-accent-error border border-accent-error/30",
        info: "bg-accent-info/20 text-accent-info border border-accent-info/30",
        outline: "border border-dark-border text-dark-muted",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
