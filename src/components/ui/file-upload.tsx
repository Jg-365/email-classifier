import * as React from "react";
import { cn } from "@/lib/utils";
import { Upload, File, X } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  selectedFile: File | null;
  accept?: string;
  className?: string;
}

const FileUpload = React.forwardRef<HTMLDivElement, FileUploadProps>(
  ({ onFileSelect, onFileRemove, selectedFile, accept = ".txt,.pdf", className }, ref) => {
    const fileInputRef = React.useRef<HTMLInputElement>(null);
    const [isDragOver, setIsDragOver] = React.useState(false);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    };

    const handleDragOver = (event: React.DragEvent) => {
      event.preventDefault();
      setIsDragOver(true);
    };

    const handleDragLeave = (event: React.DragEvent) => {
      event.preventDefault();
      setIsDragOver(false);
    };

    const handleDrop = (event: React.DragEvent) => {
      event.preventDefault();
      setIsDragOver(false);
      
      const file = event.dataTransfer.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    };

    const handleClick = () => {
      fileInputRef.current?.click();
    };

    return (
      <div
        ref={ref}
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 transition-colors cursor-pointer",
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50",
          className
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="hidden"
        />
        
        {selectedFile ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <File className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium text-sm">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFileRemove();
              }}
              className="p-1 hover:bg-muted rounded-full transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div className="text-center space-y-3">
            <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
            <div>
              <p className="text-sm font-medium">Clique para enviar ou arraste um arquivo</p>
              <p className="text-xs text-muted-foreground">
                Suporta arquivos .txt e .pdf (máx. 20MB)
              </p>
            </div>
          </div>
        )}
      </div>
    );
  }
);

FileUpload.displayName = "FileUpload";

export { FileUpload };