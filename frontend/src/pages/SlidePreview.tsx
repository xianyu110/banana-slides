import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import {
  Home,
  ArrowLeft,
  Download,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Button, Loading, Modal, Textarea, useToast, useConfirm } from '@/components/shared';
import { SlideCard } from '@/components/preview/SlideCard';
import { useProjectStore } from '@/store/useProjectStore';
import { getImageUrl } from '@/api/client';
import { getPageImageVersions, setCurrentImageVersion } from '@/api/endpoints';
import type { ImageVersion } from '@/types';

export const SlidePreview: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams<{ projectId: string }>();
  const fromHistory = (location.state as any)?.from === 'history';
  const {
    currentProject,
    syncProject,
    generateImages,
    generatePageImage,
    editPageImage,
    deletePageById,
    exportPPTX,
    exportPDF,
    isGlobalLoading,
    taskProgress,
    pageGeneratingTasks,
  } = useProjectStore();

  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editPrompt, setEditPrompt] = useState('');
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [isOutlineExpanded, setIsOutlineExpanded] = useState(false);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [imageVersions, setImageVersions] = useState<ImageVersion[]>([]);
  const [showVersionMenu, setShowVersionMenu] = useState(false);
  const { show, ToastContainer } = useToast();
  const { confirm, ConfirmDialog } = useConfirm();

  // 加载项目数据
  useEffect(() => {
    if (projectId && (!currentProject || currentProject.id !== projectId)) {
      // 直接使用 projectId 同步项目数据
      syncProject(projectId);
    }
  }, [projectId, currentProject, syncProject]);

  // 加载当前页面的历史版本
  useEffect(() => {
    const loadVersions = async () => {
      if (!currentProject || !projectId || selectedIndex < 0 || selectedIndex >= currentProject.pages.length) {
        setImageVersions([]);
        setShowVersionMenu(false);
        return;
      }

      const page = currentProject.pages[selectedIndex];
      if (!page?.id) {
        setImageVersions([]);
        setShowVersionMenu(false);
        return;
      }

      try {
        const response = await getPageImageVersions(projectId, page.id);
        if (response.data?.versions) {
          setImageVersions(response.data.versions);
        }
      } catch (error) {
        console.error('Failed to load image versions:', error);
        setImageVersions([]);
      }
    };

    loadVersions();
  }, [currentProject, selectedIndex, projectId]);

  const handleGenerateAll = async () => {
    const hasImages = currentProject?.pages.some(
      (p) => p.generated_image_path
    );
    
    const executeGenerate = async () => {
      await generateImages();
    };
    
    if (hasImages) {
      confirm(
        '部分页面已有图片，重新生成将覆盖，确定继续吗？',
        executeGenerate,
        { title: '确认重新生成', variant: 'warning' }
      );
    } else {
      await executeGenerate();
    }
  };

  const handleRegeneratePage = async () => {
    if (!currentProject) return;
    const page = currentProject.pages[selectedIndex];
    if (!page.id) return;
    
    // 如果该页面正在生成，不重复提交
    if (pageGeneratingTasks[page.id]) {
      show({ message: '该页面正在生成中，请稍候...', type: 'info' });
      return;
    }
    
    // 如果已有图片，需要传递 force_regenerate=true
    const hasImage = !!page.generated_image_path;
    
    try {
      await generatePageImage(page.id, hasImage);
      show({ message: '已开始生成图片，请稍候...', type: 'success' });
    } catch (error: any) {
      show({ 
        message: `生成失败: ${error.message || '未知错误'}`, 
        type: 'error' 
      });
    }
  };

  const handleSwitchVersion = async (versionId: string) => {
    if (!currentProject || !selectedPage?.id || !projectId) return;
    
    try {
      await setCurrentImageVersion(projectId, selectedPage.id, versionId);
      await syncProject(projectId);
      setShowVersionMenu(false);
      show({ message: '已切换到该版本', type: 'success' });
    } catch (error: any) {
      show({ 
        message: `切换失败: ${error.message || '未知错误'}`, 
        type: 'error' 
      });
    }
  };

  const handleEditPage = () => {
    setEditPrompt('');
    setIsOutlineExpanded(false);
    setIsDescriptionExpanded(false);
    setIsEditModalOpen(true);
  };

  const handleSubmitEdit = async () => {
    if (!currentProject || !editPrompt.trim()) return;
    
    const page = currentProject.pages[selectedIndex];
    if (!page.id) return;
    await editPageImage(page.id, editPrompt);
    setIsEditModalOpen(false);
  };

  const handleExport = async (type: 'pptx' | 'pdf') => {
    setShowExportMenu(false);
    if (type === 'pptx') {
      await exportPPTX();
    } else {
      await exportPDF();
    }
  };

  const handleRefresh = async () => {
    const targetProjectId = projectId || currentProject?.id;
    if (!targetProjectId) {
      show({ message: '无法刷新：缺少项目ID', type: 'error' });
      return;
    }

    setIsRefreshing(true);
    try {
      await syncProject(targetProjectId);
      show({ message: '刷新成功', type: 'success' });
    } catch (error: any) {
      show({ 
        message: error.message || '刷新失败，请稍后重试', 
        type: 'error' 
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!currentProject) {
    return <Loading fullscreen message="加载项目中..." />;
  }

  if (isGlobalLoading) {
    return (
      <Loading
        fullscreen
        message="生成图片中..."
        progress={taskProgress || undefined}
      />
    );
  }

  const selectedPage = currentProject.pages[selectedIndex];
  const imageUrl = selectedPage?.generated_image_path
    ? getImageUrl(selectedPage.generated_image_path, selectedPage.updated_at)
    : '';

  const hasAllImages = currentProject.pages.every(
    (p) => p.generated_image_path
  );

  return (
    <div className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      {/* 顶栏 */}
      <header className="h-16 bg-white shadow-sm border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            icon={<Home size={18} />}
            onClick={() => navigate('/')}
          >
            主页
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowLeft size={18} />}
            onClick={() => {
              if (fromHistory) {
                navigate('/history');
              } else {
                navigate(`/project/${projectId}/detail`);
              }
            }}
          >
            返回
          </Button>
          <div className="flex items-center gap-2">
            <span className="text-2xl">🍌</span>
            <span className="text-xl font-bold">蕉幻</span>
          </div>
          <span className="text-gray-400">|</span>
          <span className="text-lg font-semibold">预览</span>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            icon={<ArrowLeft size={18} />}
            onClick={() => navigate(`/project/${projectId}/detail`)}
          >
            上一步
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={<RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            刷新
          </Button>
          <div className="relative">
            <Button
              variant="primary"
              size="sm"
              icon={<Download size={18} />}
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={!hasAllImages}
            >
              导出
            </Button>
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10">
                <button
                  onClick={() => handleExport('pptx')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                >
                  导出为 PPTX
                </button>
                <button
                  onClick={() => handleExport('pdf')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                >
                  导出为 PDF
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden min-w-0 min-h-0">
        {/* 左侧：缩略图列表 */}
        <aside className="w-80 bg-white border-r border-gray-200 flex flex-col flex-shrink-0">
          <div className="p-4 border-b border-gray-200 flex-shrink-0">
            <Button
              variant="primary"
              icon={<Sparkles size={18} />}
              onClick={handleGenerateAll}
              className="w-full"
            >
              批量生成图片 ({currentProject.pages.length})
            </Button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {currentProject.pages.map((page, index) => (
              <SlideCard
                key={page.id}
                page={page}
                index={index}
                isSelected={selectedIndex === index}
                onClick={() => setSelectedIndex(index)}
                onEdit={() => {
                  setSelectedIndex(index);
                  handleEditPage();
                }}
                onDelete={() => page.id && deletePageById(page.id)}
                isGenerating={page.id ? !!pageGeneratingTasks[page.id] : false}
              />
            ))}
          </div>
        </aside>

        {/* 右侧：大图预览 */}
        <main className="flex-1 flex flex-col bg-gradient-to-br from-banana-50 via-white to-gray-50 min-w-0 overflow-hidden">
          {currentProject.pages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center overflow-y-auto">
              <div className="text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  还没有页面
                </h3>
                <p className="text-gray-500 mb-6">
                  请先返回编辑页面添加内容
                </p>
                <Button
                  variant="primary"
                  onClick={() => navigate(`/project/${projectId}/outline`)}
                >
                  返回编辑
                </Button>
              </div>
            </div>
          ) : (
            <>
              {/* 预览区 */}
              <div className="flex-1 overflow-y-auto min-h-0 flex items-center justify-center p-8">
                <div className="max-w-5xl w-full">
                  <div className="relative aspect-video bg-white rounded-lg shadow-xl overflow-hidden">
                    {selectedPage?.generated_image_path ? (
                      <img
                        src={imageUrl}
                        alt={`Slide ${selectedIndex + 1}`}
                        className="w-full h-full object-contain"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-100">
                        <div className="text-center">
                          <div className="text-6xl mb-4">🖼️</div>
                          <p className="text-gray-500 mb-4">
                            {selectedPage?.id && pageGeneratingTasks[selectedPage.id]
                              ? '正在生成中...'
                              : selectedPage?.status === 'GENERATING'
                              ? '正在生成中...'
                              : '尚未生成图片'}
                          </p>
                          {(!selectedPage?.id || !pageGeneratingTasks[selectedPage.id]) && 
                           selectedPage?.status !== 'GENERATING' && (
                            <Button
                              variant="primary"
                              onClick={handleRegeneratePage}
                            >
                              生成此页
                            </Button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* 控制栏 */}
              <div className="bg-white border-t border-gray-200 px-6 py-4 flex-shrink-0">
                <div className="flex items-center justify-between max-w-5xl mx-auto">
                  {/* 导航 */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<ChevronLeft size={18} />}
                      onClick={() => setSelectedIndex(Math.max(0, selectedIndex - 1))}
                      disabled={selectedIndex === 0}
                    >
                      上一页
                    </Button>
                    <span className="px-4 text-sm text-gray-600">
                      {selectedIndex + 1} / {currentProject.pages.length}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<ChevronRight size={18} />}
                      onClick={() =>
                        setSelectedIndex(
                          Math.min(currentProject.pages.length - 1, selectedIndex + 1)
                        )
                      }
                      disabled={selectedIndex === currentProject.pages.length - 1}
                    >
                      下一页
                    </Button>
                  </div>

                  {/* 操作 */}
                  <div className="flex items-center gap-2">
                    {imageVersions.length > 1 && (
                      <div className="relative">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowVersionMenu(!showVersionMenu)}
                        >
                          历史版本 ({imageVersions.length})
                        </Button>
                        {showVersionMenu && (
                          <div className="absolute right-0 bottom-full mb-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-20 max-h-96 overflow-y-auto">
                            {imageVersions.map((version) => (
                              <button
                                key={version.version_id}
                                onClick={() => handleSwitchVersion(version.version_id)}
                                className={`w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center justify-between ${
                                  version.is_current ? 'bg-banana-50' : ''
                                }`}
                              >
                                <div className="flex items-center gap-2">
                                  <span className="text-sm">
                                    版本 {version.version_number}
                                  </span>
                                  {version.is_current && (
                                    <span className="text-xs text-banana-600 font-medium">
                                      (当前)
                                    </span>
                                  )}
                                </div>
                                <span className="text-xs text-gray-400">
                                  {version.created_at
                                    ? new Date(version.created_at).toLocaleString('zh-CN', {
                                        month: 'short',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                      })
                                    : ''}
                                </span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleEditPage}
                      disabled={!selectedPage?.generated_image_path}
                    >
                      编辑
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleRegeneratePage}
                      disabled={selectedPage?.id && pageGeneratingTasks[selectedPage.id] ? true : false}
                    >
                      {selectedPage?.id && pageGeneratingTasks[selectedPage.id]
                        ? '生成中...'
                        : '重新生成'}
                    </Button>
                  </div>
                </div>
              </div>
            </>
          )}
        </main>
      </div>

      {/* 编辑对话框 */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="编辑页面"
        size="lg"
      >
        <div className="space-y-4">
          {/* 图片 */}
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
            {imageUrl && (
              <img
                src={imageUrl}
                alt="Current slide"
                className="w-full h-full object-contain"
              />
            )}
          </div>

          {/* 大纲内容 - 可折叠 */}
          {selectedPage?.outline_content && (
            <div className="bg-gray-50 rounded-lg border border-gray-200">
              <button
                onClick={() => setIsOutlineExpanded(!isOutlineExpanded)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100 transition-colors"
              >
                <h4 className="text-sm font-semibold text-gray-700">页面大纲</h4>
                {isOutlineExpanded ? (
                  <ChevronUp size={18} className="text-gray-500" />
                ) : (
                  <ChevronDown size={18} className="text-gray-500" />
                )}
              </button>
              {isOutlineExpanded && (
                <div className="px-4 pb-4 space-y-2">
                  <div className="text-sm font-medium text-gray-900">
                    {selectedPage.outline_content.title}
                  </div>
                  {selectedPage.outline_content.points && selectedPage.outline_content.points.length > 0 && (
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                      {selectedPage.outline_content.points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )}

          {/* 描述内容 - 可折叠 */}
          {selectedPage?.description_content && (
            <div className="bg-blue-50 rounded-lg border border-blue-200">
              <button
                onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-blue-100 transition-colors"
              >
                <h4 className="text-sm font-semibold text-gray-700">页面描述</h4>
                {isDescriptionExpanded ? (
                  <ChevronUp size={18} className="text-gray-500" />
                ) : (
                  <ChevronDown size={18} className="text-gray-500" />
                )}
              </button>
              {isDescriptionExpanded && (
                <div className="px-4 pb-4">
                  <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {(selectedPage.description_content as any)?.text || 
                     (selectedPage.description_content as any)?.text_content?.join('\n') || 
                     '暂无描述'}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 编辑框 */}
          <Textarea
            label="输入修改指令(将自动添加页面描述)"
            placeholder="例如：把背景改成蓝色、增大标题字号、更改文本框样式为虚线..."
            value={editPrompt}
            onChange={(e) => setEditPrompt(e.target.value)}
            rows={4}
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setIsEditModalOpen(false)}>
              取消
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmitEdit}
              disabled={!editPrompt.trim()}
            >
              生成
            </Button>
          </div>
        </div>
      </Modal>
      <ToastContainer />
      {ConfirmDialog}
    </div>
  );
};

