import React, { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // 从 localStorage 读取保存的主题设置
    const savedTheme = localStorage.getItem('theme') as Theme;
    return savedTheme || 'system';
  });

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  // 获取系统主题
  const getSystemTheme = (): 'light' | 'dark' => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  };

  // 解析最终应用的主题
  const resolveTheme = (themeSetting: Theme): 'light' | 'dark' => {
    if (themeSetting === 'system') {
      return getSystemTheme();
    }
    return themeSetting;
  };

  // 设置主题
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);

    const resolved = resolveTheme(newTheme);
    setResolvedTheme(resolved);

    // 更新 HTML 类名
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      if (resolved === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  };

  // 切换主题（在 light 和 dark 之间切换）
  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('light');
    } else {
      // 如果是 system，切换到与当前系统主题相反的主题
      const systemTheme = getSystemTheme();
      setTheme(systemTheme === 'light' ? 'dark' : 'light');
    }
  };

  // 监听系统主题变化
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

      const handleChange = () => {
        if (theme === 'system') {
          const resolved = resolveTheme('system');
          setResolvedTheme(resolved);

          const root = document.documentElement;
          if (resolved === 'dark') {
            root.classList.add('dark');
          } else {
            root.classList.remove('dark');
          }
        }
      };

      // 监听系统主题变化
      mediaQuery.addEventListener('change', handleChange);

      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, [theme]);

  // 初始化主题
  useEffect(() => {
    const resolved = resolveTheme(theme);
    setResolvedTheme(resolved);

    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      if (resolved === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  }, []);

  const value: ThemeContextType = {
    theme,
    resolvedTheme,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};