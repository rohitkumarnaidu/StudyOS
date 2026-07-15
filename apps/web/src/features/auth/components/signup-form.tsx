"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useRef } from "react";
import { FormProvider, useForm } from "react-hook-form";

import { signupFormSchema, type SignupFormValues } from "@/features/auth/schema";
import { useSession } from "@/features/auth/session-provider";
import { FormField } from "@/shared/components/form/form-field";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { notifyError, notifyFromUnknown, notifySuccess } from "@/shared/lib";
import { safeNextPath } from "@/shared/lib/safe-next-path";
import Link from "next/link";

function SignupFormFallback() {
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading sign-up form">
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      <Skeleton className="h-10 w-full" />
    </div>
  );
}

function SignupFormInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh } = useSession();
  const nextPath = safeNextPath(searchParams.get("next"), "/dashboard");

  const submitInProgress = useRef(false);

  const form = useForm<SignupFormValues>({
    resolver: zodResolver(signupFormSchema),
    defaultValues: { email: "", password: "", displayName: "", terms: false },
  });

  async function onSubmit(values: SignupFormValues) {
    if (submitInProgress.current) return;
    submitInProgress.current = true;

    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: values.email,
          password: values.password,
          display_name: values.displayName,
        }),
      });

      if (!res.ok) {
        const err = (await res.json().catch(() => null)) as { error?: string } | null;
        if (res.status === 409) {
          notifyError("Email already in use");
          form.setError("email", { message: "Email already registered" });
        } else {
          notifyError(err?.error ?? "Signup failed");
        }
        return;
      }

      notifySuccess("Account created! Signing in...");
      await refresh();
      router.push(nextPath);
      router.refresh();
    } catch (e) {
      notifyFromUnknown(e, "Network error");
    } finally {
      submitInProgress.current = false;
    }
  }

  return (
    <FormProvider {...form}>
      <form className="space-y-4" onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit(onSubmit)();
      }} noValidate>
        <FormField<SignupFormValues> name="displayName" label="Full name">
          <Input
            id="displayName"
            type="text"
            autoComplete="name"
            {...form.register("displayName")}
          />
        </FormField>

        <FormField<SignupFormValues> name="email" label="Email">
          <Input id="email" type="email" autoComplete="email" {...form.register("email")} />
        </FormField>

        <FormField<SignupFormValues> name="password" label="Password" hint="Min 8 characters">
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            {...form.register("password")}
          />
        </FormField>

        <div className="flex items-center gap-2">
          <input
            id="terms"
            type="checkbox"
            className="h-4 w-4 rounded border-gray-300"
            {...form.register("terms")}
          />
          <label htmlFor="terms" className="text-sm text-muted-foreground">
            I agree to the{" "}
            <a href="/terms" className="underline hover:text-foreground">
              terms of service
            </a>
          </label>
          {form.formState.errors.terms && (
            <span className="text-xs text-destructive">{form.formState.errors.terms.message}</span>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating account…" : "Create account"}
        </Button>

        <div className="text-center text-sm">
          Already have an account?{" "}
          <Link href="/login" className="underline hover:text-foreground">
            Sign in
          </Link>
        </div>
      </form>
    </FormProvider>
  );
}

export function SignupForm() {
  return (
    <Suspense fallback={<SignupFormFallback />}>
      <SignupFormInner />
    </Suspense>
  );
}
