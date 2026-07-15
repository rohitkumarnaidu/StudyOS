import type { ReactNode } from "react";
import { Card } from "@/shared/components/ui/card";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-1 items-center justify-center px-4 py-16">
      <Card className="w-full max-w-sm p-6">{children}</Card>
    </div>
  );
}
