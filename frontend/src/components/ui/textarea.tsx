import * as React from "react";

import { cn } from "@/lib/utils";

export function Textarea({
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-32 w-full rounded-3xl border border-border bg-input px-4 py-3 text-sm text-foreground outline-none transition focus:border-primary",
        className,
      )}
      {...props}
    />
  );
}
