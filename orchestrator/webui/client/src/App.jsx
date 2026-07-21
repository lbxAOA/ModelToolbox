import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ModelIngestPage from "./pages/ModelIngestPage.jsx";
import ModelProviderPage from "./pages/ModelProviderPage.jsx";
import PipelinePage from "./pages/PipelinePage.jsx";
import ModelTrainingPage from "./pages/ModelTrainingPage.jsx";
import ModelMCPPage from "./pages/ModelMCPPage.jsx";
import ModelMemoryPage from "./pages/ModelMemoryPage.jsx";
import ModelSkillPage from "./pages/ModelSkillPage.jsx";
import ObsidianRagPage from "./pages/ObsidianRagPage.jsx";
import ModelOfficePage from "./pages/ModelOfficePage.jsx";
import JobsPage from "./pages/JobsPage.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ingest" element={<ModelIngestPage />} />
          <Route path="/provider" element={<ModelProviderPage />} />
          <Route path="/pipeline" element={<PipelinePage />} />
          <Route path="/training" element={<ModelTrainingPage />} />
          <Route path="/mcp" element={<ModelMCPPage />} />
          <Route path="/memory" element={<ModelMemoryPage />} />
          <Route path="/skill" element={<ModelSkillPage />} />
          <Route path="/obsidian" element={<ObsidianRagPage />} />
          <Route path="/office" element={<ModelOfficePage />} />
          <Route path="/jobs" element={<JobsPage />} />
        </Routes>
      </div>
    </div>
  );
}
