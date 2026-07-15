import { toast } from "sonner";

import { ApiError } from "../api/http";
import { pickProblemMessage } from "./toast-helpers";

export function notifySuccess(message: string) {
  toast.success(message);
}

export function notifyError(message: string) {
  toast.error(message);
}

export function notifyInfo(message: string) {
  toast.message(message);
}

/** Maps unknown errors (including `ApiError`) to user-visible toast copy. */
export function notifyFromUnknown(err: unknown, fallback = "Something went wrong") {
  if (err instanceof ApiError) {
    notifyError(pickProblemMessage(err.body) ?? err.message ?? fallback);
    return;
  }
  if (err instanceof Error) {
    notifyError(err.message || fallback);
    return;
  }
  notifyError(fallback);
}
