import { apiClient } from './client';

interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
}

interface SupportedLanguagesResponse {
  languages: Language[];
  default: string;
}

interface SetLanguageRequest {
  language: string;
}

interface SetLanguageResponse {
  success: boolean;
  message: string;
  language: string;
}

interface CurrentLanguageResponse {
  language: string;
  locale: string;
}

export const i18nApi = {
  /**
   * 获取支持的语言列表
   */
  async getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
    const response = await apiClient.get<SupportedLanguagesResponse>('/api/i18n/languages');
    return response.data;
  },

  /**
   * 设置用户语言偏好
   */
  async setLanguage(language: string): Promise<SetLanguageResponse> {
    const response = await apiClient.post<SetLanguageResponse>('/api/i18n/set-language', {
      language
    });
    return response.data;
  },

  /**
   * 获取当前语言设置
   */
  async getCurrentLanguage(): Promise<CurrentLanguageResponse> {
    const response = await apiClient.get<CurrentLanguageResponse>('/api/i18n/current');
    return response.data;
  }
};