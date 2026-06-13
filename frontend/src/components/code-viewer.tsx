import { useMemo } from "react";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

interface CodeViewerProps {
  content: string;
}

export function CodeViewer({ content }: CodeViewerProps) {
  const html = useMemo(() => hljs.highlightAuto(content).value, [content]);

  return (
    <pre className="max-h-[60vh] overflow-auto rounded-3xl bg-[#0b1115] p-5 text-sm text-slate-100">
      <code dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  );
}
