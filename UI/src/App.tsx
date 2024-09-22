import { Suspense, lazy } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import MainLayout from "@/layouts";
import Loading from "@/components/Loading";
import "./App.css";

const Dashboard = lazy(() => import("@/pages/dashboard"));
const AllData = lazy(() => import("@/pages/all-data"));
// const PageNotFound = lazy(() => import("@/components/PageNotFound"));

function App() {
  return (
    <Router>
      <Suspense fallback={<Loading />}>
        <Routes>
          <Route index element={<Navigate replace to="dashboard" />} />
          <Route element={<MainLayout />}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="all-data" element={<AllData />} />
          </Route>
          {/* <Route path="*" element={<PageNotFound />} /> */}
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
