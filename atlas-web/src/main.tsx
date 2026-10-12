import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { AtlasLoading } from "./ui/AtlasLoading";
const isReview = import.meta.env.DEV && window.location.pathname === "/review";
const isTerritoryReview = isReview && new URLSearchParams(window.location.search).get('territories') === '1';
const App = isReview && !isTerritoryReview ? lazy(() => import("./ui/ReviewApp")) : lazy(() => import("./ui/App"));
createRoot(document.getElementById("root")!).render(<React.StrictMode><Suspense fallback={<AtlasLoading/>}><App /></Suspense></React.StrictMode>);
