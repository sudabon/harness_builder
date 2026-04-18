import * as React from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-2xl border border-border bg-input px-4 text-sm text-foreground outline-none transition focus:border-primary",
        className,
      )}
      {...props}
    />
  );
}
