import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { History } from './pages/History';
import { OutlineEditor } from './pages/OutlineEditor';
import { DetailEditor } from './pages/DetailEditor';
import { SlidePreview } from './pages/SlidePreview';
import { Auth } from './pages/Auth';
import { useProjectStore } from './store/useProjectStore';
import { Loading, useToast } from './components/shared';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  const { currentProject, syncProject, error, setError } = useProjectStore();
  const { show, ToastContainer } = useToast();

  // 恢复项目状态
  useEffect(() => {
    const savedProjectId = localStorage.getItem('currentProjectId');
    if (savedProjectId && !currentProject) {
      syncProject();
    }
  }, []);

  // 显示全局错误
  useEffect(() => {
    if (error) {
      show({ message: error, type: 'error' });
      setError(null);
    }
  }, [error, setError, show]);

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/history" element={<History />} />
          <Route path="/project/:projectId/outline" element={<OutlineEditor />} />
          <Route path="/project/:projectId/detail" element={<DetailEditor />} />
          <Route path="/project/:projectId/preview" element={<SlidePreview />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ToastContainer />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;

