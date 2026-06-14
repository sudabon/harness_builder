import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Copy, Download, FolderOpen, Pencil, RefreshCw, Terminal } from "lucide-react";

import { CodeViewer } from "@/components/code-viewer";
import { FileEditor } from "@/components/file-editor";
import { FileTree } from "@/components/file-tree";
import { Badge } from "@/components/ui/badge";
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
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showRegenerateConfirm, setShowRegenerateConfirm] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const editedFiles = files.filter((file) => file.is_edited);

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
      setFiles((current) =>
        current.map((file) =>
          file.id === nextFile.id ? { ...file, is_edited: nextFile.is_edited } : file,
        ),
      );
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

  async function handleRegenerate(force: boolean) {
    if (!id) {
      return;
    }

    setShowRegenerateConfirm(false);
    setIsRegenerating(true);
    setMessage(null);
    setError(null);
    try {
      const result = await api.generateFiles(id, force);
      setFiles(result.items);
      const currentId = activeFile?.id ?? null;
      const nextSummary =
        result.items.find((item) => item.id === currentId) ?? result.items[0] ?? null;
      if (nextSummary) {
        const nextFile = await api.getFile(id, nextSummary.id);
        setActiveFile(nextFile);
      } else {
        setActiveFile(null);
      }
      setIsEditing(false);
      setMessage(force ? "編集済みファイルを含めて再生成しました。" : "再生成しました。");
    } catch (regenerateError) {
      setError(
        regenerateError instanceof Error ? regenerateError.message : "再生成に失敗しました。",
      );
    } finally {
      setIsRegenerating(false);
    }
  }

  function handleRegenerateClick() {
    if (editedFiles.length > 0) {
      setShowRegenerateConfirm(true);
      return;
    }
    void handleRegenerate(false);
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
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{project?.name ?? "プロジェクトを読み込み中..."}</CardTitle>
              <CardDescription>
                OpenSpec change パッケージのプレビュー、編集、コピー、ZIP ダウンロードを行います。
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button onClick={() => void handleDownload()} type="button" variant="primary">
                  <Download className="h-4 w-4" />
                  ZIP
                </Button>
                {id ? (
                  <Button disabled={isRegenerating} onClick={handleRegenerateClick} type="button" variant="outline">
                    <RefreshCw className="h-4 w-4" />
                    {isRegenerating ? "再生成中..." : "再生成"}
                  </Button>
                ) : null}
              </div>
              {showRegenerateConfirm ? (
                <div className="space-y-3 rounded-2xl border border-border bg-muted/60 p-4">
                  <p className="text-sm font-medium">編集済みファイルがあります</p>
                  <p className="text-xs text-muted-foreground">
                    編集済み: {editedFiles.map((file) => file.file_path).join(", ")}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    編集内容を保護したまま再生成するか、テンプレート出力で上書きするかを選択してください。
                    選択から外れたツールの下書きは、編集済みでも tasks.md から削除されます。
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Button onClick={() => void handleRegenerate(false)} type="button" variant="secondary">
                      保護のまま再生成
                    </Button>
                    <Button onClick={() => void handleRegenerate(true)} type="button" variant="outline">
                      上書きして再生成
                    </Button>
                    <Button onClick={() => setShowRegenerateConfirm(false)} type="button" variant="outline">
                      キャンセル
                    </Button>
                  </div>
                </div>
              ) : null}
              <FileTree
                files={files}
                onSelect={(fileId) => void selectFile(fileId)}
                selectedFileId={activeFile?.id ?? null}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>使い方</CardTitle>
              <CardDescription>
                ZIP を OpenSpec 初期化済みの対象リポジトリへ展開して適用します。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3 text-sm text-muted-foreground">
                <li className="flex gap-3">
                  <FolderOpen className="mt-0.5 h-4 w-4 shrink-0 text-foreground" />
                  <span>ZIP を対象リポジトリのルートに展開し、`openspec/changes/` を配置します。</span>
                </li>
                <li className="flex gap-3">
                  <Terminal className="mt-0.5 h-4 w-4 shrink-0 text-foreground" />
                  <span>`/opsx:apply setup-ai-harness` を実行します。</span>
                </li>
              </ol>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {activeFile?.file_path ?? "ファイルを選択してください"}
                  {activeFile?.is_edited ? <Badge>編集済み</Badge> : null}
                </CardTitle>
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
              <p className="text-sm text-muted-foreground">生成された change ファイルがまだありません。</p>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
