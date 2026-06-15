export function FieldHint({ text }: { text?: string }) {
  if (!text) {
    return null;
  }

  return <p className="text-sm text-muted-foreground">{text}</p>;
}
