import google.generativeai as genai
import re
import os
from typing import Dict, List, Union

class GeminiService:
    """Gemini LLM 服務類別"""
    
    def __init__(self, api_key: str, model_name: str = None):
        """初始化 Gemini 服務"""
        if not api_key:
            raise ValueError("Gemini API 金鑰不能為空")
        
        # 配置 Gemini API
        genai.configure(api_key=api_key)
        
        # 使用環境變數或傳入的模型名稱，默認為 gemini-2.0-flash
        if model_name is None:
            model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
        
        # 初始化模型
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        print(f"✅ Gemini 服務已初始化 (模型: {model_name})")
        
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
        
        response = self.model.generate_content(optimization_prompt)
        return response.text.strip()
    
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
        
        response = self.model.generate_content(suggestion_prompt)
        suggestions_text = response.text.strip()
        
        # 解析回應
        return self._parse_suggestions(suggestions_text)
    
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
        
        # 如果解析失敗，使用備用方法
        if not (match_a and match_b and match_c):
            # 按行分割並尋找建議
            lines = suggestions_text.split('\n')
            current_suggestion = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if '建議A' in line or '建議a' in line:
                    if current_suggestion:
                        self._set_suggestion_content(suggestions, current_suggestion, current_content)
                    current_suggestion = 'option_a'
                    current_content = [line.split('：')[-1].split(':')[-1].strip()]
                elif '建議B' in line or '建議b' in line:
                    if current_suggestion:
                        self._set_suggestion_content(suggestions, current_suggestion, current_content)
                    current_suggestion = 'option_b'
                    current_content = [line.split('：')[-1].split(':')[-1].strip()]
                elif '建議C' in line or '建議c' in line:
                    if current_suggestion:
                        self._set_suggestion_content(suggestions, current_suggestion, current_content)
                    current_suggestion = 'option_c'
                    current_content = [line.split('：')[-1].split(':')[-1].strip()]
                elif current_suggestion and line:
                    current_content.append(line)
            
            # 設定最後一個建議
            if current_suggestion:
                self._set_suggestion_content(suggestions, current_suggestion, current_content)
        
        return suggestions
    
    def _set_suggestion_content(self, suggestions: Dict, suggestion_key: str, content_lines: List[str]):
        """設定建議內容"""
        content = ' '.join(content_lines).strip()
        if content:
            suggestions[suggestion_key]['prompt'] = content
    
    def _get_improvements_explanation(self, original: str, optimized: str) -> List[str]:
        """獲取改進說明"""
        improvements = []
        
        if len(optimized) > len(original):
            improvements.append("增加了更具體的描述細節")
        
        if any(word in optimized for word in ['光線', '構圖', '色彩', '風格']):
            improvements.append("添加了專業的視覺技術參數")
        
        if optimized != original:
            improvements.append("優化了語言表達，使其更適合AI理解")
        
        if not improvements:
            improvements.append("提示詞已經很好，僅進行細微調整")
        
        return improvements
    
    def _get_content_type_chinese(self, content_type: str) -> str:
        """獲取內容類型的中文名稱"""
        type_mapping = {
            'image': '圖像',
            'video': '影片'
        }
        return type_mapping.get(content_type, '內容')
    
    def check_content_policy(self, prompt: str) -> bool:
        """檢查內容是否符合政策"""
        return not self._check_sensitive_keywords(prompt)
    
    def generate_content(self, prompt: str) -> Dict:
        """生成內容的統一接口"""
        try:
            response = self.model.generate_content(prompt)
            return {
                'success': True,
                'content': response.text.strip()
            }
        except Exception as e:
            print(f"❌ Gemini 內容生成失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            } 