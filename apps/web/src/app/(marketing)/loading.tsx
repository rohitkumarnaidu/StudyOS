import { Skeleton } from "@/shared/components/ui/skeleton";

export default function MarketingLoading() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-16" aria-busy="true" aria-label="Loading">
      <Skeleton className="h-6 w-24" />
      <Skeleton className="h-10 w-2/3" />
      <Skeleton className="h-20 w-full" />
    </div>
  );
}
