import { Skeleton } from "@/shared/components/ui/skeleton";

export default function AppLoading() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-10" aria-busy="true" aria-label="Loading">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-4 w-full max-w-xl" />
      <Skeleton className="h-4 w-full max-w-lg" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
}
