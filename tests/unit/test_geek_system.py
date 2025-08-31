"""
Testes unitários para o sistema geek completo
Testa GeekPrioritizer, GeekAlertManager e GeekCommands
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer, GeekScore
from src.core.geek_alerts import GeekAlertManager, GeekAlert
from src.telegram_bot.geek_commands import GeekCommands

class TestGeekPrioritizer:
    """Testes para o GeekPrioritizer"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.prioritizer = GeekPrioritizer()
        
        # Ofertas de teste
        self.gaming_offer = Offer(
            title="PlayStation 5 Console Gaming",
            price=Decimal("3999.99"),
            original_price=Decimal("4699.99"),
            discount_percentage=15.0,
            category="consoles_gaming",
            store="Amazon",
            url="https://amzn.to/ps5",
            image_url="https://example.com/ps5.jpg",
            description="Console PlayStation 5 para jogos",
            stock_quantity=10
        )
        
        self.tech_offer = Offer(
            title="RTX 4070 Ti Gaming Graphics Card",
            price=Decimal("4299.99"),
            original_price=Decimal("5399.99"),
            discount_percentage=20.0,
            category="placas_video",
            store="Kabum",
            url="https://kabum.com/rtx4070",
            image_url="https://example.com/rtx4070.jpg",
            description="Placa de vídeo RTX 4070 Ti para gaming",
            stock_quantity=5
        )
        
        self.smart_home_offer = Offer(
            title="Smart TV LG OLED 55\" 4K",
            price=Decimal("2999.99"),
            original_price=Decimal("3999.99"),
            discount_percentage=25.0,
            category="smart_tvs",
            store="Magazine Luiza",
            url="https://magalu.com/smarttv",
            image_url="https://example.com/smarttv.jpg",
            description="Smart TV LG OLED com tecnologia 4K",
            stock_quantity=15
        )
        
        self.audio_offer = Offer(
            title="Headphone Sony WH-1000XM5 Bluetooth",
            price=Decimal("1899.99"),
            original_price=Decimal("2299.99"),
            discount_percentage=17.0,
            category="headphones_premium",
            store="Mercado Livre",
            url="https://mercadolivre.com/headphone",
            image_url="https://example.com/headphone.jpg",
            description="Headphone premium com noise cancelling",
            stock_quantity=25
        )
        
        self.general_offer = Offer(
            title="Cabo USB-C Genérico 2m",
            price=Decimal("19.99"),
            original_price=Decimal("29.99"),
            discount_percentage=33.0,
            category="cables",
            store="AliExpress",
            url="https://aliexpress.com/cable",
            image_url="https://example.com/cable.jpg",
            description="Cabo USB-C simples para carregamento",
            stock_quantity=100
        )
    
    def test_geek_prioritizer_initialization(self):
        """Testa inicialização do GeekPrioritizer"""
        assert self.prioritizer is not None
        assert hasattr(self.prioritizer, 'geek_config')
        assert hasattr(self.prioritizer, 'geek_keywords_regex')
        assert self.prioritizer.logger is not None
    
    def test_calculate_geek_score_gaming(self):
        """Testa cálculo de score para oferta de gaming"""
        geek_score = self.prioritizer.calculate_geek_score(self.gaming_offer)
        
        assert isinstance(geek_score, GeekScore)
        assert geek_score.overall_score > 0.5  # Gaming deve ter score alto
        assert "gaming" in geek_score.matched_categories
        assert geek_score.geek_level in ["primary", "secondary"]
        assert geek_score.priority_multiplier >= 1.0
    
    def test_calculate_geek_score_tech(self):
        """Testa cálculo de score para oferta tech"""
        geek_score = self.prioritizer.calculate_geek_score(self.tech_offer)
        
        assert isinstance(geek_score, GeekScore)
        assert geek_score.overall_score > 0.2  # Tech deve ter score médio
        assert "gaming" in geek_score.matched_keywords
        assert geek_score.geek_level in ["primary", "secondary", "general"]
    
    def test_calculate_geek_score_smart_home(self):
        """Testa cálculo de score para oferta smart home"""
        geek_score = self.prioritizer.calculate_geek_score(self.smart_home_offer)
        
        assert isinstance(geek_score, GeekScore)
        assert geek_score.overall_score > 0.1  # Smart home deve ter score baixo-médio
        assert "smart tv" in geek_score.matched_keywords
        assert geek_score.geek_level in ["primary", "secondary", "general"]
    
    def test_calculate_geek_score_audio(self):
        """Testa cálculo de score para oferta de audio"""
        geek_score = self.prioritizer.calculate_geek_score(self.audio_offer)
        
        assert isinstance(geek_score, GeekScore)
        assert geek_score.overall_score > 0.2  # Audio premium deve ter score médio
        assert "headphone" in geek_score.matched_keywords
        assert "bluetooth" in geek_score.matched_keywords
    
    def test_calculate_geek_score_general(self):
        """Testa cálculo de score para oferta geral"""
        geek_score = self.prioritizer.calculate_geek_score(self.general_offer)
        
        assert isinstance(geek_score, GeekScore)
        assert geek_score.overall_score < 0.3  # Produto geral deve ter score baixo
        assert geek_score.geek_level == "general"
        assert geek_score.priority_multiplier == 1.0
    
    def test_prioritize_offers(self):
        """Testa priorização de lista de ofertas"""
        offers = [
            self.general_offer,
            self.audio_offer,
            self.smart_home_offer,
            self.tech_offer,
            self.gaming_offer
        ]
        
        prioritized = self.prioritizer.prioritize_offers(offers)
        
        assert len(prioritized) == 5
        assert prioritized[0][1].overall_score >= prioritized[1][1].overall_score
        assert "PlayStation" in prioritized[0][0].title  # PlayStation deve ser primeiro
        assert "Cabo USB" in prioritized[-1][0].title  # Cabo deve ser último
    
    def test_evaluate_category_gaming(self):
        """Testa avaliação específica de categoria gaming"""
        score = self.prioritizer._evaluate_category(self.gaming_offer)
        assert score > 0.8  # Gaming deve ter score alto
    
    def test_evaluate_keywords_gaming(self):
        """Testa avaliação de palavras-chave gaming"""
        score = self.prioritizer._evaluate_keywords(self.gaming_offer)
        assert score > 0.3  # Deve encontrar várias palavras-chave
    
    def test_evaluate_product_type_tech(self):
        """Testa avaliação de tipo de produto tech"""
        score = self.prioritizer._evaluate_product_type(self.tech_offer)
        assert score > 0.2  # RTX deve ser considerado produto tech
    
    def test_determine_geek_level(self):
        """Testa determinação do nível geek"""
        # Testar diferentes scores
        assert self.prioritizer._determine_geek_level(0.95) == "primary"
        assert self.prioritizer._determine_geek_level(0.85) == "primary"
        assert self.prioritizer._determine_geek_level(0.75) == "primary"
        assert self.prioritizer._determine_geek_level(0.45) == "general"
    
    def test_calculate_priority_multiplier(self):
        """Testa cálculo do multiplicador de prioridade"""
        # Testar diferentes níveis
        assert self.prioritizer._calculate_priority_multiplier(0.95, "primary") > 1.0
        assert self.prioritizer._calculate_priority_multiplier(0.85, "secondary") >= 1.0
        assert self.prioritizer._calculate_priority_multiplier(0.45, "general") == 1.0

class TestGeekAlertManager:
    """Testes para o GeekAlertManager"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.alert_manager = GeekAlertManager()
        
        # Mock do prioritizador
        self.mock_geek_score = Mock(spec=GeekScore)
        self.mock_geek_score.overall_score = 0.85
        self.mock_geek_score.matched_categories = ["gaming"]
        self.mock_geek_score.matched_keywords = ["playstation", "gaming"]
        
        # Oferta de teste
        self.test_offer = Offer(
            title="PlayStation 5 Console",
            price=Decimal("3999.99"),
            original_price=Decimal("4699.99"),
            discount_percentage=15.0,
            category="consoles_gaming",
            store="Amazon",
            url="https://amzn.to/ps5",
            image_url="https://example.com/ps5.jpg",
            description="Console PlayStation 5",
            stock_quantity=10
        )
    
    @pytest.mark.asyncio
    async def test_alert_manager_initialization(self):
        """Testa inicialização do GeekAlertManager"""
        assert self.alert_manager is not None
        assert hasattr(self.alert_manager, 'alert_config')
        assert hasattr(self.alert_manager, 'alert_history')
        assert self.alert_manager.logger is not None
    
    @pytest.mark.asyncio
    async def test_check_offer_for_alerts_high_score(self):
        """Testa verificação de oferta para alertas com score alto"""
        # Mock do prioritizador para retornar score alto
        with patch.object(self.alert_manager.prioritizer, 'calculate_geek_score', return_value=self.mock_geek_score):
            alert = await self.alert_manager.check_offer_for_alerts(self.test_offer)
            
            assert alert is not None
            assert alert.offer.title == "PlayStation 5 Console"
            assert alert.priority in ["high", "critical"]
            assert alert.alert_type in ["high_priority", "price_drop"]
    
    @pytest.mark.asyncio
    async def test_check_offer_for_alerts_low_score(self):
        """Testa verificação de oferta para alertas com score baixo"""
        # Mock do prioritizador para retornar score baixo
        low_score_mock = Mock(spec=GeekScore)
        low_score_mock.overall_score = 0.3
        
        with patch.object(self.alert_manager.prioritizer, 'calculate_geek_score', return_value=low_score_mock):
            alert = await self.alert_manager.check_offer_for_alerts(self.test_offer)
            
            assert alert is None  # Não deve gerar alerta
    
    @pytest.mark.asyncio
    async def test_create_geek_alert(self):
        """Testa criação de alerta geek"""
        alert = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        
        assert alert is not None
        assert alert.offer.title == "PlayStation 5 Console"
        assert alert.geek_score == self.mock_geek_score
        assert alert.created_at is not None
        assert not alert.sent
    
    def test_determine_alert_details(self):
        """Testa determinação de detalhes do alerta"""
        alert_type, priority, message = self.alert_manager._determine_alert_details(
            self.test_offer, self.mock_geek_score
        )
        
        assert alert_type in ["high_priority", "price_drop", "limited_stock"]
        assert priority in ["critical", "high", "medium"]
        assert "ALERTA GEEK" in message
        assert "SCORE GEEK" in message
        assert "PREÇO" in message
    
    @pytest.mark.asyncio
    async def test_get_pending_alerts(self):
        """Testa obtenção de alertas pendentes"""
        # Criar alguns alertas
        alert1 = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        alert2 = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        
        # Verificar que ambos estão pendentes inicialmente
        pending_initial = await self.alert_manager.get_pending_alerts()
        assert len(pending_initial) == 2
        
        # Marcar um como enviado
        await self.alert_manager.mark_alert_sent(alert1)
        
        # Verificar alertas pendentes
        pending = await self.alert_manager.get_pending_alerts()
        assert len(pending) == 1
        assert pending[0].offer.title == alert2.offer.title
    
    @pytest.mark.asyncio
    async def test_mark_alert_sent(self):
        """Testa marcação de alerta como enviado"""
        alert = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        
        success = await self.alert_manager.mark_alert_sent(alert)
        assert success
        assert alert.sent
        assert alert.sent_at is not None
    
    @pytest.mark.asyncio
    async def test_get_alert_stats(self):
        """Testa obtenção de estatísticas de alertas"""
        # Criar alguns alertas
        await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        
        stats = await self.alert_manager.get_alert_stats()
        
        assert "total_alerts" in stats
        assert "pending_alerts" in stats
        assert "sent_alerts" in stats
        assert "priority_counts" in stats
        assert "type_counts" in stats
    
    @pytest.mark.asyncio
    async def test_clear_old_alerts(self):
        """Testa limpeza de alertas antigos"""
        # Criar alerta antigo
        old_alert = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        old_alert.created_at = datetime.now() - timedelta(days=10)
        
        # Criar alerta recente
        recent_alert = await self.alert_manager._create_geek_alert(self.test_offer, self.mock_geek_score)
        
        # Verificar que ambos estão no histórico
        assert len(self.alert_manager.alert_history) == 2
        
        # Limpar alertas antigos
        removed_count = await self.alert_manager.clear_old_alerts(days=7)
        
        assert removed_count == 1
        assert len(self.alert_manager.alert_history) == 1
        assert self.alert_manager.alert_history[0].offer.title == recent_alert.offer.title

class TestGeekCommands:
    """Testes para o GeekCommands"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.geek_commands = GeekCommands()
    
    def test_geek_commands_initialization(self):
        """Testa inicialização do GeekCommands"""
        assert self.geek_commands is not None
        assert hasattr(self.geek_commands, 'available_commands')
        assert len(self.geek_commands.available_commands) > 0
        assert "/geek" in self.geek_commands.available_commands
    
    @pytest.mark.asyncio
    async def test_handle_geek_command_valid(self):
        """Testa processamento de comando geek válido"""
        response = await self.geek_commands.handle_geek_command("/geek", [], 123)
        
        assert response is not None
        assert "OFERTAS GEEK PRIORITÁRIAS" in response
        assert "PlayStation 5" in response
    
    @pytest.mark.asyncio
    async def test_handle_geek_command_invalid(self):
        """Testa processamento de comando geek inválido"""
        response = await self.geek_commands.handle_geek_command("/invalid", [], 123)
        
        assert "não reconhecido" in response
    
    @pytest.mark.asyncio
    async def test_show_gaming_offers(self):
        """Testa comando de ofertas gaming"""
        response = await self.geek_commands._show_gaming_offers([], 123)
        
        assert "OFERTAS GAMING EXCLUSIVAS" in response
        assert "PlayStation 5" in response
        assert "Nintendo Switch" in response
    
    @pytest.mark.asyncio
    async def test_show_tech_offers(self):
        """Testa comando de ofertas tech"""
        response = await self.geek_commands._show_tech_offers([], 123)
        
        assert "OFERTAS TECH PREMIUM" in response
        assert "MacBook Air" in response
        assert "Samsung Galaxy" in response
    
    @pytest.mark.asyncio
    async def test_show_anime_offers(self):
        """Testa comando de ofertas anime"""
        response = await self.geek_commands._show_anime_offers([], 123)
        
        assert "OFERTAS ANIME & OTAKU" in response
        assert "Goku Ultra Instinct" in response
        assert "One Piece" in response
    
    @pytest.mark.asyncio
    async def test_show_smart_home_offers(self):
        """Testa comando de ofertas smart home"""
        response = await self.geek_commands._show_smart_home_offers([], 123)
        
        assert "OFERTAS SMART HOME & IOT" in response
        assert "Smart TV Samsung" in response
        assert "Echo Dot" in response
    
    @pytest.mark.asyncio
    async def test_show_audio_offers(self):
        """Testa comando de ofertas audio"""
        response = await self.geek_commands._show_audio_offers([], 123)
        
        assert "OFERTAS AUDIO PREMIUM" in response
        assert "Headphone Sony" in response
        assert "Headset Gaming" in response
    
    @pytest.mark.asyncio
    async def test_show_collectibles_offers(self):
        """Testa comando de ofertas collectibles"""
        response = await self.geek_commands._show_collectibles_offers([], 123)
        
        assert "OFERTAS COLLECTIBLES" in response
        assert "Funko Pop!" in response
        assert "Action Figure" in response
    
    @pytest.mark.asyncio
    async def test_show_geek_stats(self):
        """Testa comando de estatísticas geek"""
        response = await self.geek_commands._show_geek_stats(123)
        
        assert "ESTATÍSTICAS GEEK DO SISTEMA" in response
        assert "RESUMO GERAL" in response
        assert "DISTRIBUIÇÃO POR CATEGORIA" in response
        assert "ALERTAS E PRIORIDADES" in response
    
    def test_show_geek_help(self):
        """Testa comando de ajuda geek"""
        response = self.geek_commands._show_geek_help()
        
        assert "AJUDA - COMANDOS GEEK" in response
        assert "COMANDOS PRINCIPAIS" in response
        assert "CATEGORIAS PRIORITÁRIAS" in response
        assert "SISTEMA DE SCORES" in response
    
    def test_get_available_commands(self):
        """Testa obtenção de comandos disponíveis"""
        commands = self.geek_commands.get_available_commands()
        
        assert isinstance(commands, dict)
        assert "/geek" in commands
        assert "/gaming" in commands
        assert "/tech" in commands
        assert "/anime" in commands
    
    @pytest.mark.asyncio
    async def test_get_user_preferences(self):
        """Testa obtenção de preferências do usuário"""
        preferences = await self.geek_commands.get_user_preferences(123)
        
        assert isinstance(preferences, dict)
        assert "favorite_categories" in preferences
        assert "min_score_threshold" in preferences
        assert "notification_enabled" in preferences
    
    @pytest.mark.asyncio
    async def test_update_user_preferences(self):
        """Testa atualização de preferências do usuário"""
        new_preferences = {
            "favorite_categories": ["gaming", "anime"],
            "min_score_threshold": 0.8
        }
        
        success = await self.geek_commands.update_user_preferences(123, new_preferences)
        assert success

class TestGeekSystemIntegration:
    """Testes de integração do sistema geek completo"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.prioritizer = GeekPrioritizer()
        self.alert_manager = GeekAlertManager()
        self.geek_commands = GeekCommands()
        
        # Oferta de teste
        self.test_offer = Offer(
            title="PlayStation 5 Console Gaming + RTX 4070 Ti Bundle",
            price=Decimal("7999.99"),
            original_price=Decimal("9999.99"),
            discount_percentage=20.0,
            category="consoles_gaming",
            store="Amazon",
            url="https://amzn.to/bundle",
            image_url="https://example.com/bundle.jpg",
            description="Bundle completo para gaming",
            stock_quantity=3
        )
    
    @pytest.mark.asyncio
    async def test_complete_geek_workflow(self):
        """Testa workflow completo do sistema geek"""
        # 1. Calcular score geek
        geek_score = self.prioritizer.calculate_geek_score(self.test_offer)
        assert geek_score.overall_score > 0.5  # Score deve ser pelo menos médio
        
        # 2. Verificar se deve gerar alerta (pode não gerar se score for baixo)
        alert = await self.alert_manager.check_offer_for_alerts(self.test_offer)
        if alert:
            assert alert.priority in ["high", "critical"]
        else:
            # Se não gerou alerta, verificar se é porque o score é baixo
            assert geek_score.overall_score < self.alert_manager.alert_config["high_priority_threshold"]
        
        # 3. Processar comando geek
        response = await self.geek_commands._show_geek_offers([], 123)
        assert "OFERTAS GEEK PRIORITÁRIAS" in response
    
    @pytest.mark.asyncio
    async def test_geek_prioritization_consistency(self):
        """Testa consistência da priorização geek"""
        offers = [
            Offer(title="Gaming Chair RGB", price=Decimal("299.99"), category="gaming", store="Amazon", url="https://amzn.to/chair"),
            Offer(title="Cabo USB Genérico", price=Decimal("9.99"), category="cables", store="AliExpress", url="https://aliexpress.com/cable"),
            Offer(title="RTX 4080 Gaming", price=Decimal("5999.99"), category="placas_video", store="Kabum", url="https://kabum.com/rtx4080"),
        ]
        
        # Priorizar ofertas
        prioritized = self.prioritizer.prioritize_offers(offers)
        
        # Verificar que a priorização está funcionando (score mais alto primeiro)
        assert prioritized[0][1].overall_score >= prioritized[1][1].overall_score
        assert prioritized[1][1].overall_score >= prioritized[2][1].overall_score
        
        # Verificar que os produtos estão na lista
        titles = [offer.title for offer, _ in prioritized]
        assert any("RTX" in title for title in titles)
        assert any("Gaming Chair" in title for title in titles)
        assert any("Cabo USB" in title for title in titles)
    
    def test_geek_configuration_consistency(self):
        """Testa consistência da configuração geek"""
        config = self.prioritizer.geek_config
        
        # Verificar se categorias primárias têm scores altos
        for cat_name, cat_info in config["primary_categories"].items():
            assert cat_info["priority_score"] >= 0.8
            assert "keywords" in cat_info
            assert "subcategories" in cat_info
        
        # Verificar se categorias secundárias têm scores médios
        for cat_name, cat_info in config["secondary_categories"].items():
            assert 0.4 <= cat_info["priority_score"] <= 0.7
        
        # Verificar configurações de priorização
        prioritization = config["prioritization"]
        assert prioritization["min_geek_score"] >= 0.5
        assert prioritization["geek_boost_multiplier"] > 1.0
        assert sum([
            prioritization["category_matching_weight"],
            prioritization["keyword_matching_weight"],
            prioritization["price_quality_weight"]
        ]) == 1.0

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
