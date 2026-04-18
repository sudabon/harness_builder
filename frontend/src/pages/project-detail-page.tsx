import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Copy, Download, Pencil, RefreshCw } from "lucide-react";

import { CodeViewer } from "@/components/code-viewer";
import { FileEditor } from "@/components/file-editor";
import { FileTree } from "@/components/file-tree";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { downloadBlob } from "@/lib/download";
import type { GeneratedFile, GeneratedFileSummary, Project } from "@/lib/types";

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<GeneratedFileSummary[]>([]);
  const [activeFile, setActiveFile] = useState<GeneratedFile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      return;
    }

    api
      .getProject(id)
      .then(setProject)
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "プロジェクト取得に失敗しました。"));

    api
      .listFiles(id)
      .then((result) => {
        setFiles(result.items);
        if (result.items[0]) {
          return api.getFile(id, result.items[0].id).then(setActiveFile);
        }
      })
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "ファイル一覧取得に失敗しました。"));
  }, [id]);

  async function selectFile(fileId: string) {
    if (!id) {
      return;
    }
    setIsEditing(false);
    setMessage(null);
    const file = await api.getFile(id, fileId);
    setActiveFile(file);
  }

  async function handleSave(content: string) {
    if (!id || !activeFile) {
      return;
    }

    setIsSaving(true);
    try {
      const nextFile = await api.updateFile(id, activeFile.id, content);
      setActiveFile(nextFile);
      setIsEditing(false);
      setMessage("ファイルを保存しました。");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "保存に失敗しました。");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDownload() {
    if (!id) {
      return;
    }

    try {
      const { blob, filename } = await api.exportProject(id);
      downloadBlob(blob, filename);
      setMessage("ZIP ダウンロードを開始しました。");
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : "ダウンロードに失敗しました。");
    }
  }

  async function handleCopy() {
    if (!activeFile) {
      return;
    }
    await navigator.clipboard.writeText(activeFile.content);
    setMessage("クリップボードへコピーしました。");
  }

  return (
    <div className="shell space-y-6">
      <section className="grid gap-6 xl:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>{project?.name ?? "プロジェクトを読み込み中..."}</CardTitle>
            <CardDescription>
              生成ファイルのプレビュー、編集、コピー、ZIP ダウンロードを行います。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button onClick={() => void handleDownload()} type="button" variant="primary">
                <Download className="h-4 w-4" />
                ZIP
              </Button>
              {id ? (
                <Button onClick={() => void api.generateFiles(id).then(() => window.location.reload())} type="button" variant="outline">
                  <RefreshCw className="h-4 w-4" />
                  再生成
                </Button>
              ) : null}
            </div>
            <FileTree
              files={files}
              onSelect={(fileId) => void selectFile(fileId)}
              selectedFileId={activeFile?.id ?? null}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>{activeFile?.file_path ?? "ファイルを選択してください"}</CardTitle>
                <CardDescription>
                  Syntax highlight 付きのプレビューと簡易エディタを提供します。
                </CardDescription>
              </div>
              {activeFile ? (
                <div className="flex gap-2">
                  <Button onClick={() => void handleCopy()} type="button" variant="outline">
                    <Copy className="h-4 w-4" />
                    コピー
                  </Button>
                  <Button onClick={() => setIsEditing(true)} type="button" variant="secondary">
                    <Pencil className="h-4 w-4" />
                    編集
                  </Button>
                </div>
              ) : null}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {message ? <p className="text-sm text-secondary">{message}</p> : null}
            {error ? <p className="text-sm text-danger">{error}</p> : null}

            {activeFile ? (
              isEditing ? (
                <FileEditor
                  initialValue={activeFile.content}
                  isSaving={isSaving}
                  onCancel={() => setIsEditing(false)}
                  onSave={handleSave}
                />
              ) : (
                <CodeViewer content={activeFile.content} />
              )
            ) : (
              <p className="text-sm text-muted-foreground">生成ファイルがまだありません。</p>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
