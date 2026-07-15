import { useFormContext } from "react-hook-form";
import { Button, type ButtonProps } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";

interface FormSubmitButtonProps extends ButtonProps {
  loadingText?: string;
}

export function FormSubmitButton({
  children,
  loadingText = "Saving...",
  ...props
}: FormSubmitButtonProps) {
  const { formState } = useFormContext();

  return (
    <Button
      type="submit"
      disabled={formState.isSubmitting || props.disabled}
      {...props}
    >
      {formState.isSubmitting ? (
        <>
          <Spinner size="sm" />
          {loadingText}
        </>
      ) : (
        children
      )}
    </Button>
  );
}
