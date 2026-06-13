import { Badge } from "@/components/ui/badge";
import type { GeneratedFileSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

interface FileTreeProps {
  files: GeneratedFileSummary[];
  selectedFileId: string | null;
  onSelect: (fileId: string) => void;
}

export function FileTree({ files, selectedFileId, onSelect }: FileTreeProps) {
  return (
    <div className="space-y-2">
      {files.map((file) => (
        <button
          className={cn(
            "block w-full rounded-2xl border px-3 py-3 text-left text-sm transition",
            selectedFileId === file.id
              ? "border-primary bg-primary/8 text-foreground"
              : "border-transparent bg-muted/60 text-muted-foreground hover:border-border hover:bg-card",
          )}
          key={file.id}
          onClick={() => onSelect(file.id)}
          type="button"
        >
          <span className="flex items-center justify-between gap-2">
            <span className="font-mono text-xs">{file.file_path}</span>
            {file.is_edited ? <Badge>編集済み</Badge> : null}
          </span>
        </button>
      ))}
    </div>
  );
}
