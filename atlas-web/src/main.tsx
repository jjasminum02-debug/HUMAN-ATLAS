import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
const isReview = import.meta.env.DEV && window.location.pathname === "/review";
const App = isReview ? lazy(() => import("./ui/ReviewApp")) : lazy(() => import("./ui/App"));
createRoot(document.getElementById("root")!).render(<React.StrictMode><Suspense fallback={<p>Human Atlas를 준비하고 있습니다…</p>}><App /></Suspense></React.StrictMode>);
