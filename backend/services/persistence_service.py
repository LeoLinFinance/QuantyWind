"""
持久化存储服务
用于保存盯盘股票列表、系统提示词等配置数据
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class PersistenceService:
    """持久化存储服务"""
    
    def __init__(self):
        # 数据存储路径
        self.data_dir = Path('data/config')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 各类数据文件
        self.watchlist_file = self.data_dir / 'watchlist.json'
        self.system_prompt_file = self.data_dir / 'system_prompt.json'
        self.user_settings_file = self.data_dir / 'user_settings.json'
        
        print(f"✅ 持久化服务初始化完成，数据目录: {self.data_dir}")
    
    # ========================================================================
    # 盯盘股票列表
    # ========================================================================
    
    def save_watchlist(self, symbols: List[str]) -> bool:
        """
        保存盯盘股票列表
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                'symbols': symbols,
                'updated_at': datetime.now().isoformat(),
                'count': len(symbols)
            }
            
            with open(self.watchlist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 盯盘列表已保存: {len(symbols)} 只股票")
            return True
            
        except Exception as e:
            print(f"❌ 保存盯盘列表失败: {e}")
            return False
    
    def load_watchlist(self) -> List[str]:
        """
        加载盯盘股票列表
        
        Returns:
            股票代码列表
        """
        try:
            if not self.watchlist_file.exists():
                print("ℹ️ 盯盘列表文件不存在，返回空列表")
                return []
            
            with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            symbols = data.get('symbols', [])
            print(f"✅ 盯盘列表已加载: {len(symbols)} 只股票")
            return symbols
            
        except Exception as e:
            print(f"❌ 加载盯盘列表失败: {e}")
            return []

    
    def add_to_watchlist(self, symbol: str) -> bool:
        """
        添加股票到盯盘列表
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否添加成功
        """
        symbols = self.load_watchlist()
        
        if symbol in symbols:
            print(f"ℹ️ {symbol} 已在盯盘列表中")
            return False
        
        symbols.append(symbol)
        return self.save_watchlist(symbols)
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """
        从盯盘列表移除股票
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否移除成功
        """
        symbols = self.load_watchlist()
        
        if symbol not in symbols:
            print(f"ℹ️ {symbol} 不在盯盘列表中")
            return False
        
        symbols.remove(symbol)
        return self.save_watchlist(symbols)
    
    # ========================================================================
    # 系统提示词
    # ========================================================================
    
    def save_system_prompt(self, prompt: str) -> bool:
        """
        保存系统提示词
        
        Args:
            prompt: 提示词内容
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                'prompt': prompt,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.system_prompt_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 系统提示词已保存")
            return True
            
        except Exception as e:
            print(f"❌ 保存系统提示词失败: {e}")
            return False
    
    def load_system_prompt(self) -> Optional[str]:
        """
        加载系统提示词
        
        Returns:
            提示词内容，如果不存在则返回None
        """
        try:
            if not self.system_prompt_file.exists():
                print("ℹ️ 系统提示词文件不存在")
                return None
            
            with open(self.system_prompt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            prompt = data.get('prompt')
            print(f"✅ 系统提示词已加载")
            return prompt
            
        except Exception as e:
            print(f"❌ 加载系统提示词失败: {e}")
            return None
    
    # ========================================================================
    # 用户设置
    # ========================================================================
    
    def save_user_settings(self, settings: Dict) -> bool:
        """
        保存用户设置
        
        Args:
            settings: 设置字典
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                'settings': settings,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.user_settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 用户设置已保存")
            return True
            
        except Exception as e:
            print(f"❌ 保存用户设置失败: {e}")
            return False
    
    def load_user_settings(self) -> Dict:
        """
        加载用户设置
        
        Returns:
            设置字典
        """
        try:
            if not self.user_settings_file.exists():
                print("ℹ️ 用户设置文件不存在，返回默认设置")
                return {}
            
            with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            settings = data.get('settings', {})
            print(f"✅ 用户设置已加载")
            return settings
            
        except Exception as e:
            print(f"❌ 加载用户设置失败: {e}")
            return {}
    
    def update_user_setting(self, key: str, value) -> bool:
        """
        更新单个用户设置
        
        Args:
            key: 设置键
            value: 设置值
        
        Returns:
            是否更新成功
        """
        settings = self.load_user_settings()
        settings[key] = value
        return self.save_user_settings(settings)
    
    # ========================================================================
    # 工具方法
    # ========================================================================
    
    def get_all_data_info(self) -> Dict:
        """
        获取所有持久化数据的信息
        
        Returns:
            数据信息字典
        """
        info = {
            'watchlist': {
                'exists': self.watchlist_file.exists(),
                'count': len(self.load_watchlist()) if self.watchlist_file.exists() else 0
            },
            'system_prompt': {
                'exists': self.system_prompt_file.exists(),
                'has_content': bool(self.load_system_prompt()) if self.system_prompt_file.exists() else False
            },
            'user_settings': {
                'exists': self.user_settings_file.exists(),
                'count': len(self.load_user_settings()) if self.user_settings_file.exists() else 0
            }
        }
        return info
    
    def clear_all_data(self) -> bool:
        """
        清除所有持久化数据（慎用）
        
        Returns:
            是否清除成功
        """
        try:
            if self.watchlist_file.exists():
                self.watchlist_file.unlink()
            if self.system_prompt_file.exists():
                self.system_prompt_file.unlink()
            if self.user_settings_file.exists():
                self.user_settings_file.unlink()
            
            print("✅ 所有持久化数据已清除")
            return True
            
        except Exception as e:
            print(f"❌ 清除数据失败: {e}")
            return False
