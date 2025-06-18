"""
OpenAI LLM 服務
用於 prompt 優化和文字生成
"""

import os
import re
from typing import Dict, List, Union
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 嘗試導入 OpenAI SDK
try:
    import openai
    OPENAI_AVAILABLE = True
    print("✅ OpenAI SDK 可用")
except ImportError as e:
    print(f"⚠️ OpenAI SDK 不可用: {e}")
    print("💡 請執行: pip install openai")
    OPENAI_AVAILABLE = False
    
    # 創建模擬的 OpenAI 類別
    class openai:
        class OpenAI:
            def __init__(self, api_key=None):
                raise Exception("OpenAI SDK 不可用")

class OpenAILLMService:
    """OpenAI LLM 服務類別"""
    
    def __init__(self, api_key: str = None, model_name: str = None):
        """初始化 OpenAI LLM 服務"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model_name = model_name or os.getenv('OPENAI_TEXT_GEN_MODEL', 'gpt-4')
        self.use_mock = False
        
        if not OPENAI_AVAILABLE:
            print("⚠️ OpenAI SDK 不可用，將使用模擬模式")
            self.use_mock = True
            return
        
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY 未設定，將使用模擬模式")
            self.use_mock = True
            return
        
        try:
            # 初始化 OpenAI 客戶端
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f"✅ OpenAI LLM 服務已初始化")
            print(f"   模型: {self.model_name}")
            print(f"   API Key: {'已設定' if self.api_key else '未設定'}")
            
        except Exception as e:
            print(f"❌ OpenAI LLM 服務初始化失敗: {e}")
            self.use_mock = True
        
        # 敏感詞彙清單（基本版本）
        self.sensitive_keywords = [
            '暴力', '血腥', '恐怖', '仇恨', '歧視', '裸體', '色情', 
            '毒品', '武器', '爆炸', '自殺', '死亡', '傷害', '攻擊',
            'violence', 'blood', 'horror', 'hate', 'nude', 'porn',
            'drug', 'weapon', 'bomb', 'suicide', 'death', 'harm'
        ]
    
    def analyze_prompt_safety(self, prompt: str, content_type: str) -> Dict:
        """分析 prompt 的安全性"""
        if not prompt or not prompt.strip():
            return {'error': 'Prompt 不能為空'}
        
        prompt = prompt.strip()
        
        if self.use_mock:
            return self._mock_analyze_prompt_safety(prompt, content_type)
        
        # 基本敏感詞彙檢查
        has_sensitive_content = self._check_sensitive_keywords(prompt)
        
        if not has_sensitive_content:
            # 安全的 prompt，直接優化
            optimized_prompt = self._optimize_safe_prompt(prompt, content_type)
            return {
                'status': 'safe',
                'optimized_prompt': optimized_prompt,
                'improvements': self._get_improvements_explanation(prompt, optimized_prompt),
                'original_prompt': prompt
            }
        else:
            # 不安全的 prompt，生成替代建議
            suggestions = self._generate_alternative_prompts(prompt, content_type)
            return {
                'status': 'unsafe',
                'original_prompt': prompt,
                'risk_analysis': '檢測到可能被AI模型拒絕的內容，已為您提供安全的替代建議',
                'suggestions': suggestions
            }
    
    def _check_sensitive_keywords(self, prompt: str) -> bool:
        """檢查是否包含敏感詞彙"""
        prompt_lower = prompt.lower()
        
        for keyword in self.sensitive_keywords:
            if keyword.lower() in prompt_lower:
                return True
        
        return False
    
    def _optimize_safe_prompt(self, prompt: str, content_type: str) -> str:
        """優化安全的 prompt"""
        
        optimization_prompt = f"""
        作為一個專業的 {self._get_content_type_chinese(content_type)} 生成 prompt 優化專家，請優化以下用戶輸入的提示詞：

        原始提示詞：{prompt}

        請按以下要求優化：
        1. 保持用戶原始意圖和場景
        2. 使用更具體、描述性的詞彙
        3. 加入適當的技術參數（如光線、構圖、風格等）
        4. 確保語言流暢、結構清晰
        5. 適合用於 AI {self._get_content_type_chinese(content_type)}生成模型
        
        請直接返回優化後的提示詞，不要有額外的說明或格式。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的 AI 提示詞優化專家。"},
                    {"role": "user", "content": optimization_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI API 調用失敗: {e}")
            # 回退到基本優化
            return self._basic_prompt_optimization(prompt, content_type)
    
    def _generate_alternative_prompts(self, prompt: str, content_type: str) -> Dict:
        """生成替代建議 prompt"""
        
        suggestion_prompt = f"""
        作為AI內容生成安全專家，用戶的原始提示詞可能包含不適當內容："{prompt}"

        請生成三個不同安全級別的替代建議：

        建議A（最安全）：
        - 完全移除任何可能敏感的內容
        - 使用安全、正面的描述
        - 確保不會被任何AI模型拒絕
        - 盡可能保持原始場景意圖

        建議B（中等風險）：
        - 用間接、藝術化的方式表達
        - 保留部分原始創意元素
        - 可能包含輕微的戲劇化描述

        建議C（保留原意）：
        - 最大化保留用戶原始想法
        - 強化表達效果和視覺衝擊
        - 用更豐富的細節描述

        請按以下格式回答（每個建議直接給出優化後的提示詞）：
        建議A：[提示詞內容]
        建議B：[提示詞內容]
        建議C：[提示詞內容]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的 AI 內容安全專家和提示詞優化師。"},
                    {"role": "user", "content": suggestion_prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            return self._parse_suggestions(suggestions_text)
            
        except Exception as e:
            print(f"❌ OpenAI API 調用失敗: {e}")
            # 回退到基本建議
            return self._basic_alternative_suggestions(prompt, content_type)
    
    def _parse_suggestions(self, suggestions_text: str) -> Dict:
        """解析建議回應"""
        suggestions = {
            'option_a': {
                'title': '建議 A (最安全)',
                'prompt': '',
                'description': '移除所有敏感內容，確保完全安全'
            },
            'option_b': {
                'title': '建議 B (中等風險)',
                'prompt': '',
                'description': '藝術化表達，保留創意元素'
            },
            'option_c': {
                'title': '建議 C (保留原意)',
                'prompt': '',
                'description': '強化原始想法，豐富視覺描述'
            }
        }
        
        # 使用正則表達式提取建議
        pattern_a = r'建議A[：:]\s*(.+?)(?=建議B|$)'
        pattern_b = r'建議B[：:]\s*(.+?)(?=建議C|$)'
        pattern_c = r'建議C[：:]\s*(.+?)$'
        
        match_a = re.search(pattern_a, suggestions_text, re.DOTALL | re.IGNORECASE)
        match_b = re.search(pattern_b, suggestions_text, re.DOTALL | re.IGNORECASE)
        match_c = re.search(pattern_c, suggestions_text, re.DOTALL | re.IGNORECASE)
        
        if match_a:
            suggestions['option_a']['prompt'] = match_a.group(1).strip()
        
        if match_b:
            suggestions['option_b']['prompt'] = match_b.group(1).strip()
        
        if match_c:
            suggestions['option_c']['prompt'] = match_c.group(1).strip()
        
        return suggestions
    
    def _get_improvements_explanation(self, original: str, optimized: str) -> List[str]:
        """獲取改進說明"""
        improvements = []
        
        if len(optimized) > len(original):
            improvements.append("增加了更詳細的描述")
        
        if any(word in optimized.lower() for word in ['光線', '構圖', '風格', '色彩', '質感']):
            improvements.append("添加了技術參數")
        
        if any(word in optimized.lower() for word in ['專業', '高品質', '細節', '精緻']):
            improvements.append("提升了品質要求")
        
        if len(improvements) == 0:
            improvements.append("優化了語言表達")
        
        return improvements
    
    def _get_content_type_chinese(self, content_type: str) -> str:
        """獲取內容類型的中文名稱"""
        type_mapping = {
            'image': '圖像',
            'video': '影片',
            'text': '文字'
        }
        return type_mapping.get(content_type, '內容')
    
    def check_content_policy(self, prompt: str) -> bool:
        """檢查內容政策（返回 True 表示安全）"""
        return not self._check_sensitive_keywords(prompt)
    
    def generate_content(self, prompt: str) -> Dict:
        """生成內容（通用方法）"""
        if self.use_mock:
            return {
                'success': True,
                'content': f"模擬回應：{prompt[:50]}...",
                'mock_mode': True
            }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content.strip(),
                'model': self.model_name,
                'mock_mode': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mock_mode': False
            }
    
    # 模擬模式方法
    def _mock_analyze_prompt_safety(self, prompt: str, content_type: str) -> Dict:
        """模擬 prompt 安全性分析"""
        has_sensitive = self._check_sensitive_keywords(prompt)
        
        if not has_sensitive:
            optimized = self._basic_prompt_optimization(prompt, content_type)
            return {
                'status': 'safe',
                'optimized_prompt': optimized,
                'improvements': ['模擬模式：基本優化'],
                'original_prompt': prompt,
                'mock_mode': True
            }
        else:
            return {
                'status': 'unsafe',
                'original_prompt': prompt,
                'risk_analysis': '模擬模式：檢測到敏感內容',
                'suggestions': self._basic_alternative_suggestions(prompt, content_type),
                'mock_mode': True
            }
    
    def _basic_prompt_optimization(self, prompt: str, content_type: str) -> str:
        """基本 prompt 優化（回退方法）"""
        optimized = prompt
        
        # 添加品質描述
        if content_type == 'image':
            if '高品質' not in optimized:
                optimized = f"高品質, 專業攝影, {optimized}"
            if '細節' not in optimized:
                optimized = f"{optimized}, 細節豐富"
        elif content_type == 'video':
            if '流暢' not in optimized:
                optimized = f"流暢動作, {optimized}"
            if '專業' not in optimized:
                optimized = f"專業拍攝, {optimized}"
        
        return optimized
    
    def _basic_alternative_suggestions(self, prompt: str, content_type: str) -> Dict:
        """基本替代建議（回退方法）"""
        safe_prompt = re.sub(r'|'.join(self.sensitive_keywords), '安全內容', prompt, flags=re.IGNORECASE)
        
        return {
            'option_a': {
                'title': '建議 A (最安全)',
                'prompt': f"安全、正面的{self._get_content_type_chinese(content_type)}內容",
                'description': '移除所有敏感內容，確保完全安全'
            },
            'option_b': {
                'title': '建議 B (中等風險)',
                'prompt': safe_prompt,
                'description': '藝術化表達，保留創意元素'
            },
            'option_c': {
                'title': '建議 C (保留原意)',
                'prompt': f"創意豐富的{self._get_content_type_chinese(content_type)}: {safe_prompt}",
                'description': '強化原始想法，豐富視覺描述'
            }
        } 