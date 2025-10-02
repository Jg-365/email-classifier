import * as React from "react";
import { cn } from "@/lib/utils";
import { CheckCircle, AlertTriangle } from "lucide-react";

interface ClassificationBadgeProps {
  type: "productive" | "unproductive";
  className?: string;
}

const ClassificationBadge = ({
  type,
  className,
}: ClassificationBadgeProps) => {
  const isProductive = type === "productive";

  return (
    <div
      className={cn(
        "inline-flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium",
        isProductive
          ? "bg-green-100 text-green-800 border border-green-200"
          : "bg-orange-100 text-orange-800 border border-orange-200",
        className
      )}
    >
      {isProductive ? (
        <CheckCircle className="h-4 w-4" />
      ) : (
        <AlertTriangle className="h-4 w-4" />
      )}
      <span>
        {isProductive ? "Produtivo" : "Não Produtivo"}
      </span>
    </div>
  );
};

export { ClassificationBadge };
