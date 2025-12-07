/**
 * IndexedDB数据库服务
 * 使用Dexie封装IndexedDB，替代后端SQLite
 */
import Dexie, { Table } from 'dexie';
import type { Project, Page, ImageVersion } from '@/types';

// 素材接口
export interface Material {
  id: string;
  project_id?: string | null;
  filename: string;
  blob: Blob; // 存储文件内容
  url?: string; // 临时URL
  relative_path: string;
  created_at: string;
  prompt?: string;
  original_filename?: string;
  source_filename?: string;
  name?: string;
}

// 用户模板接口
export interface UserTemplate {
  template_id: string;
  name?: string;
  blob: Blob; // 存储模板图片
  template_image_url?: string; // 临时URL
  created_at: string;
  updated_at: string;
}

// API配置接口
export interface APISettings {
  id: string; // 固定为'default'
  text_api_key: string;
  text_api_base: string;
  image_api_key: string;
  image_api_base: string;
  updated_at: string;
}

// 定义数据库类
export class BananaSlidesDB extends Dexie {
  projects!: Table<Project, string>;
  pages!: Table<Page, string>;
  imageVersions!: Table<ImageVersion, string>;
  materials!: Table<Material, string>;
  userTemplates!: Table<UserTemplate, string>;
  settings!: Table<APISettings, string>;

  constructor() {
    super('BananaSlidesDB');

    // 定义数据库schema
    this.version(1).stores({
      projects: 'project_id, created_at, updated_at',
      pages: 'page_id, project_id, order_index',
      imageVersions: 'version_id, page_id, version_number, is_current',
      materials: 'id, project_id, created_at',
      userTemplates: 'template_id, created_at',
      settings: 'id', // 只存储一条记录，id固定为'default'
    });
  }
}

// 创建数据库实例
export const db = new BananaSlidesDB();

// ===== 项目相关操作 =====

/**
 * 创建项��
 */
export const createProject = async (project: Omit<Project, 'created_at' | 'updated_at'>): Promise<Project> => {
  const now = new Date().toISOString();
  const newProject: Project = {
    ...project,
    created_at: now,
    updated_at: now,
  };

  await db.projects.add(newProject);

  // 同时保存pages
  if (newProject.pages && newProject.pages.length > 0) {
    await db.pages.bulkAdd(newProject.pages);
  }

  return newProject;
};

/**
 * 获取项目列表
 */
export const listProjects = async (limit?: number, offset?: number): Promise<{ projects: Project[]; total: number }> => {
  const total = await db.projects.count();

  let query = db.projects.orderBy('updated_at').reverse();

  if (offset !== undefined) {
    query = query.offset(offset);
  }

  if (limit !== undefined) {
    query = query.limit(limit);
  }

  const projects = await query.toArray();

  // 加载每个项目的pages
  for (const project of projects) {
    project.pages = await db.pages
      .where('project_id')
      .equals(project.project_id)
      .sortBy('order_index');
  }

  return { projects, total };
};

/**
 * 获取单个项目
 */
export const getProject = async (projectId: string): Promise<Project | undefined> => {
  const project = await db.projects.get(projectId);

  if (project) {
    // 加载项目的pages
    project.pages = await db.pages
      .where('project_id')
      .equals(projectId)
      .sortBy('order_index');
  }

  return project;
};

/**
 * 更新项目
 */
export const updateProject = async (projectId: string, data: Partial<Project>): Promise<Project | undefined> => {
  await db.projects.update(projectId, {
    ...data,
    updated_at: new Date().toISOString(),
  });

  return getProject(projectId);
};

/**
 * 删除项目
 */
export const deleteProject = async (projectId: string): Promise<void> => {
  // 删除项目的所有pages
  await db.pages.where('project_id').equals(projectId).delete();

  // 删除项目
  await db.projects.delete(projectId);
};

// ===== 页面相关操作 =====

/**
 * 创建页面
 */
export const createPage = async (page: Page): Promise<Page> => {
  await db.pages.add(page);
  return page;
};

/**
 * 更新页面
 */
export const updatePage = async (pageId: string, data: Partial<Page>): Promise<Page | undefined> => {
  await db.pages.update(pageId, {
    ...data,
    updated_at: new Date().toISOString(),
  });

  return db.pages.get(pageId);
};

/**
 * 删除页面
 */
export const deletePage = async (pageId: string): Promise<void> => {
  await db.pages.delete(pageId);

  // 删除页面的所有图片版本
  await db.imageVersions.where('page_id').equals(pageId).delete();
};

/**
 * 批量更新页面顺序
 */
export const updatePagesOrder = async (pageIds: string[]): Promise<void> => {
  await db.transaction('rw', db.pages, async () => {
    for (let i = 0; i < pageIds.length; i++) {
      await db.pages.update(pageIds[i], { order_index: i });
    }
  });
};

// ===== 素材相关操作 =====

/**
 * 添加素材
 */
export const addMaterial = async (material: Material): Promise<Material> => {
  await db.materials.add(material);
  return material;
};

/**
 * 获取素材列表
 */
export const listMaterials = async (projectId?: string | null): Promise<Material[]> => {
  if (!projectId || projectId === 'all') {
    // 获取所有素材
    return db.materials.orderBy('created_at').reverse().toArray();
  } else if (projectId === 'none') {
    // 获取全局素材（不绑定项目）
    return db.materials.where('project_id').equals(null as any).toArray();
  } else {
    // 获取特定项目的素材
    return db.materials.where('project_id').equals(projectId).toArray();
  }
};

/**
 * 删除素材
 */
export const deleteMaterial = async (materialId: string): Promise<void> => {
  const material = await db.materials.get(materialId);
  if (material && material.url) {
    // 释放Blob URL
    URL.revokeObjectURL(material.url);
  }
  await db.materials.delete(materialId);
};

// ===== 用户模板相关操作 =====

/**
 * 添加用户模板
 */
export const addUserTemplate = async (template: UserTemplate): Promise<UserTemplate> => {
  await db.userTemplates.add(template);
  return template;
};

/**
 * 获取用户模板列表
 */
export const listUserTemplates = async (): Promise<UserTemplate[]> => {
  return db.userTemplates.orderBy('created_at').reverse().toArray();
};

/**
 * 删除用户模板
 */
export const deleteUserTemplate = async (templateId: string): Promise<void> => {
  const template = await db.userTemplates.get(templateId);
  if (template && template.template_image_url) {
    // 释放Blob URL
    URL.revokeObjectURL(template.template_image_url);
  }
  await db.userTemplates.delete(templateId);
};

// ===== API设置相关操作 =====

/**
 * 获取API设置
 */
export const getAPISettings = async (): Promise<APISettings | undefined> => {
  return db.settings.get('default');
};

/**
 * 更新API设置
 */
export const updateAPISettings = async (settings: Partial<Omit<APISettings, 'id'>>): Promise<APISettings> => {
  const now = new Date().toISOString();
  const existing = await db.settings.get('default');

  const newSettings: APISettings = {
    id: 'default',
    text_api_key: settings.text_api_key || existing?.text_api_key || '',
    text_api_base: settings.text_api_base || existing?.text_api_base || '',
    image_api_key: settings.image_api_key || existing?.image_api_key || '',
    image_api_base: settings.image_api_base || existing?.image_api_base || '',
    updated_at: now,
  };

  await db.settings.put(newSettings);
  return newSettings;
};

// ===== 工具函数 =====

/**
 * 创建Blob URL
 */
export const createBlobURL = (blob: Blob): string => {
  return URL.createObjectURL(blob);
};

/**
 * 清除所有数据（用于测试或重置）
 */
export const clearAllData = async (): Promise<void> => {
  await db.transaction('rw', [db.projects, db.pages, db.imageVersions, db.materials, db.userTemplates], async () => {
    await db.projects.clear();
    await db.pages.clear();
    await db.imageVersions.clear();
    await db.materials.clear();
    await db.userTemplates.clear();
  });
};

export default db;
