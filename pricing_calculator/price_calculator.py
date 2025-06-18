from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

class PriceCalculator:
    """AI 內容生成價格計算器"""
    
    def __init__(self):
        """初始化價格計算器"""
        # DALL-E 3 價格（美元）- 根據 OpenAI 官方價格
        self.dalle_prices = {
            'standard': {
                '1024x1024': Decimal('0.040'),   # $0.040/張
                '1024x1792': Decimal('0.080'),   # $0.080/張
                '1792x1024': Decimal('0.080')    # $0.080/張
            },
            'hd': {
                '1024x1024': Decimal('0.080'),   # $0.080/張
                '1024x1792': Decimal('0.120'),   # $0.120/張
                '1792x1024': Decimal('0.120')    # $0.120/張
            }
        }
        
        # Imagen 4 價格（美元）- 根據最新 Vertex AI 價格
        self.imagen_prices = {
            'standard': Decimal('0.040'),  # Imagen 4 標準品質 $0.04/張
            'high': Decimal('0.080'),      # Imagen 4 高品質 $0.08/張
            'ultra': Decimal('0.120')      # Imagen 4 超高品質 $0.12/張
        }
        
        # Veo 影片價格（美元每秒）
        self.video_prices = {
            'standard': Decimal('0.50'),
            'high': Decimal('1.00'),
            'ultra': Decimal('2.00')
        }
        
        # 尺寸調整係數（根據像素數量）
        self.size_multipliers = {
            '1024x1024': Decimal('1.0'),    # 1M 像素基準
            '1024x1792': Decimal('1.75'),   # 1.8M 像素
            '1792x1024': Decimal('1.75')    # 1.8M 像素
        }
        
        # 批量折扣階梯
        self.bulk_discount_tiers = {
            5: Decimal('0.05'),   # 5+ 張享 5% 折扣
            10: Decimal('0.10'),  # 10+ 張享 10% 折扣
            20: Decimal('0.15'),  # 20+ 張享 15% 折扣
            50: Decimal('0.20')   # 50+ 張享 20% 折扣
        }
        
        # 稅率設定（可配置）
        self.tax_rate = Decimal('0.08')  # 8% 稅率
        
        # 支援的貨幣
        self.supported_currencies = ['USD', 'TWD', 'EUR', 'JPY']
        self.exchange_rates = {
            'USD': Decimal('1.0'),
            'TWD': Decimal('31.5'),  # 假設匯率
            'EUR': Decimal('0.85'),
            'JPY': Decimal('110.0')
        }
    
    def calculate_image_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """計算圖像生成費用（支援 DALL-E 3 和 Imagen 4）"""
        if not params:
            return {
                'error': '缺少計算參數',
                'error_code': 'MISSING_PARAMS'
            }
        
        count = params.get('count', 1)
        quality = params.get('quality', 'standard')
        size = params.get('size', '1024x1024')
        model = params.get('model', 'dall-e-3')
        
        # 驗證參數
        validation_result = self._validate_image_params(count, quality, size, model)
        if validation_result.get('error'):
            return validation_result
        
        # 根據模型計算基礎價格
        if model in ['dall-e-3', 'openai']:
            # DALL-E 3 價格結構（品質和尺寸組合定價）
            if quality in self.dalle_prices and size in self.dalle_prices[quality]:
                unit_price = self.dalle_prices[quality][size]
            else:
                unit_price = self.dalle_prices['standard']['1024x1024']
            service_name = 'DALL-E 3'
            provider_name = 'OpenAI'
            max_batch_size = 1  # DALL-E 3 每次只能生成 1 張
        else:
            # Imagen 4 價格結構（品質定價 + 尺寸調整）
            base_price = self.imagen_prices.get(quality, self.imagen_prices['standard'])
            size_multiplier = self.size_multipliers.get(size, Decimal('1.0'))
            unit_price = base_price * size_multiplier
            service_name = 'Imagen 4'
            provider_name = 'Google Vertex AI'
            max_batch_size = 4  # Imagen 4 每次最多 4 張
        
        # 總價格（未折扣）
        subtotal = unit_price * Decimal(str(count))
        
        # 批量折扣
        discount_rate = self._get_bulk_discount(count)
        discount_amount = subtotal * discount_rate
        
        # 折扣後價格
        discounted_price = subtotal - discount_amount
        
        # 稅費計算
        tax_amount = discounted_price * self.tax_rate
        
        # 最終總額
        final_total = discounted_price + tax_amount
        
        # 計算預估處理批次
        batches = (count + max_batch_size - 1) // max_batch_size
        if model in ['dall-e-3', 'openai']:
            estimated_time = count * 20  # DALL-E 3 每張約 20 秒
        else:
            estimated_time = batches * 15  # Imagen 4 每批約 15 秒
        
        return {
            'success': True,
            'cost_breakdown': {
                'unit_price': self._format_currency(unit_price),
                'subtotal': self._format_currency(subtotal),
                'discount_rate': float(discount_rate * 100),
                'discount_amount': self._format_currency(discount_amount),
                'discounted_price': self._format_currency(discounted_price),
                'tax_rate': float(self.tax_rate * 100),
                'tax_amount': self._format_currency(tax_amount),
                'total': self._format_currency(final_total)
            },
            'parameters': {
                'count': count,
                'quality': quality,
                'size': size,
                'model': model,
                'unit_price': self._format_currency(unit_price),
                'processing_batches': batches,
                'estimated_time_seconds': estimated_time
            },
            'model_info': {
                'service': service_name,
                'provider': provider_name,
                'pricing_model': 'per_image_with_quality_size_tiers' if model in ['dall-e-3', 'openai'] else 'per_image_with_quality_tiers'
            },
            'currency': 'USD',
            'calculation_timestamp': self._get_timestamp()
        }
    
    def calculate_video_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """計算 Veo 影片生成費用"""
        if not params:
            return {
                'error': '缺少計算參數',
                'error_code': 'MISSING_PARAMS'
            }
        
        count = params.get('count', 1)
        quality = params.get('quality', 'standard')
        duration = params.get('duration', 5)
        resolution = params.get('resolution', '1080p')
        
        # 驗證參數
        validation_result = self._validate_video_params(count, quality, duration, resolution)
        if validation_result.get('error'):
            return validation_result
        
        # 基礎價格（每秒）
        base_price_per_second = self.video_prices.get(quality, self.video_prices['standard'])
        
        # 解析度調整係數
        resolution_multipliers = {
            '720p': Decimal('1.0'),
            '1080p': Decimal('1.5'),
            '4k': Decimal('3.0')
        }
        resolution_multiplier = resolution_multipliers.get(resolution, Decimal('1.0'))
        
        # 單個影片價格
        unit_price = base_price_per_second * Decimal(str(duration)) * resolution_multiplier
        
        # 總價格
        subtotal = unit_price * Decimal(str(count))
        
        # 影片沒有批量折扣（處理成本較高）
        discount_rate = Decimal('0')
        discount_amount = Decimal('0')
        
        # 稅費計算
        tax_amount = subtotal * self.tax_rate
        
        # 最終總額
        final_total = subtotal + tax_amount
        
        # 預估處理時間（影片生成較慢）
        estimated_time = duration * count * 30  # 每秒影片約需 30 秒處理
        
        return {
            'success': True,
            'cost_breakdown': {
                'unit_price': self._format_currency(unit_price),
                'subtotal': self._format_currency(subtotal),
                'discount_rate': float(discount_rate * 100),
                'discount_amount': self._format_currency(discount_amount),
                'tax_rate': float(self.tax_rate * 100),
                'tax_amount': self._format_currency(tax_amount),
                'total': self._format_currency(final_total)
            },
            'parameters': {
                'count': count,
                'quality': quality,
                'duration': duration,
                'resolution': resolution,
                'base_price_per_second': self._format_currency(base_price_per_second),
                'resolution_multiplier': float(resolution_multiplier),
                'estimated_time_seconds': estimated_time
            },
            'model_info': {
                'service': 'Veo',
                'provider': 'Google Vertex AI',
                'pricing_model': 'per_second_with_resolution_tiers'
            },
            'currency': 'USD',
            'calculation_timestamp': self._get_timestamp()
        }
    
    def get_pricing_tiers(self) -> Dict[str, Any]:
        """獲取價格等級資訊"""
        return {
            'image_pricing': {
                'standard': {
                    'price': self._format_currency(self.image_prices['standard']),
                    'description': '標準品質，快速生成',
                    'features': ['基本解析度', '較快生成', '適合預覽']
                },
                'high': {
                    'price': self._format_currency(self.image_prices['high']),
                    'description': '高品質，平衡效果與速度',
                    'features': ['高解析度', '中等生成時間', '商用品質']
                },
                'ultra': {
                    'price': self._format_currency(self.image_prices['ultra']),
                    'description': '超高品質，專業級效果',
                    'features': ['超高解析度', '較長生成時間', '專業品質']
                }
            },
            'video_pricing': {
                'standard': {
                    'price_per_second': self._format_currency(self.video_prices['standard']),
                    'description': '標準品質影片',
                    'features': ['720p 解析度', '基本品質', '快速生成']
                },
                'high': {
                    'price_per_second': self._format_currency(self.video_prices['high']),
                    'description': '高品質影片',
                    'features': ['1080p 解析度', '高品質', '中等生成時間']
                },
                'ultra': {
                    'price_per_second': self._format_currency(self.video_prices['ultra']),
                    'description': '超高品質影片',
                    'features': ['4K 解析度', '專業品質', '較長生成時間']
                }
            },
            'bulk_discounts': [
                {'min_items': 5, 'discount': '5%'},
                {'min_items': 10, 'discount': '10%'},
                {'min_items': 20, 'discount': '15%'},
                {'min_items': 50, 'discount': '20%'}
            ],
            'currency': 'USD'
        }
    
    def _validate_image_params(self, count: int, quality: str, size: str, model: str = 'dall-e-3') -> Dict[str, Any]:
        """驗證圖像生成參數"""
        errors = []
        
        # 驗證數量
        if not isinstance(count, int) or count < 1:
            errors.append('生成數量必須是正整數')
        elif model in ['dall-e-3', 'openai'] and count > 4:
            errors.append('DALL-E 3 單次生成數量不能超過 4 張')
        elif model not in ['dall-e-3', 'openai'] and count > 50:
            errors.append('單次生成數量不能超過 50 張')
        
        # 驗證品質
        if model in ['dall-e-3', 'openai']:
            if quality not in self.dalle_prices:
                errors.append(f'DALL-E 3 不支援的品質設定: {quality}')
        else:
            if quality not in self.imagen_prices:
                errors.append(f'Imagen 4 不支援的品質設定: {quality}')
        
        # 驗證尺寸
        if model in ['dall-e-3', 'openai']:
            # DALL-E 3 支援的尺寸
            dalle_sizes = ['1024x1024', '1024x1792', '1792x1024']
            if size not in dalle_sizes:
                errors.append(f'DALL-E 3 不支援的尺寸設定: {size}')
        else:
            # Imagen 4 支援的尺寸
            if size not in self.size_multipliers:
                errors.append(f'Imagen 4 不支援的尺寸設定: {size}')
        
        if errors:
            return {
                'error': '; '.join(errors),
                'error_code': 'INVALID_PARAMS'
            }
        
        return {'success': True}
    
    def _validate_video_params(self, count: int, quality: str, duration: int, resolution: str) -> Dict[str, Any]:
        """驗證影片生成參數"""
        if not isinstance(count, int) or count < 1 or count > 10:
            return {
                'error': '影片數量必須在 1-10 之間',
                'error_code': 'INVALID_COUNT'
            }
        
        if quality not in self.video_prices:
            return {
                'error': f'不支援的品質設定: {quality}',
                'error_code': 'INVALID_QUALITY'
            }
        
        if not isinstance(duration, int) or duration < 1 or duration > 30:
            return {
                'error': '影片長度必須在 1-30 秒之間',
                'error_code': 'INVALID_DURATION'
            }
        
        if resolution not in ['720p', '1080p', '4k']:
            return {
                'error': f'不支援的解析度設定: {resolution}',
                'error_code': 'INVALID_RESOLUTION'
            }
        
        return {'success': True}
    
    def _get_bulk_discount(self, count: int) -> Decimal:
        """計算批量折扣率"""
        # 找到適用的最高折扣階梯
        applicable_discount = Decimal('0')
        for threshold, discount in sorted(self.bulk_discount_tiers.items(), reverse=True):
            if count >= threshold:
                applicable_discount = discount
                break
        
        return applicable_discount
    
    def _format_currency(self, amount: Decimal, currency: str = 'USD') -> str:
        """格式化貨幣顯示"""
        # 轉換為指定貨幣
        if currency != 'USD':
            rate = self.exchange_rates.get(currency, Decimal('1.0'))
            amount = amount * rate
        
        # 四捨五入到合適的小數位數
        if currency in ['JPY']:
            # 日幣不使用小數
            rounded = amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            return f"¥{rounded:,}"
        elif currency == 'TWD':
            rounded = amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            return f"NT${rounded:,}"
        elif currency == 'EUR':
            rounded = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return f"€{rounded:.2f}"
        else:  # USD
            rounded = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return f"${rounded:.2f}"
    
    def _get_timestamp(self) -> str:
        """獲取當前時間戳"""
        return datetime.now().isoformat()
    
    def calculate_monthly_estimate(self, usage_projection: Dict[str, Any]) -> Dict[str, Any]:
        """計算月度費用預估"""
        monthly_total = Decimal('0')
        breakdown = {}
        
        # 圖像費用
        if 'images' in usage_projection:
            image_usage = usage_projection['images']
            for quality, count in image_usage.items():
                if quality in self.image_prices and count > 0:
                    params = {
                        'count': count,
                        'quality': quality,
                        'size': '1024x1024'  # 預設尺寸
                    }
                    result = self.calculate_image_cost(params)
                    if result.get('success'):
                        cost = Decimal(result['cost_breakdown']['total'].replace('$', ''))
                        breakdown[f'images_{quality}'] = {
                            'count': count,
                            'total': self._format_currency(cost)
                        }
                        monthly_total += cost
        
        # 影片費用
        if 'videos' in usage_projection:
            video_usage = usage_projection['videos']
            for quality, data in video_usage.items():
                if quality in self.video_prices:
                    count = data.get('count', 0)
                    duration = data.get('duration', 5)
                    if count > 0:
                        params = {
                            'count': count,
                            'quality': quality,
                            'duration': duration,
                            'resolution': '1080p'  # 預設解析度
                        }
                        result = self.calculate_video_cost(params)
                        if result.get('success'):
                            cost = Decimal(result['cost_breakdown']['total'].replace('$', ''))
                            breakdown[f'videos_{quality}'] = {
                                'count': count,
                                'duration': duration,
                                'total': self._format_currency(cost)
                            }
                            monthly_total += cost
        
        return {
            'success': True,
            'monthly_total': self._format_currency(monthly_total),
            'breakdown': breakdown,
            'currency': 'USD',
            'calculation_timestamp': self._get_timestamp()
        }
    
    def update_pricing(self, new_prices: Dict[str, Any]) -> Dict[str, Any]:
        """更新價格配置"""
        if 'image_prices' in new_prices:
            for quality, price in new_prices['image_prices'].items():
                if quality in self.image_prices:
                    self.image_prices[quality] = Decimal(str(price))
        
        if 'video_prices' in new_prices:
            for quality, price in new_prices['video_prices'].items():
                if quality in self.video_prices:
                    self.video_prices[quality] = Decimal(str(price))
        
        if 'bulk_discount_tiers' in new_prices:
            self.bulk_discount_tiers = {
                int(k): Decimal(str(v)) 
                for k, v in new_prices['bulk_discount_tiers'].items()
            }
        
        return {
            'success': True,
            'message': '價格配置已更新',
            'timestamp': self._get_timestamp()
        }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """獲取完整價格資訊"""
        return {
            'imagen_4_prices': {
                quality: self._format_currency(price) 
                for quality, price in self.image_prices.items()
            },
            'veo_prices': {
                quality: f"{self._format_currency(price)}/sec" 
                for quality, price in self.video_prices.items()
            },
            'bulk_discounts': {
                f"{threshold}+": f"{float(discount * 100):.0f}%" 
                for threshold, discount in self.bulk_discount_tiers.items()
            },
            'size_multipliers': {
                size: f"{float(mult):.1f}x" 
                for size, mult in self.size_multipliers.items()
            },
            'tax_rate': f"{float(self.tax_rate * 100):.0f}%",
            'currency': 'USD',
            'last_updated': self._get_timestamp()
        } 