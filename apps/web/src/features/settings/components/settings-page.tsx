/* eslint-disable react-hooks/incompatible-library -- RHF watch() is required for reactive form controls */
"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { FormProvider, useForm } from "react-hook-form";
import { z } from "zod";
import { FormField } from "@/shared/components/form/form-field";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Switch } from "@/shared/components/ui/switch";
import { Label } from "@/shared/components/ui/label";
import { Separator } from "@/shared/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { notifySuccess } from "@/shared/lib";
import { useTheme } from "next-themes";
import { useState, useEffect, useRef } from "react";
import { User, Bell, Palette, Download, Languages, Accessibility, Keyboard } from "lucide-react";

const profileSchema = z.object({
  displayName: z.string().min(1, "Name is required").max(100),
  email: z.string().email("Enter a valid email"),
});

type ProfileValues = z.infer<typeof profileSchema>;

const notificationSchema = z.object({
  emailNotifications: z.boolean(),
  studyReminders: z.boolean(),
  streakAlerts: z.boolean(),
  weeklyReport: z.boolean(),
});

type NotificationValues = z.infer<typeof notificationSchema>;

// eslint-disable-next-line @typescript-eslint/no-unused-vars -- schema used for type inference only
const accessibilitySchema = z.object({
  reduceMotion: z.boolean(),
  highContrast: z.boolean(),
  largeText: z.boolean(),
  screenReader: z.boolean(),
});

type AccessibilityValues = z.infer<typeof accessibilitySchema>;

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "हिन्दी (Hindi)" },
  { value: "ta", label: "தமிழ் (Tamil)" },
];

export function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const initialized = useRef(false);
  const [mounted, setMounted] = useState(false);
  const [language, setLanguage] = useState("en");

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      setMounted(true);
    }
  }, []);

  const profileForm = useForm<ProfileValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: { displayName: "Demo User", email: "demo@studyos.app" },
  });

  const notificationForm = useForm<NotificationValues>({
    resolver: zodResolver(notificationSchema),
    defaultValues: {
      emailNotifications: true,
      studyReminders: true,
      streakAlerts: true,
      weeklyReport: false,
    },
  });

  const accessibilityForm = useForm<AccessibilityValues>({
    defaultValues: {
      reduceMotion: false,
      highContrast: false,
      largeText: false,
      screenReader: false,
    },
  });

  function onProfileSubmit() {
    notifySuccess("Profile updated");
  }

  function onNotificationSubmit() {
    notifySuccess("Notification preferences saved");
  }

  function onAccessibilitySubmit() {
    notifySuccess("Accessibility settings saved");
  }

  function handleExportData() {
    const data = {
      profile: profileForm.getValues(),
      notifications: notificationForm.getValues(),
      accessibility: accessibilityForm.getValues(),
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `studyos-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    notifySuccess("Data exported successfully");
  }

  if (!mounted) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your profile, notifications, and preferences.
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="language" className="flex items-center gap-2">
            <Languages className="h-4 w-4" />
            Language
          </TabsTrigger>
          <TabsTrigger value="accessibility" className="flex items-center gap-2">
            <Accessibility className="h-4 w-4" />
            Accessibility
          </TabsTrigger>
          <TabsTrigger value="shortcuts" className="flex items-center gap-2">
            <Keyboard className="h-4 w-4" />
            Shortcuts
          </TabsTrigger>
          <TabsTrigger value="data" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Data
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <FormProvider {...profileForm}>
            <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-4 max-w-md">
              <FormField<ProfileValues> name="displayName" label="Full name">
                <Input {...profileForm.register("displayName")} />
              </FormField>

              <FormField<ProfileValues> name="email" label="Email">
                <Input type="email" {...profileForm.register("email")} disabled />
              </FormField>

              <Button type="submit" disabled={profileForm.formState.isSubmitting}>
                Save changes
              </Button>
            </form>
          </FormProvider>
        </TabsContent>

        <TabsContent value="notifications">
          <FormProvider {...notificationForm}>
            <form onSubmit={notificationForm.handleSubmit(onNotificationSubmit)} className="space-y-6 max-w-md">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Email notifications</Label>
                    <p className="text-xs text-muted-foreground">Receive study updates via email</p>
                  </div>
                  <Switch
                    checked={notificationForm.watch("emailNotifications")}
                    onCheckedChange={(v) => notificationForm.setValue("emailNotifications", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Study reminders</Label>
                    <p className="text-xs text-muted-foreground">Daily reminders to study</p>
                  </div>
                  <Switch
                    checked={notificationForm.watch("studyReminders")}
                    onCheckedChange={(v) => notificationForm.setValue("studyReminders", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Streak alerts</Label>
                    <p className="text-xs text-muted-foreground">Alert when your streak is at risk</p>
                  </div>
                  <Switch
                    checked={notificationForm.watch("streakAlerts")}
                    onCheckedChange={(v) => notificationForm.setValue("streakAlerts", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Weekly report</Label>
                    <p className="text-xs text-muted-foreground">Summary of your weekly progress</p>
                  </div>
                  <Switch
                    checked={notificationForm.watch("weeklyReport")}
                    onCheckedChange={(v) => notificationForm.setValue("weeklyReport", v)}
                  />
                </div>
              </div>

              <Button type="submit" disabled={notificationForm.formState.isSubmitting}>
                Save preferences
              </Button>
            </form>
          </FormProvider>
        </TabsContent>

        <TabsContent value="appearance">
          <div className="space-y-4 max-w-md">
            <div>
              <Label>Theme</Label>
              <p className="text-xs text-muted-foreground mb-2">Choose your preferred appearance</p>
              <Select value={theme} onValueChange={setTheme}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="language">
          <div className="space-y-4 max-w-md">
            <div>
              <Label>Interface Language</Label>
              <p className="text-xs text-muted-foreground mb-2">
                Choose your preferred language for the interface
              </p>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  {LANGUAGES.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value}>
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="accessibility">
          <FormProvider {...accessibilityForm}>
            <form onSubmit={accessibilityForm.handleSubmit(onAccessibilitySubmit)} className="space-y-6 max-w-md">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Reduce motion</Label>
                    <p className="text-xs text-muted-foreground">Minimize animations and transitions</p>
                  </div>
                  <Switch
                    checked={accessibilityForm.watch("reduceMotion")}
                    onCheckedChange={(v) => accessibilityForm.setValue("reduceMotion", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>High contrast</Label>
                    <p className="text-xs text-muted-foreground">Increase contrast for better readability</p>
                  </div>
                  <Switch
                    checked={accessibilityForm.watch("highContrast")}
                    onCheckedChange={(v) => accessibilityForm.setValue("highContrast", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Large text</Label>
                    <p className="text-xs text-muted-foreground">Increase base font size</p>
                  </div>
                  <Switch
                    checked={accessibilityForm.watch("largeText")}
                    onCheckedChange={(v) => accessibilityForm.setValue("largeText", v)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Screen reader optimizations</Label>
                    <p className="text-xs text-muted-foreground">Enhanced ARIA labels and navigation</p>
                  </div>
                  <Switch
                    checked={accessibilityForm.watch("screenReader")}
                    onCheckedChange={(v) => accessibilityForm.setValue("screenReader", v)}
                  />
                </div>
              </div>

              <Button type="submit" disabled={accessibilityForm.formState.isSubmitting}>
                Save settings
              </Button>
            </form>
          </FormProvider>
        </TabsContent>

        <TabsContent value="shortcuts">
          <div className="space-y-4 max-w-md">
            <div>
              <Label>Keyboard Shortcuts</Label>
              <p className="text-xs text-muted-foreground mb-4">
                Quick actions you can perform with keyboard shortcuts
              </p>
              <div className="space-y-3">
                {[
                  { keys: "Ctrl + K", action: "Open command palette" },
                  { keys: "Ctrl + /", action: "Toggle help" },
                  { keys: "Ctrl + B", action: "Toggle sidebar" },
                  { keys: "Ctrl + N", action: "New note" },
                  { keys: "Ctrl + R", action: "Start revision session" },
                  { keys: "Esc", action: "Close modal / cancel" },
                ].map((shortcut) => (
                  <div key={shortcut.keys} className="flex items-center justify-between py-2">
                    <span className="text-sm">{shortcut.action}</span>
                    <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded border">
                      {shortcut.keys}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="data">
          <div className="space-y-4 max-w-md">
            <div>
              <Label>Export your data</Label>
              <p className="text-xs text-muted-foreground mb-2">
                Download all your study data, progress, and completions.
              </p>
              <Button variant="outline" onClick={handleExportData}>
                <Download className="mr-2 h-4 w-4" />
                Export data
              </Button>
            </div>

            <Separator />

            <div>
              <Label className="text-destructive">Delete account</Label>
              <p className="text-xs text-muted-foreground mb-2">
                Permanently delete your account and all associated data.
              </p>
              <Button variant="destructive" disabled>
                Delete account
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
