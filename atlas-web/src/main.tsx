import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { AtlasLoading } from "./ui/AtlasLoading";
const App = lazy(() => import("./ui/App"));
createRoot(document.getElementById("root")!).render(<React.StrictMode><Suspense fallback={<AtlasLoading/>}><App /></Suspense></React.StrictMode>);
