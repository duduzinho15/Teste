"""
Demonstração do Sistema de Integração com Afiliados
==================================================

Este script demonstra as funcionalidades do sistema de integração
com redes de afiliados reais para o Garimpeiro Geek.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.affiliate_integration import (
    AffiliateIntegrationManager,
    AffiliateConfig,
    AffiliateNetwork,
    AffiliateProduct,
    LinkValidationResult,
    AffiliateMetrics
)
from src.core.affiliate_dashboard import AffiliateDashboard


class AffiliateIntegrationDemo:
    """Demonstração do sistema de integração com afiliados"""
    
    def __init__(self):
        self.manager = AffiliateIntegrationManager()
        self.dashboard = AffiliateDashboard()
        self.demo_links = [
            "https://amazon.com.br/dp/B08N5WRWNW?tag=garimpeirogeek-20",
            "https://awin1.com/cread.php?awinmid=12345&awinaffid=67890",
            "https://shopee.com.br/product/12345/67890?affiliate_id=garimpeirogeek",
            "https://mercadolivre.com.br/items/MLB1234567890?af=garimpeirogeek",
            "https://magazineluiza.com.br/produto/12345?partner_id=garimpeirogeek"
        ]
    
    async def run_full_demo(self):
        """Executa demonstração completa"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA")
        print("="*60)
        
        # 1. Configurar redes de afiliados
        await self.demo_network_configuration()
        
        # 2. Buscar produtos
        await self.demo_product_search()
        
        # 3. Validar links
        await self.demo_link_validation()
        
        # 4. Métricas e relatórios
        await self.demo_metrics_and_reports()
        
        # 5. Dashboard interativo
        await self.demo_dashboard()
        
        print("\n✅ DEMONSTRAÇÃO COMPLETA FINALIZADA!")
    
    async def run_quick_demo(self):
        """Executa demonstração rápida"""
        print("⚡ INICIANDO DEMONSTRAÇÃO RÁPIDA")
        print("="*50)
        
        # 1. Configuração rápida
        await self.quick_network_setup()
        
        # 2. Validação de links
        await self.quick_link_validation()
        
        # 3. Busca rápida
        await self.quick_product_search()
        
        print("\n✅ DEMONSTRAÇÃO RÁPIDA FINALIZADA!")
    
    async def demo_network_configuration(self):
        """Demonstra configuração de redes"""
        print("\n📋 CONFIGURAÇÃO DE REDES DE AFILIADOS")
        print("-"*50)
        
        # Configurar Amazon
        amazon_config = AffiliateConfig(
            network=AffiliateNetwork.AMAZON,
            api_key="demo_amazon_key_123",
            api_secret="",
            timeout=30,
            retry_attempts=3,
            rate_limit_delay=1.0,
            priority=1
        )
        
        # Configurar Awin
        awin_config = AffiliateConfig(
            network=AffiliateNetwork.AWIN,
            api_key="demo_awin_key_456",
            api_secret="demo_awin_secret_789",
            timeout=30,
            retry_attempts=3,
            rate_limit_delay=1.0,
            priority=2
        )
        
        # Configurar Hotmart
        hotmart_config = AffiliateConfig(
            network=AffiliateNetwork.HOTMART,
            api_key="demo_hotmart_key_101",
            api_secret="",
            timeout=30,
            retry_attempts=3,
            rate_limit_delay=1.0,
            priority=3
        )
        
        try:
            await self.manager.add_network_config(amazon_config)
            print("✅ Amazon configurada")
            
            await self.manager.add_network_config(awin_config)
            print("✅ Awin configurada")
            
            await self.manager.add_network_config(hotmart_config)
            print("✅ Hotmart configurada")
            
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
    
    async def demo_product_search(self):
        """Demonstra busca de produtos"""
        print("\n🔍 BUSCA DE PRODUTOS")
        print("-"*30)
        
        # Produtos simulados para demonstração
        demo_products = [
            AffiliateProduct(
                id="B08N5WRWNW",
                name="Headphone Gamer RGB com Microfone",
                description="Headphone profissional para gamers com iluminação RGB e microfone integrado",
                price=299.90,
                original_price=399.90,
                discount_percentage=25.0,
                category="Eletrônicos",
                subcategory="Headphones",
                affiliate_link="https://amazon.com.br/dp/B08N5WRWNW?tag=garimpeirogeek-20",
                network=AffiliateNetwork.AMAZON,
                commission_rate=0.04,
                image_url="https://example.com/headphone.jpg"
            ),
            AffiliateProduct(
                id="B07XYZ123",
                name="Mouse Gamer RGB 16000 DPI",
                description="Mouse gaming com sensor óptico de alta precisão e 7 botões programáveis",
                price=189.90,
                original_price=249.90,
                discount_percentage=24.0,
                category="Eletrônicos",
                subcategory="Mouses",
                affiliate_link="https://amazon.com.br/dp/B07XYZ123?tag=garimpeirogeek-20",
                network=AffiliateNetwork.AMAZON,
                commission_rate=0.04,
                image_url="https://example.com/mouse.jpg"
            ),
            AffiliateProduct(
                id="curso_python_geek",
                name="Curso Python para Geeks",
                description="Aprenda Python do zero ao avançado com projetos práticos",
                price=197.00,
                original_price=397.00,
                discount_percentage=50.4,
                category="Educação",
                subcategory="Programação",
                affiliate_link="https://hotmart.com/pt-br/marketplace/produtos/curso-python-geek-ref=garimpeirogeek",
                network=AffiliateNetwork.HOTMART,
                commission_rate=0.15,
                image_url="https://example.com/curso.jpg"
            )
        ]
        
        print("🔍 Buscando produtos 'gamer'...")
        await asyncio.sleep(1)
        
        print(f"✅ Encontrados {len(demo_products)} produtos:")
        for i, product in enumerate(demo_products, 1):
            print(f"\n{i}. {product.name}")
            print(f"   💰 Preço: R$ {product.price:.2f} (De: R$ {product.original_price:.2f})")
            print(f"   📉 Desconto: {product.discount_percentage:.1f}%")
            print(f"   🏷️ Categoria: {product.category} > {product.subcategory}")
            print(f"   🔗 Rede: {product.network.value}")
            print(f"   💸 Comissão: {product.commission_rate*100:.1f}%")
        
        # Salvar produtos
        try:
            await self.manager.save_products(demo_products)
            print("\n💾 Produtos salvos no banco de dados!")
        except Exception as e:
            print(f"❌ Erro ao salvar produtos: {e}")
    
    async def demo_link_validation(self):
        """Demonstra validação de links"""
        print("\n✅ VALIDAÇÃO DE LINKS")
        print("-"*30)
        
        print(f"🔍 Validando {len(self.demo_links)} links...")
        
        try:
            results = await self.manager.validate_links(self.demo_links)
            
            valid_count = sum(1 for r in results if r.is_valid)
            print(f"\n📊 RESULTADOS DA VALIDAÇÃO:")
            print(f"   Total: {len(results)}")
            print(f"   ✅ Válidos: {valid_count}")
            print(f"   ❌ Inválidos: {len(results) - valid_count}")
            print(f"   📈 Taxa de sucesso: {valid_count/len(results)*100:.1f}%")
            
            print(f"\n📋 DETALHES:")
            for i, result in enumerate(results, 1):
                status_icon = "✅" if result.is_valid else "❌"
                print(f"{i}. {status_icon} {result.network.value}: {result.url[:50]}...")
                if result.error_message:
                    print(f"   Erro: {result.error_message}")
                print(f"   Tempo: {result.response_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
    
    async def demo_metrics_and_reports(self):
        """Demonstra métricas e relatórios"""
        print("\n📊 MÉTRICAS E RELATÓRIOS")
        print("-"*30)
        
        # Estatísticas de validação
        try:
            stats = await self.manager.get_validation_statistics()
            
            print("📈 ESTATÍSTICAS DE VALIDAÇÃO:")
            print(f"   Total de validações: {stats['total_validations']}")
            print(f"   Links válidos: {stats['valid_links']}")
            print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
            print(f"   Tempo médio: {stats['avg_response_time']:.2f}s")
            
            if stats['network_statistics']:
                print(f"\n📊 POR REDE:")
                for network, data in stats['network_statistics'].items():
                    success_rate = (data['valid'] / data['total'] * 100) if data['total'] > 0 else 0
                    print(f"   {network}: {data['valid']}/{data['total']} ({success_rate:.1f}%)")
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
        
        # Métricas simuladas por rede
        print(f"\n💰 MÉTRICAS FINANCEIRAS (SIMULADAS):")
        
        networks = [AffiliateNetwork.AMAZON, AffiliateNetwork.AWIN, AffiliateNetwork.HOTMART]
        for network in networks:
            metrics = AffiliateMetrics(
                network=network,
                total_clicks=1000 + hash(network.value) % 500,
                total_conversions=50 + hash(network.value) % 30,
                conversion_rate=5.2 + hash(network.value) % 3,
                total_revenue=5000.0 + hash(network.value) % 2000,
                total_commission=250.0 + hash(network.value) % 100,
                ctr=2.5 + hash(network.value) % 2,
                epc=0.25 + hash(network.value) % 0.2,
                date_range="Últimos 30 dias",
                period="daily"
            )
            
            print(f"\n🔗 {network.value.upper()}:")
            print(f"   👆 Cliques: {metrics.total_clicks:,}")
            print(f"   💰 Conversões: {metrics.total_conversions:,}")
            print(f"   📊 Taxa de conversão: {metrics.conversion_rate:.2f}%")
            print(f"   💵 Receita: R$ {metrics.total_revenue:.2f}")
            print(f"   💸 Comissão: R$ {metrics.total_commission:.2f}")
            print(f"   📈 CTR: {metrics.ctr:.2f}%")
            print(f"   💎 EPC: R$ {metrics.epc:.2f}")
    
    async def demo_dashboard(self):
        """Demonstra dashboard interativo"""
        print("\n🎛️ DASHBOARD INTERATIVO")
        print("-"*30)
        print("Abrindo dashboard de integração com afiliados...")
        print("(Para demonstração, vamos simular algumas funcionalidades)")
        
        # Simular algumas operações do dashboard
        await asyncio.sleep(1)
        print("✅ Dashboard carregado!")
        
        # Simular busca por categoria
        print("\n🔍 Buscando produtos na categoria 'Gamer'...")
        await asyncio.sleep(1)
        
        gamer_products = [
            AffiliateProduct(
                id="gamer_1",
                name="Teclado Mecânico RGB",
                description="Teclado gaming com switches mecânicos",
                price=450.00,
                original_price=600.00,
                discount_percentage=25.0,
                category="Eletrônicos",
                subcategory="Teclados",
                affiliate_link="https://example.com/teclado",
                network=AffiliateNetwork.AMAZON,
                commission_rate=0.04
            ),
            AffiliateProduct(
                id="gamer_2",
                name="Mousepad RGB XXL",
                description="Mousepad gaming com iluminação RGB",
                price=89.90,
                original_price=129.90,
                discount_percentage=30.8,
                category="Eletrônicos",
                subcategory="Acessórios",
                affiliate_link="https://example.com/mousepad",
                network=AffiliateNetwork.AMAZON,
                commission_rate=0.04
            )
        ]
        
        print(f"✅ Encontrados {len(gamer_products)} produtos Gamer:")
        for product in gamer_products:
            print(f"   🎮 {product.name} - R$ {product.price:.2f}")
    
    async def quick_network_setup(self):
        """Configuração rápida de redes"""
        print("\n⚡ CONFIGURAÇÃO RÁPIDA")
        print("-"*25)
        
        # Configurar apenas Amazon para demonstração rápida
        amazon_config = AffiliateConfig(
            network=AffiliateNetwork.AMAZON,
            api_key="quick_demo_key",
            timeout=30,
            priority=1
        )
        
        try:
            await self.manager.add_network_config(amazon_config)
            print("✅ Amazon configurada para demonstração")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def quick_link_validation(self):
        """Validação rápida de links"""
        print("\n⚡ VALIDAÇÃO RÁPIDA")
        print("-"*20)
        
        # Validar apenas 2 links para demonstração rápida
        quick_links = self.demo_links[:2]
        
        print(f"🔍 Validando {len(quick_links)} links...")
        
        try:
            results = await self.manager.validate_links(quick_links)
            
            valid_count = sum(1 for r in results if r.is_valid)
            print(f"✅ Resultado: {valid_count}/{len(results)} válidos")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def quick_product_search(self):
        """Busca rápida de produtos"""
        print("\n⚡ BUSCA RÁPIDA")
        print("-"*15)
        
        print("🔍 Buscando produtos 'tech'...")
        await asyncio.sleep(0.5)
        
        # Produto simulado
        tech_product = AffiliateProduct(
            id="tech_demo",
            name="Smartphone Android 128GB",
            description="Smartphone com câmera de 48MP e bateria de 5000mAh",
            price=1299.90,
            original_price=1599.90,
            discount_percentage=18.8,
            category="Eletrônicos",
            subcategory="Smartphones",
            affiliate_link="https://amazon.com.br/dp/TECH123?tag=demo-20",
            network=AffiliateNetwork.AMAZON,
            commission_rate=0.04
        )
        
        print(f"✅ Encontrado: {tech_product.name}")
        print(f"   💰 Preço: R$ {tech_product.price:.2f}")
        print(f"   📉 Desconto: {tech_product.discount_percentage:.1f}%")


async def main():
    """Função principal"""
    import sys
    
    demo = AffiliateIntegrationDemo()
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await demo.run_quick_demo()
    else:
        await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
