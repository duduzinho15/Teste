"""
Sistema de Download e Processamento de Imagens de Produtos
Baixa, redimensiona e otimiza imagens para postagem no Telegram
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from urllib.parse import urlparse
import aiohttp
import aiofiles
from PIL import Image, ImageOps, ImageEnhance
import io

logger = logging.getLogger(__name__)


class ProductImageDownloader:
    """Downloader e processador de imagens de produtos"""
    
    def __init__(self, cache_dir: str = "image_cache", max_size: int = 1024):
        self.cache_dir = Path(cache_dir)
        self.max_size = max_size
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
        
        # Criar diretório de cache se não existir
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configurações de imagem
        self.image_config = {
            "telegram": {
                "max_width": 800,
                "max_height": 800,
                "quality": 85,
                "format": "JPEG"
            },
            "thumbnail": {
                "max_width": 200,
                "max_height": 200,
                "quality": 80,
                "format": "JPEG"
            }
        }
    
    async def download_and_process_image(self, image_url: str, 
                                       platform: str = "geral",
                                       category: str = "geral") -> Optional[str]:
        """Baixa e processa imagem para postagem"""
        try:
            # Verificar se já está em cache
            cache_path = self._get_cache_path(image_url, platform, category)
            if cache_path.exists():
                logger.info(f"Imagem em cache: {cache_path}")
                return str(cache_path)
            
            # Download da imagem
            image_data = await self._download_image(image_url)
            if not image_data:
                return None
            
            # Processar imagem
            processed_image = await self._process_image(image_data, platform, category)
            if not processed_image:
                return None
            
            # Salvar em cache
            await self._save_to_cache(processed_image, cache_path)
            
            logger.info(f"Imagem processada e salva: {cache_path}")
            return str(cache_path)
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem {image_url}: {e}")
            return None
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Baixa imagem da URL"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.warning(f"Falha no download: {response.status} - {image_url}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro no download da imagem: {e}")
            return None
    
    async def _process_image(self, image_data: bytes, platform: str, category: str) -> Optional[bytes]:
        """Processa imagem para otimização"""
        try:
            # Abrir imagem
            image = Image.open(io.BytesIO(image_data))
            
            # Converter para RGB se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Aplicar filtros específicos por plataforma
            image = await self._apply_platform_filters(image, platform, category)
            
            # Redimensionar para Telegram
            telegram_config = self.image_config["telegram"]
            image = self._resize_image(image, telegram_config["max_width"], telegram_config["max_height"])
            
            # Melhorar qualidade
            image = self._enhance_image(image, platform)
            
            # Converter para bytes
            output = io.BytesIO()
            image.save(output, format=telegram_config["format"], 
                      quality=telegram_config["quality"], optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return None
    
    async def _apply_platform_filters(self, image: Image.Image, platform: str, category: str) -> Image.Image:
        """Aplica filtros específicos por plataforma"""
        try:
            # Filtros por plataforma
            if platform == "mercadolivre":
                # Mercado Livre: cores vibrantes, contraste médio
                image = ImageEnhance.Color(image).enhance(1.1)
                image = ImageEnhance.Contrast(image).enhance(1.05)
                image = ImageEnhance.Brightness(image).enhance(1.02)
                
            elif platform == "amazon":
                # Amazon: cores naturais, contraste equilibrado
                image = ImageEnhance.Color(image).enhance(1.0)
                image = ImageEnhance.Contrast(image).enhance(1.1)
                image = ImageEnhance.Sharpness(image).enhance(1.05)
                
            elif platform == "shopee":
                # Shopee: cores vivas, saturação alta
                image = ImageEnhance.Color(image).enhance(1.2)
                image = ImageEnhance.Saturation(image).enhance(1.1)
                image = ImageEnhance.Brightness(image).enhance(1.05)
                
            elif platform == "aliexpress":
                # AliExpress: cores neutras, foco em detalhes
                image = ImageEnhance.Color(image).enhance(0.95)
                image = ImageEnhance.Contrast(image).enhance(1.15)
                image = ImageEnhance.Sharpness(image).enhance(1.1)
            
            # Filtros por categoria
            if category in ["eletronicos", "informatica", "games"]:
                # Produtos tech: cores precisas, contraste alto
                image = ImageEnhance.Contrast(image).enhance(1.1)
                image = ImageEnhance.Sharpness(image).enhance(1.1)
                
            elif category in ["moda", "beleza"]:
                # Moda/beleza: cores suaves, brilho equilibrado
                image = ImageEnhance.Brightness(image).enhance(1.05)
                image = ImageEnhance.Color(image).enhance(1.05)
                
            elif category in ["casa", "esporte"]:
                # Casa/esporte: cores naturais, contraste médio
                image = ImageEnhance.Color(image).enhance(1.0)
                image = ImageEnhance.Contrast(image).enhance(1.05)
            
            return image
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {e}")
            return image
    
    def _resize_image(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Redimensiona imagem mantendo proporção"""
        try:
            # Calcular novas dimensões
            width, height = image.size
            
            if width <= max_width and height <= max_height:
                return image
            
            # Calcular proporção
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Redimensionar com alta qualidade
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return resized
            
        except Exception as e:
            logger.error(f"Erro ao redimensionar imagem: {e}")
            return image
    
    def _enhance_image(self, image: Image.Image, platform: str) -> Image.Image:
        """Melhora qualidade da imagem"""
        try:
            # Aplicar sharpening sutil
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.05)
            
            # Ajustar brilho se necessário
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.02)
            
            return image
            
        except Exception as e:
            logger.error(f"Erro ao melhorar imagem: {e}")
            return image
    
    def _get_cache_path(self, image_url: str, platform: str, category: str) -> Path:
        """Gera caminho de cache para imagem"""
        # Gerar nome único baseado na URL
        import hashlib
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
        
        # Estrutura: cache_dir/platform/category/hash.jpg
        cache_path = self.cache_dir / platform / category
        cache_path.mkdir(parents=True, exist_ok=True)
        
        return cache_path / f"{url_hash}.jpg"
    
    async def _save_to_cache(self, image_data: bytes, cache_path: Path) -> bool:
        """Salva imagem processada em cache"""
        try:
            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(image_data)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar em cache: {e}")
            return False
    
    async def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """Cria thumbnail de uma imagem"""
        try:
            # Abrir imagem
            image = Image.open(image_path)
            
            # Redimensionar para thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Salvar thumbnail
            thumbnail_path = image_path.replace('.jpg', '_thumb.jpg')
            thumbnail.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Erro ao criar thumbnail: {e}")
            return None
    
    async def batch_process_images(self, image_urls: List[str], platform: str, category: str) -> List[str]:
        """Processa múltiplas imagens em lote"""
        try:
            tasks = []
            for url in image_urls:
                task = self.download_and_process_image(url, platform, category)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrar resultados válidos
            processed_images = []
            for result in results:
                if isinstance(result, str) and result:
                    processed_images.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Erro no processamento em lote: {result}")
            
            return processed_images
            
        except Exception as e:
            logger.error(f"Erro no processamento em lote: {e}")
            return []
    
    async def cleanup_cache(self, max_age_days: int = 7) -> int:
        """Limpa cache antigo"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            
            cleaned_count = 0
            
            for file_path in self.cache_dir.rglob("*.jpg"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
            
            logger.info(f"Cache limpo: {cleaned_count} arquivos removidos")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza do cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        try:
            total_files = 0
            total_size = 0
            
            for file_path in self.cache_dir.rglob("*.jpg"):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {}


# Instância global
product_image_downloader = ProductImageDownloader()
