import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Sun, Moon, Monitor } from 'lucide-react';

interface ThemeToggleProps {
  variant?: 'toggle' | 'dropdown';
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  variant = 'toggle',
  className = ''
}) => {
  const { theme, setTheme, resolvedTheme } = useTheme();

  if (variant === 'dropdown') {
    return (
      <select
        value={theme}
        onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors ${className}`}
      >
        <option value="light">🌞 明亮模式</option>
        <option value="dark">🌙 暗黑模式</option>
        <option value="system">🖥️ 跟随系统</option>
      </select>
    );
  }

  // 简单的切换按钮
  const getIcon = () => {
    if (theme === 'system') {
      return <Monitor size={16} />;
    }
    return resolvedTheme === 'dark' ? <Moon size={16} /> : <Sun size={16} />;
  };

  const getLabelText = () => {
    if (theme === 'system') {
      return '跟随系统';
    }
    return resolvedTheme === 'dark' ? '暗黑模式' : '明亮模式';
  };

  return (
    <button
      onClick={() => {
        if (theme === 'light') {
          setTheme('dark');
        } else if (theme === 'dark') {
          setTheme('system');
        } else {
          setTheme('light');
        }
      }}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 ${className}`}
      title={`当前: ${getLabelText()}`}
    >
      {getIcon()}
    </button>
  );
};

export default ThemeToggle;