import { redirect } from "next/navigation";

/**
 * The root route has no content of its own — it always sends visitors
 * into the app. `(app)/layout.tsx`'s auth guard is what decides
 * whether that lands on `/dashboard` or bounces further to `/login`;
 * this stays a single, unconditional redirect rather than duplicating
 * that auth check here too.
 */
export default function Home() {
  redirect("/dashboard");
}
