import { z } from "zod";

export const loginFormSchema = z.object({
  email: z.string().email("Enter a valid email").max(320),
  password: z.string().min(1, "Password is required").max(256),
});

export type LoginFormValues = z.infer<typeof loginFormSchema>;

export const signupFormSchema = z.object({
  email: z.string().email("Enter a valid email").max(320),
  password: z.string().min(8, "At least 8 characters").max(256),
  displayName: z.string().min(1, "Name is required").max(100),
  terms: z.boolean().refine((val) => val === true, "Accept terms to continue"),
});

export type SignupFormValues = z.infer<typeof signupFormSchema>;
