export function getErrorMessage(err: unknown): string {
  if (!err) return "Unknown error";

  if (typeof err === "string") return err;

  if (err instanceof Error) return err.message || "Unexpected error";

  try {
    return JSON.stringify(err);
  } catch {
    return "Unexpected error";
  }
}
