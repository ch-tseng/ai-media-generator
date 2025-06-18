from typing import Dict, List, Any
from llm_services.openai_llm_service import OpenAILLMService

class PromptAnalyzer:
    """Prompt 分析器類別"""
    
    def __init__(self, llm_service: OpenAILLMService):
        """初始化 Prompt 分析器"""
        if not llm_service:
            raise ValueError("LLM 服務不能為空")
        
        self.llm_service = llm_service
    
    def analyze_safety(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """分析 prompt 安全性並提供優化建議"""
        if not prompt or not prompt.strip():
            return {
                'error': 'Prompt 不能為空',
                'error_code': 'EMPTY_PROMPT'
            }
        
        if len(prompt.strip()) > 2000:
            return {
                'error': 'Prompt 長度不能超過 2000 字元',
                'error_code': 'PROMPT_TOO_LONG',
                'current_length': len(prompt.strip())
            }
        
        # 使用 OpenAI LLM 服務進行安全性分析
        result = self.llm_service.analyze_prompt_safety(prompt.strip(), content_type)
        
        # 添加額外的分析資訊
        if 'error' not in result:
            result['analysis_info'] = {
                'original_length': len(prompt.strip()),
                'content_type': content_type,
                'analysis_timestamp': self._get_timestamp()
            }
            
            if result.get('status') == 'safe':
                result['analysis_info']['optimized_length'] = len(result.get('optimized_prompt', ''))
            
        return result
    
    def optimize_prompt(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """單純優化 prompt（假設是安全的）"""
        if not prompt or not prompt.strip():
            return {
                'error': 'Prompt 不能為空',
                'error_code': 'EMPTY_PROMPT'
            }
        
        prompt = prompt.strip()
        
        # 檢查是否包含敏感內容
        if self.llm_service.check_content_policy(prompt):
            # 安全內容，直接優化
            optimized = self.llm_service._optimize_safe_prompt(prompt, content_type)
            
            return {
                'status': 'optimized',
                'original_prompt': prompt,
                'optimized_prompt': optimized,
                'improvements': self.llm_service._get_improvements_explanation(prompt, optimized),
                'content_type': content_type,
                'timestamp': self._get_timestamp()
            }
        else:
            # 包含敏感內容，返回警告
            return {
                'status': 'contains_sensitive_content',
                'original_prompt': prompt,
                'warning': '檢測到敏感內容，請使用完整的安全性分析功能',
                'suggestion': '建議使用 analyze_safety 方法獲取安全的替代建議'
            }
    
    def generate_alternatives(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """生成替代 prompt 建議"""
        if not prompt or not prompt.strip():
            return {
                'error': 'Prompt 不能為空',
                'error_code': 'EMPTY_PROMPT'
            }
        
        # 強制生成替代建議（無論是否包含敏感內容）
        suggestions = self.llm_service._generate_alternative_prompts(prompt.strip(), content_type)
        
        return {
            'status': 'alternatives_generated',
            'original_prompt': prompt.strip(),
            'suggestions': suggestions,
            'content_type': content_type,
            'timestamp': self._get_timestamp()
        }
    
    def extract_key_elements(self, prompt: str) -> List[str]:
        """提取 prompt 中的關鍵元素"""
        if not prompt or not prompt.strip():
            return []
        
        prompt = prompt.strip()
        
        # 基本關鍵詞提取
        key_elements = []
        
        # 人物相關
        person_keywords = ['人', '女性', '男性', '小孩', '老人', '年輕', '中年']
        for keyword in person_keywords:
            if keyword in prompt:
                key_elements.append(f"人物: {keyword}")
        
        # 場景相關
        scene_keywords = ['室內', '戶外', '海邊', '山上', '城市', '鄉村', '森林', '街道']
        for keyword in scene_keywords:
            if keyword in prompt:
                key_elements.append(f"場景: {keyword}")
        
        # 時間相關
        time_keywords = ['白天', '夜晚', '黃昏', '清晨', '中午', '傍晚']
        for keyword in time_keywords:
            if keyword in prompt:
                key_elements.append(f"時間: {keyword}")
        
        # 風格相關
        style_keywords = ['寫實', '藝術', '卡通', '油畫', '水彩', '素描', '攝影']
        for keyword in style_keywords:
            if keyword in prompt:
                key_elements.append(f"風格: {keyword}")
        
        # 情緒相關
        emotion_keywords = ['快樂', '悲傷', '平靜', '興奮', '溫暖', '神秘', '浪漫']
        for keyword in emotion_keywords:
            if keyword in prompt:
                key_elements.append(f"情緒: {keyword}")
        
        return key_elements
    
    def get_prompt_suggestions(self, content_type: str) -> Dict[str, List[str]]:
        """獲取 prompt 撰寫建議"""
        if content_type == 'image':
            return {
                'characters': [
                    '一位優雅的年輕女性，長髮飄逸',
                    '友善微笑的中年男性，穿著商務服裝',
                    '天真可愛的小孩，眼神清澈',
                    '慈祥的老年人，臉上布滿歲月痕跡'
                ],
                'backgrounds': [
                    '櫻花盛開的公園，陽光透過樹葉灑下',
                    '繁華的城市夜景，霓虹燈光閃爍',
                    '溫馨的咖啡廳，溫暖的燈光氛圍',
                    '壯麗的海邊夕陽，波浪輕撫沙灘'
                ],
                'photography': [
                    '使用 85mm 鏡頭，淺景深背景虛化',
                    '廣角鏡頭拍攝，展現遼闊的全景',
                    '微距攝影，捕捉細膩的紋理細節',
                    '逆光拍攝，營造夢幻的輪廓光'
                ],
                'styles': [
                    '超寫實風格，細節豐富層次分明',
                    '印象派藝術風格，色彩豐富筆觸明顯',
                    '復古膠片風格，溫暖色調懷舊質感',
                    '現代簡約風格，乾淨線條極簡構圖'
                ]
            }
        else:  # video
            return {
                'actions': [
                    '人物緩慢走向鏡頭，表情自然放鬆',
                    '優雅的舞蹈動作，裙擺隨風飄動',
                    '孩童在草地上奔跑嬉戲，充滿活力',
                    '老人坐在搖椅上，慢慢搖擺回憶往昔'
                ],
                'camera_movements': [
                    '鏡頭緩慢推進，逐漸聚焦於主體',
                    '環繞拍攝，360度展現場景全貌',
                    '從低角度向上拍攝，營造壯觀效果',
                    '跟拍移動，保持主體在畫面中心'
                ],
                'environments': [
                    '微風輕撫，樹葉沙沙作響',
                    '雨滴落在窗戶上，模糊了外面的景色',
                    '夕陽西下，天空色彩漸變',
                    '城市車流，燈光拖出美麗軌跡'
                ],
                'effects': [
                    '慢鏡頭效果，突出動作的優美',
                    '時間加速，展現變化過程',
                    '景深變化，焦點在不同物體間轉移',
                    '色彩漸變，營造情緒轉換'
                ]
            }
    
    def validate_prompt_length(self, prompt: str) -> Dict[str, Any]:
        """驗證 prompt 長度"""
        if not prompt:
            return {
                'valid': False,
                'length': 0,
                'max_length': 2000,
                'error': 'Prompt 不能為空'
            }
        
        length = len(prompt.strip())
        max_length = 2000
        
        return {
            'valid': length <= max_length,
            'length': length,
            'max_length': max_length,
            'remaining': max_length - length,
            'percentage': round((length / max_length) * 100, 1)
        }
    
    def _get_timestamp(self) -> str:
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.now().isoformat() 