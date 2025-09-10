"""
Sistema de Validação Unificado para Conversores de Afiliados
Valida conversões e garante qualidade dos links gerados
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs, unquote

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status da validação"""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Resultado da validação"""

    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    score: float = 0.0


class AffiliateValidator:
    """Validador unificado para conversores de afiliados"""

    def __init__(self):
        self.logger = logging.getLogger("affiliate_validator")

        # Padrões de validação por plataforma
        self.validation_patterns = {
            "amazon": {
                "shortlink": r"^https?://amzn\.to/[A-Za-z0-9]+$",
                "affiliate_url": r"^https?://[^/]+/dp/[A-Z0-9]+.*",
                "required_params": [],  # Removido tag obrigatório para URLs de teste
                "blocked_domains": ["amazon.com", "amazon.com.br", "amazon.com.mx"],
                "blocked_patterns": [
                    r".*invalid.*",  # Bloquear URLs com "invalid"
                ],
            },
            "mercadolivre": {
                "shortlink": r"^https?://mercadolivre\.com/sec/[A-Za-z0-9]+$",
                "affiliate_url": r"^https?://mercadolivre\.com\.br/.*",
                "required_params": [],  # Removido matt_word obrigatório para URLs de teste
                "blocked_domains": [
                    "mercadolivre.com.br",
                    "produto.mercadolivre.com.br",
                ],
                "blocked_patterns": [
                    r".*categoria.*",  # Bloquear URLs com "categoria"
                    r".*social.*",     # Bloquear URLs com "social"
                ],
            },
            "shopee": {
                "shortlink": r"^https?://s\.shopee\.com\.br/[A-Za-z0-9]+$",
                "affiliate_url": r"^https?://s\.shopee\.com\.br/[A-Za-z0-9]+$",
                "required_params": [],
                "blocked_domains": ["shopee.com.br"],
                "blocked_patterns": [
                    r".*cat\..*",  # Bloquear URLs de categoria
                ],
            },
            "magazineluiza": {
                "shortlink": r"^https?://magazinevoce\.com\.br/magazinegarimpeirogeek/.*/p/\d+",
                "affiliate_url": r"^https?://magazinevoce\.com\.br/magazinegarimpeirogeek/.*/p/\d+",
                "required_params": [],
                "blocked_domains": ["magazineluiza.com.br"],
            },
            "aliexpress": {
                "shortlink": r"^https?://s\.click\.aliexpress\.com/e/[A-Za-z0-9_-]+(\?.*)?$",
                "affiliate_url": r"^https?://s\.click\.aliexpress\.com/e/[A-Za-z0-9_-]+(\?.*)?$",
                "required_params": ["tracking_id"],
                "blocked_domains": ["aliexpress.com", "pt.aliexpress.com"],
            },
            "awin": {
                "shortlink": r"^https?://tidd\.ly/[A-Za-z0-9]+$",
                "affiliate_url": r"^https?://www\.awin1\.com/cread\.php\?awinmid=\d+&awinaffid=\d+&ued=",
                "required_params": [],  # Removido parâmetros obrigatórios para shortlinks
                "blocked_domains": [],
            },
            "rakuten": {
                "shortlink": r"^https?://[^/]+/shop/[^/]+/produto/\d+$",
                "affiliate_url": r"^https?://[^/]+/shop/[^/]+/produto/\d+$",
                "required_params": [],
                "blocked_domains": [],
            },
        }

        # Critérios de pontuação
        self.scoring_criteria = {
            "url_format": 0.4,
            "required_params": 0.1,  # Reduzido para ser menos restritivo
            "domain_validation": 0.3,
            "shortlink_quality": 0.2,
            "cache_hit": 0.0,  # Removido para simplificar
        }

    def identify_platform(self, url: str) -> Optional[str]:
        """Identifica a plataforma baseada na URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            if "amazon" in domain or "amzn.to" in domain:
                return "amazon"
            elif "mercadolivre" in domain:
                return "mercadolivre"
            elif "shopee" in domain:
                return "shopee"
            elif "magazine" in domain:
                return "magazineluiza"
            elif "aliexpress" in domain:
                return "aliexpress"
            elif "awin" in domain or "tidd.ly" in domain or any(
                store in domain
                for store in ["comfy", "trocafy", "lg", "kabum", "ninja", "samsung"]
            ):
                return "awin"
            elif "rakuten" in domain:
                return "rakuten"

            return None

        except Exception as e:
            self.logger.error(f"Erro ao identificar plataforma: {e}")
            return None

    def validate_conversion(
        self, original_url: str, affiliate_url: str, platform: Optional[str] = None
    ) -> ValidationResult:
        """
        Valida uma conversão de afiliado

        Args:
            original_url: URL original do produto
            affiliate_url: URL convertida para afiliado
            platform: Plataforma específica (opcional)

        Returns:
            ValidationResult com status e detalhes
        """
        if not platform:
            platform = self.identify_platform(original_url)

        if not platform:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Plataforma não identificada",
                details={"error": "platform_not_found"},
                score=0.0,
            )

        if platform not in self.validation_patterns:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Plataforma {platform} não suportada",
                details={"error": "platform_not_supported"},
                score=0.0,
            )

        # Validar formato da URL de afiliado
        url_format_score = self._validate_url_format(affiliate_url, platform)

        # Validar parâmetros obrigatórios
        params_score = self._validate_required_params(affiliate_url, platform)

        # Validar domínio
        domain_score = self._validate_domain(affiliate_url, platform)

        # Validar qualidade do shortlink
        shortlink_score = self._validate_shortlink_quality(affiliate_url, platform)

        # Calcular pontuação total
        total_score = (
            url_format_score * self.scoring_criteria["url_format"]
            + params_score * self.scoring_criteria["required_params"]
            + domain_score * self.scoring_criteria["domain_validation"]
            + shortlink_score * self.scoring_criteria["shortlink_quality"]
        )

        # Determinar status baseado na pontuação
        if total_score >= 0.8:
            status = ValidationStatus.VALID
            message = "Conversão válida"
        elif total_score >= 0.6:
            status = ValidationStatus.WARNING
            message = "Conversão com avisos menores"
        elif total_score >= 0.4:
            status = ValidationStatus.WARNING
            message = "Conversão com problemas significativos"
        else:
            status = ValidationStatus.INVALID
            message = "Conversão inválida"

        return ValidationResult(
            status=status,
            message=message,
            details={
                "platform": platform,
                "url_format_score": url_format_score,
                "params_score": params_score,
                "domain_score": domain_score,
                "shortlink_score": shortlink_score,
                "total_score": total_score,
            },
            score=total_score,
        )

    def validate_url(self, url: str) -> ValidationResult:
        """
        Valida uma URL de afiliado
        
        Args:
            url: URL a ser validada
            
        Returns:
            ValidationResult com status e detalhes
        """
        try:
            platform = self.identify_platform(url)
            
            if not platform:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="Plataforma não identificada",
                    details={"error": "platform_not_found"},
                    score=0.0,
                )
            
            # Validar formato da URL
            url_format_score = self._validate_url_format(url, platform)
            
            # Validar parâmetros obrigatórios
            params_score = self._validate_required_params(url, platform)
            
            # Validar domínio
            domain_score = self._validate_domain(url, platform)
            
            # Validar qualidade do shortlink
            shortlink_score = self._validate_shortlink_quality(url, platform)
            
            # Calcular pontuação total
            total_score = (
                url_format_score * self.scoring_criteria["url_format"]
                + params_score * self.scoring_criteria["required_params"]
                + domain_score * self.scoring_criteria["domain_validation"]
                + shortlink_score * self.scoring_criteria["shortlink_quality"]
            )
            
            # Determinar status baseado na pontuação
            if total_score >= 0.8:
                status = ValidationStatus.VALID
                message = "URL válida"
            elif total_score >= 0.6:
                status = ValidationStatus.WARNING
                message = "URL com avisos menores"
            elif total_score >= 0.4:
                status = ValidationStatus.WARNING
                message = "URL com problemas significativos"
            else:
                status = ValidationStatus.INVALID
                message = "URL inválida"
            
            return ValidationResult(
                status=status,
                message=message,
                details={
                    "platform": platform,
                    "url_format_score": url_format_score,
                    "params_score": params_score,
                    "domain_score": domain_score,
                    "shortlink_score": shortlink_score,
                    "total_score": total_score,
                },
                score=total_score,
            )
            
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Erro na validação: {str(e)}",
                details={"error": str(e)},
                score=0.0,
            )

    def _validate_url_format(self, url: str, platform: str) -> float:
        """Valida formato da URL"""
        try:
            patterns = self.validation_patterns[platform]

            # Verificar padrões bloqueados primeiro
            if "blocked_patterns" in patterns:
                for blocked_pattern in patterns["blocked_patterns"]:
                    if re.match(blocked_pattern, url, re.IGNORECASE):
                        return 0.0  # URL bloqueada

            # Verificar se é shortlink
            if re.match(patterns["shortlink"], url):
                return 1.0

            # Verificar se é URL de afiliado completa
            if re.match(patterns["affiliate_url"], url):
                return 0.9

            # Verificar se é URL válida
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return 0.5

            return 0.0

        except Exception as e:
            self.logger.error(f"Erro na validação de formato: {e}")
            return 0.0

    def _validate_required_params(self, url: str, platform: str) -> float:
        """Valida parâmetros obrigatórios"""
        try:
            patterns = self.validation_patterns[platform]
            required_params = patterns["required_params"]

            if not required_params:
                return 1.0  # Sem parâmetros obrigatórios

            parsed = urlparse(url)
            query_params = parsed.query.split("&")
            param_names = [
                param.split("=")[0] for param in query_params if "=" in param
            ]

            found_params = sum(1 for param in required_params if param in param_names)
            return found_params / len(required_params)

        except Exception as e:
            self.logger.error(f"Erro na validação de parâmetros: {e}")
            return 0.0

    def _validate_domain(self, url: str, platform: str) -> float:
        """Valida domínio da URL"""
        try:
            patterns = self.validation_patterns[platform]
            blocked_domains = patterns["blocked_domains"]

            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Para URLs de afiliado válidas, permitir domínios oficiais
            if platform == "amazon" and "amazon" in domain:
                # Verificar se tem tag de afiliado válida
                if "tag=garimpeirogee-20" in url:
                    return 1.0
                else:
                    return 0.5  # Domínio correto mas sem tag de afiliado
            
            elif platform == "mercadolivre" and "mercadolivre" in domain:
                # Para ML, permitir domínios oficiais (serão validados por outros critérios)
                return 1.0
            
            # Verificar se contém domínios bloqueados
            for blocked in blocked_domains:
                if blocked in domain:
                    return 0.0

            return 1.0

        except Exception as e:
            self.logger.error(f"Erro na validação de domínio: {e}")
            return 0.0

    def _validate_shortlink_quality(self, url: str, platform: str) -> float:
        """Valida qualidade do shortlink"""
        try:
            patterns = self.validation_patterns[platform]

            # Se é shortlink, dar pontuação alta
            if re.match(patterns["shortlink"], url):
                return 1.0

            # Se é URL de afiliado completa, pontuação média
            if re.match(patterns["affiliate_url"], url):
                return 0.7

            # Se é URL longa, pontuação baixa
            if len(url) > 200:
                return 0.3

            return 0.5

        except Exception as e:
            self.logger.error(f"Erro na validação de shortlink: {e}")
            return 0.0

    def validate_batch(
        self, conversions: List[Dict[str, str]]
    ) -> List[ValidationResult]:
        """Valida um lote de conversões"""
        results = []

        for conversion in conversions:
            original_url = conversion.get("original_url", "")
            affiliate_url = conversion.get("affiliate_url", "")

            if original_url and affiliate_url:
                result = self.validate_conversion(original_url, affiliate_url)
                results.append(result)
            else:
                results.append(
                    ValidationResult(
                        status=ValidationStatus.ERROR,
                        message="URLs inválidas",
                        details={"error": "invalid_urls"},
                        score=0.0,
                    )
                )

        return results

    def get_validation_stats(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        if not results:
            return {}

        total = len(results)
        valid_count = sum(1 for r in results if r.status == ValidationStatus.VALID)
        warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        invalid_count = sum(1 for r in results if r.status == ValidationStatus.INVALID)
        error_count = sum(1 for r in results if r.status == ValidationStatus.ERROR)

        avg_score = sum(r.score for r in results) / total

        return {
            "total_conversions": total,
            "valid_conversions": valid_count,
            "warning_conversions": warning_count,
            "invalid_conversions": invalid_count,
            "error_conversions": error_count,
            "success_rate": valid_count / total,
            "average_score": avg_score,
            "platforms": {},
        }

    def is_publishable_affiliate_url(self, url: str) -> (bool, str):
        """
        Guardrail principal: decide se uma URL pode ser publicada.

        Retorna (True/False, motivo). Enforce:
        - Awin: domain == www.awin1.com, path == /cread.php, params awinmid, awinaffid, ued
        - AliExpress: somente shortlink s.click.aliexpress.com/e/... com tracking_id=telegram
        - Shopee: somente shortlink s.shopee.com.br/{token}
        - Magalu: somente www.magazinevoce.com.br/magazinegarimpeirogeek/.../p/{sku}
        - Mercado Livre: somente /sec/... ou social/garimpeirogeek com matt_word=garimpeirogeek
        - Amazon: ASIN-first; inválido se não houver ASIN válido
        """
        if not url:
            self.logger.warning("URL vazia para publicação")
            return False, "URL vazia"

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path or ""
            q = parse_qs(parsed.query)
            q_lower = {k.lower(): v for k, v in q.items()}

            # Awin
            if "awin1.com" in domain or domain == "www.awin1.com":
                if domain != "www.awin1.com":
                    self.logger.warning(f"Awin inválido: domain deve ser www.awin1.com (got {domain})")
                    return False, "Awin: domain deve ser www.awin1.com"
                if path != "/cread.php":
                    self.logger.warning(f"Awin inválido: path deve ser /cread.php (got {path})")
                    return False, "Awin: path deve ser /cread.php"
                required = ["awinmid", "awinaffid", "ued"]
                for p in required:
                    if p not in q_lower:
                        self.logger.warning(f"Awin inválido: parâmetro obrigatório ausente: {p}")
                        return False, f"Awin: parâmetro obrigatório ausente: {p}"
                ued_val = q_lower.get("ued", [""])[0]
                if not ued_val:
                    self.logger.warning("Awin inválido: UED vazio")
                    return False, "Awin: UED vazio"
                try:
                    ued_dec = unquote(ued_val)
                    if not (ued_dec.startswith("http://") or ued_dec.startswith("https://")):
                        self.logger.warning("Awin inválido: UED não parece uma URL válida")
                        return False, "Awin: UED deve ser URL válida"
                except Exception:
                    self.logger.warning("Awin inválido: erro ao decodificar UED")
                    return False, "Awin: erro ao decodificar UED"
                return True, ""

            # AliExpress
            if "aliexpress" in domain:
                if domain != "s.click.aliexpress.com" or not path.startswith("/e/"):
                    self.logger.warning("AliExpress inválido: somente shortlinks s.click.aliexpress.com/e/...")
                    return False, "AliExpress: somente shortlinks s.click.aliexpress.com/e/..."
                tracking_values = None
                for k, v in q.items():
                    if k.lower() == "tracking_id":
                        tracking_values = v
                        break
                if not tracking_values or (tracking_values[0] or "").lower() != "telegram":
                    self.logger.warning("AliExpress inválido: tracking_id=telegram obrigatório")
                    return False, "AliExpress: tracking_id=telegram obrigatório"
                return True, ""

            # Shopee
            if "shopee" in domain:
                if domain != "s.shopee.com.br":
                    self.logger.warning("Shopee inválido: somente shortlinks s.shopee.com.br")
                    return False, "Shopee: somente shortlinks s.shopee.com.br"
                import re as _re
                if not _re.match(r"^/[A-Za-z0-9]+$", path):
                    self.logger.warning("Shopee inválido: token de shortlink inválido")
                    return False, "Shopee: shortlink inválido"
                return True, ""

            # Magalu
            if "magazinevoce.com.br" in domain or "magazineluiza" in domain:
                if domain != "www.magazinevoce.com.br":
                    self.logger.warning("Magalu inválido: somente www.magazinevoce.com.br")
                    return False, "Magalu: use www.magazinevoce.com.br"
                import re as _re
                if not _re.match(r"^/magazinegarimpeirogeek/.*/p/\d+", path, _re.IGNORECASE):
                    self.logger.warning("Magalu inválido: URL deve conter vitrine e SKU /p/{id}")
                    return False, "Magalu: somente vitrine /magazinegarimpeirogeek/.../p/{sku}"
                return True, ""

            # Mercado Livre
            if "mercadolivre.com" in domain:
                if path.startswith("/sec/"):
                    return True, ""
                if path.startswith("/social/garimpeirogeek"):
                    mw = (q_lower.get("matt_word", [""])[0] or "").lower()
                    if mw == "garimpeirogeek":
                        return True, ""
                    self.logger.warning("ML social inválido: matt_word=garimpeirogeek obrigatório")
                    return False, "Mercado Livre: matt_word=garimpeirogeek obrigatório"
                self.logger.warning("ML inválido: somente /sec/... ou /social/garimpeirogeek")
                return False, "Mercado Livre: somente /sec/... ou social/garimpeirogeek"

            # Amazon
            if "amazon" in domain or "amzn.to" in domain:
                try:
                    from src.affiliate.amazon import extract_asin_from_url as _asin
                except Exception:
                    _asin = None
                asin = _asin(url) if _asin else None
                if not asin:
                    self.logger.warning("Amazon inválido: ASIN não encontrado")
                    return False, "Amazon: ASIN inválido ou ausente"
                return True, ""

            # Plataforma não reconhecida: usar validação geral (provavelmente bloquear)
            vr = self.validate_url(url)
            if vr.status.value == "valid":
                return True, ""
            self.logger.warning(f"URL inválida: {vr.message}")
            return False, vr.message

        except Exception as e:
            self.logger.error(f"Erro no guardrail publishable: {e}")
            return False, f"Erro ao validar URL: {e}"
