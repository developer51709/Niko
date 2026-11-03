import { useEffect, useRef } from "react";
import { useStrings } from "../i18n";

type RichTextEditorProps = {
  value: string;
  /** The formatted body and its plain-text equivalent, on every edit. */
  onChange: (html: string, text: string) => void;
  placeholder?: string;
  disabled?: boolean;
};

type Tool = { command: string; label: string; titleKey: string; value?: string; className?: string };

const TOOLS: Tool[] = [
  { command: "bold", label: "B", titleKey: "editor.bold", className: "is-bold" },
  { command: "italic", label: "I", titleKey: "editor.italic", className: "is-italic" },
  { command: "underline", label: "U", titleKey: "editor.underline", className: "is-underline" },
  { command: "strikeThrough", label: "S", titleKey: "editor.strike", className: "is-strike" },
  { command: "insertUnorderedList", label: "• List", titleKey: "editor.bulleted" },
  { command: "insertOrderedList", label: "1. List", titleKey: "editor.numbered" },
  { command: "formatBlock", value: "blockquote", label: "❝", titleKey: "editor.quote" },
  { command: "removeFormat", label: "Clear", titleKey: "editor.clearFormatting" },
];

/**
 * A small Gmail-style editor: the toolbar formats the current selection, and
 * the body is a contenteditable area that hands back both HTML and plain text.
 *
 * `styleWithCSS` is turned off so bold/italic come out as `<b>`/`<i>` rather
 * than styled spans — that is the shape the server keeps when it sanitises the
 * body, and the shape every mail client understands.
 */
export function RichTextEditor({ value, onChange, placeholder, disabled }: RichTextEditorProps) {
  const { t } = useStrings("shared");
  const editorRef = useRef<HTMLDivElement | null>(null);
  const lastHtml = useRef(value);

  useEffect(() => {
    const editor = editorRef.current;
    if (editor && value !== lastHtml.current && value !== editor.innerHTML) {
      editor.innerHTML = value;
      lastHtml.current = value;
    }
  }, [value]);

  useEffect(() => {
    try {
      document.execCommand("styleWithCSS", false, "false");
      document.execCommand("defaultParagraphSeparator", false, "p");
    } catch {
      // Not every browser exposes these; the toolbar still works.
    }
  }, []);

  function emit() {
    const editor = editorRef.current;
    if (!editor) return;
    lastHtml.current = editor.innerHTML;
    onChange(editor.innerHTML, editor.innerText);
  }

  function run(command: string, argument?: string) {
    if (disabled) return;
    editorRef.current?.focus();
    document.execCommand(command, false, argument);
    emit();
  }

  function addLink() {
    if (disabled) return;
    const url = window.prompt("Link address", "https://");
    if (!url) return;
    const trimmed = url.trim();
    if (!/^(https?:\/\/|mailto:)/i.test(trimmed)) {
      window.alert("Links must start with http://, https:// or mailto:.");
      return;
    }
    editorRef.current?.focus();
    document.execCommand("createLink", false, trimmed);
    emit();
  }

  return (
    <div className={`staff-email-editor${disabled ? " is-disabled" : ""}`}>
      <div className="staff-email-editor-toolbar" role="toolbar" aria-label={t("editor.formatting")}>
        {TOOLS.map((tool) => (
          <button
            key={tool.command + (tool.value || "")}
            type="button"
            title={t(tool.titleKey)}
            aria-label={t(tool.titleKey)}
            className={tool.className}
            // Keep the selection alive while a toolbar button is pressed.
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => run(tool.command, tool.value)}
            disabled={disabled}
          >
            {tool.label}
          </button>
        ))}
        <button
          type="button"
          title={t("editor.insertLink")}
          aria-label={t("editor.insertLink")}
          className="is-link"
          onMouseDown={(event) => event.preventDefault()}
          onClick={addLink}
          disabled={disabled}
        >
          Link
        </button>
      </div>
      <div
        ref={editorRef}
        className="staff-email-editor-body"
        contentEditable={!disabled}
        suppressContentEditableWarning
        role="textbox"
        aria-multiline="true"
        aria-label={t("editor.message")}
        data-placeholder={placeholder || t("editor.placeholder")}
        onInput={emit}
        onBlur={emit}
        onPaste={() => window.setTimeout(emit, 0)}
      />
    </div>
  );
}
