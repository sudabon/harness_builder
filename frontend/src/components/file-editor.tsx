import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface FileEditorProps {
  initialValue: string;
  isSaving: boolean;
  onCancel: () => void;
  onSave: (nextValue: string) => Promise<void>;
}

export function FileEditor({ initialValue, isSaving, onCancel, onSave }: FileEditorProps) {
  const [content, setContent] = useState(initialValue);

  return (
    <div className="space-y-4">
      <Textarea className="min-h-[60vh] font-mono text-xs" onChange={(e) => setContent(e.target.value)} value={content} />
      <div className="flex gap-3">
        <Button disabled={isSaving} onClick={() => void onSave(content)} type="button">
          {isSaving ? "保存中..." : "保存"}
        </Button>
        <Button onClick={onCancel} type="button" variant="outline">
          キャンセル
        </Button>
      </div>
    </div>
  );
}
