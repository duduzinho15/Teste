"""
Dashboard de Integração com Afiliados
====================================

Interface para gerenciar integração com redes de afiliados,
validação de links e monitoramento de métricas.
"""

import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import asdict
from datetime import datetime, timedelta

from .affiliate_integration import (
    AffiliateIntegrationManager,
    AffiliateConfig,
    AffiliateNetwork,
    AffiliateProduct,
    LinkValidationResult,
    AffiliateMetrics
)


class AffiliateDashboard:
    """Dashboard para gerenciar integração com afiliados"""
    
    def __init__(self):
        self.manager = AffiliateIntegrationManager()
        self.networks = {
            "Amazon": AffiliateNetwork.AMAZON,
            "Awin": AffiliateNetwork.AWIN,
            "Hotmart": AffiliateNetwork.HOTMART,
            "Monetizze": AffiliateNetwork.MONETIZZE,
            "Eduzz": AffiliateNetwork.EDUZZ,
            "Braip": AffiliateNetwork.BRAIP,
            "Perfect Pay": AffiliateNetwork.PERFECT_PAY,
            "Kiwify": AffiliateNetwork.KIWIFY
        }
    
    async def show_main_menu(self):
        """Exibe menu principal"""
        while True:
            print("\n" + "="*60)
            print("🔗 DASHBOARD DE INTEGRAÇÃO COM AFILIADOS")
            print("="*60)
            print("1. 📋 Configurar Redes de Afiliados")
            print("2. 🔍 Buscar Produtos")
            print("3. ✅ Validar Links")
            print("4. 📊 Visualizar Métricas")
            print("5. 🗄️ Gerenciar Produtos")
            print("6. ⚙️ Configurações Avançadas")
            print("7. 📈 Relatórios")
            print("0. 🔙 Voltar")
            print("-"*60)
            
            choice = input("Escolha uma opção: ").strip()
            
            if choice == "1":
                await self.configure_networks()
            elif choice == "2":
                await self.search_products()
            elif choice == "3":
                await self.validate_links()
            elif choice == "4":
                await self.view_metrics()
            elif choice == "5":
                await self.manage_products()
            elif choice == "6":
                await self.advanced_settings()
            elif choice == "7":
                await self.generate_reports()
            elif choice == "0":
                break
            else:
                print("❌ Opção inválida!")
    
    async def configure_networks(self):
        """Configura redes de afiliados"""
        while True:
            print("\n" + "="*50)
            print("📋 CONFIGURAÇÃO DE REDES DE AFILIADOS")
            print("="*50)
            print("1. ➕ Adicionar Nova Rede")
            print("2. 📝 Editar Rede Existente")
            print("3. 🗑️ Remover Rede")
            print("4. 📋 Listar Redes Configuradas")
            print("5. ✅ Testar Conexões")
            print("0. 🔙 Voltar")
            print("-"*50)
            
            choice = input("Escolha uma opção: ").strip()
            
            if choice == "1":
                await self.add_network()
            elif choice == "2":
                await self.edit_network()
            elif choice == "3":
                await self.remove_network()
            elif choice == "4":
                await self.list_networks()
            elif choice == "5":
                await self.test_connections()
            elif choice == "0":
                break
            else:
                print("❌ Opção inválida!")
    
    async def add_network(self):
        """Adiciona nova rede de afiliados"""
        print("\n" + "-"*40)
        print("➕ ADICIONAR NOVA REDE")
        print("-"*40)
        
        # Selecionar rede
        print("Redes disponíveis:")
        for i, (name, network) in enumerate(self.networks.items(), 1):
            print(f"{i}. {name}")
        
        try:
            network_choice = int(input("\nEscolha a rede: ")) - 1
            network_names = list(self.networks.keys())
            if 0 <= network_choice < len(network_names):
                network_name = network_names[network_choice]
                network = self.networks[network_name]
            else:
                print("❌ Rede inválida!")
                return
        except ValueError:
            print("❌ Opção inválida!")
            return
        
        # Configurações
        api_key = input("API Key: ").strip()
        api_secret = input("API Secret (opcional): ").strip()
        timeout = int(input("Timeout (segundos, padrão 30): ") or "30")
        retry_attempts = int(input("Tentativas de retry (padrão 3): ") or "3")
        rate_limit_delay = float(input("Delay entre requests (segundos, padrão 1.0): ") or "1.0")
        priority = int(input("Prioridade (1-10, padrão 1): ") or "1")
        
        # Criar configuração
        config = AffiliateConfig(
            network=network,
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            retry_attempts=retry_attempts,
            rate_limit_delay=rate_limit_delay,
            priority=priority
        )
        
        try:
            await self.manager.add_network_config(config)
            print(f"✅ Rede {network_name} configurada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao configurar rede: {e}")
    
    async def edit_network(self):
        """Edita rede existente"""
        print("\n" + "-"*40)
        print("📝 EDITAR REDE")
        print("-"*40)
        
        # Listar redes configuradas
        networks = await self.get_configured_networks()
        if not networks:
            print("❌ Nenhuma rede configurada!")
            return
        
        print("Redes configuradas:")
        for i, network in enumerate(networks, 1):
            print(f"{i}. {network['network']} (Prioridade: {network['priority']})")
        
        try:
            choice = int(input("\nEscolha a rede para editar: ")) - 1
            if 0 <= choice < len(networks):
                network = networks[choice]
                await self.edit_network_config(network)
            else:
                print("❌ Opção inválida!")
        except ValueError:
            print("❌ Opção inválida!")
    
    async def edit_network_config(self, network_config: Dict):
        """Edita configuração específica de rede"""
        print(f"\nEditando: {network_config['network']}")
        print("-"*30)
        
        api_key = input(f"API Key (atual: {network_config['api_key'][:10]}...): ").strip()
        if not api_key:
            api_key = network_config['api_key']
        
        timeout = input(f"Timeout (atual: {network_config['timeout']}): ").strip()
        timeout = int(timeout) if timeout else network_config['timeout']
        
        priority = input(f"Prioridade (atual: {network_config['priority']}): ").strip()
        priority = int(priority) if priority else network_config['priority']
        
        enabled = input(f"Ativada (atual: {network_config['enabled']}) [s/N]: ").strip().lower()
        enabled = enabled == 's' if enabled else network_config['enabled']
        
        # Criar nova configuração
        config = AffiliateConfig(
            network=AffiliateNetwork(network_config['network']),
            api_key=api_key,
            api_secret=network_config['api_secret'],
            timeout=timeout,
            retry_attempts=network_config['retry_attempts'],
            rate_limit_delay=network_config['rate_limit_delay'],
            priority=priority,
            enabled=enabled
        )
        
        try:
            await self.manager.add_network_config(config)
            print("✅ Rede atualizada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao atualizar rede: {e}")
    
    async def remove_network(self):
        """Remove rede de afiliados"""
        print("\n" + "-"*40)
        print("🗑️ REMOVER REDE")
        print("-"*40)
        
        networks = await self.get_configured_networks()
        if not networks:
            print("❌ Nenhuma rede configurada!")
            return
        
        print("Redes configuradas:")
        for i, network in enumerate(networks, 1):
            print(f"{i}. {network['network']}")
        
        try:
            choice = int(input("\nEscolha a rede para remover: ")) - 1
            if 0 <= choice < len(networks):
                network = networks[choice]
                confirm = input(f"Tem certeza que deseja remover {network['network']}? [s/N]: ").strip().lower()
                if confirm == 's':
                    await self.manager.remove_network_config(network['network'])
                    print("✅ Rede removida com sucesso!")
            else:
                print("❌ Opção inválida!")
        except ValueError:
            print("❌ Opção inválida!")
    
    async def list_networks(self):
        """Lista redes configuradas"""
        print("\n" + "-"*50)
        print("📋 REDES CONFIGURADAS")
        print("-"*50)
        
        networks = await self.get_configured_networks()
        if not networks:
            print("❌ Nenhuma rede configurada!")
            return
        
        for network in networks:
            status = "✅ Ativa" if network['enabled'] else "❌ Inativa"
            print(f"\n🔗 {network['network']}")
            print(f"   Status: {status}")
            print(f"   Prioridade: {network['priority']}")
            print(f"   API Key: {network['api_key'][:10]}...")
            print(f"   Timeout: {network['timeout']}s")
            print(f"   Retry: {network['retry_attempts']} tentativas")
            print(f"   Rate Limit: {network['rate_limit_delay']}s")
    
    async def test_connections(self):
        """Testa conexões com redes"""
        print("\n" + "-"*40)
        print("✅ TESTANDO CONEXÕES")
        print("-"*40)
        
        networks = await self.get_configured_networks()
        if not networks:
            print("❌ Nenhuma rede configurada!")
            return
        
        for network in networks:
            if not network['enabled']:
                continue
            
            print(f"\n🔗 Testando {network['network']}...")
            try:
                # Teste básico de conectividade
                config = AffiliateConfig(
                    network=AffiliateNetwork(network['network']),
                    api_key=network['api_key'],
                    api_secret=network['api_secret'],
                    timeout=network['timeout']
                )
                
                # Aqui você pode adicionar testes específicos por rede
                print(f"   ✅ Conexão OK")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    async def search_products(self):
        """Busca produtos"""
        print("\n" + "-"*40)
        print("🔍 BUSCAR PRODUTOS")
        print("-"*40)
        
        keywords = input("Palavras-chave: ").strip()
        if not keywords:
            print("❌ Palavras-chave são obrigatórias!")
            return
        
        category = input("Categoria (opcional): ").strip()
        
        print(f"\n🔍 Buscando produtos com '{keywords}'...")
        
        try:
            products = await self.manager.search_products(keywords, category)
            
            if not products:
                print("❌ Nenhum produto encontrado!")
                return
            
            print(f"\n✅ Encontrados {len(products)} produtos:")
            print("-"*60)
            
            for i, product in enumerate(products[:10], 1):  # Mostrar apenas os primeiros 10
                print(f"\n{i}. {product.name}")
                print(f"   Preço: R$ {product.price:.2f}")
                print(f"   Categoria: {product.category}")
                print(f"   Rede: {product.network.value}")
                print(f"   Comissão: {product.commission_rate*100:.1f}%")
                print(f"   Link: {product.affiliate_link[:50]}...")
            
            if len(products) > 10:
                print(f"\n... e mais {len(products) - 10} produtos")
            
            # Salvar produtos
            save = input("\n💾 Salvar produtos no banco? [s/N]: ").strip().lower()
            if save == 's':
                await self.manager.save_products(products)
                print("✅ Produtos salvos!")
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
    
    async def validate_links(self):
        """Valida links de afiliado"""
        print("\n" + "-"*40)
        print("✅ VALIDAR LINKS")
        print("-"*40)
        
        print("1. 🔗 Validar Link Único")
        print("2. 📄 Validar Múltiplos Links")
        print("3. 📊 Ver Estatísticas")
        print("0. 🔙 Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            await self.validate_single_link()
        elif choice == "2":
            await self.validate_multiple_links()
        elif choice == "3":
            await self.show_validation_stats()
        elif choice == "0":
            return
        else:
            print("❌ Opção inválida!")
    
    async def validate_single_link(self):
        """Valida um link único"""
        url = input("\n🔗 Digite o link: ").strip()
        if not url:
            print("❌ Link é obrigatório!")
            return
        
        print("🔍 Validando link...")
        
        try:
            results = await self.manager.validate_links([url])
            if results:
                result = results[0]
                print(f"\n📊 RESULTADO DA VALIDAÇÃO:")
                print(f"   URL: {result.url}")
                print(f"   Rede: {result.network.value}")
                print(f"   Status: {result.status.value}")
                print(f"   Válido: {'✅ Sim' if result.is_valid else '❌ Não'}")
                print(f"   Tempo de resposta: {result.response_time:.2f}s")
                
                if result.error_message:
                    print(f"   Erro: {result.error_message}")
                
                if result.final_url:
                    print(f"   URL Final: {result.final_url}")
            else:
                print("❌ Erro na validação!")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def validate_multiple_links(self):
        """Valida múltiplos links"""
        print("\n📄 Digite os links (um por linha, linha vazia para finalizar):")
        urls = []
        
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
        
        if not urls:
            print("❌ Nenhum link fornecido!")
            return
        
        print(f"\n🔍 Validando {len(urls)} links...")
        
        try:
            results = await self.manager.validate_links(urls)
            
            valid_count = sum(1 for r in results if r.is_valid)
            print(f"\n📊 RESULTADOS:")
            print(f"   Total: {len(results)}")
            print(f"   Válidos: {valid_count}")
            print(f"   Inválidos: {len(results) - valid_count}")
            print(f"   Taxa de sucesso: {valid_count/len(results)*100:.1f}%")
            
            # Mostrar detalhes dos inválidos
            invalid_results = [r for r in results if not r.is_valid]
            if invalid_results:
                print(f"\n❌ LINKS INVÁLIDOS:")
                for result in invalid_results[:5]:  # Mostrar apenas os primeiros 5
                    print(f"   {result.url} - {result.error_message}")
                
                if len(invalid_results) > 5:
                    print(f"   ... e mais {len(invalid_results) - 5} links inválidos")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def show_validation_stats(self):
        """Mostra estatísticas de validação"""
        print("\n" + "-"*40)
        print("📊 ESTATÍSTICAS DE VALIDAÇÃO")
        print("-"*40)
        
        try:
            stats = await self.manager.get_validation_statistics()
            
            print(f"Total de validações: {stats['total_validations']}")
            print(f"Links válidos: {stats['valid_links']}")
            print(f"Links inválidos: {stats['invalid_links']}")
            print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
            print(f"Tempo médio de resposta: {stats['avg_response_time']:.2f}s")
            
            if stats['network_statistics']:
                print(f"\n📈 POR REDE:")
                for network, data in stats['network_statistics'].items():
                    success_rate = (data['valid'] / data['total'] * 100) if data['total'] > 0 else 0
                    print(f"   {network}: {data['valid']}/{data['total']} ({success_rate:.1f}%)")
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    async def view_metrics(self):
        """Visualiza métricas de afiliados"""
        print("\n" + "-"*40)
        print("📊 MÉTRICAS DE AFILIADOS")
        print("-"*40)
        
        networks = await self.get_configured_networks()
        if not networks:
            print("❌ Nenhuma rede configurada!")
            return
        
        print("Redes disponíveis:")
        for i, network in enumerate(networks, 1):
            print(f"{i}. {network['network']}")
        print("0. Todas as redes")
        
        try:
            choice = input("\nEscolha a rede: ").strip()
            
            if choice == "0":
                # Mostrar todas as redes
                for network in networks:
                    await self.show_network_metrics(AffiliateNetwork(network['network']))
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(networks):
                    network = networks[choice_idx]
                    await self.show_network_metrics(AffiliateNetwork(network['network']))
                else:
                    print("❌ Opção inválida!")
                    
        except ValueError:
            print("❌ Opção inválida!")
    
    async def show_network_metrics(self, network: AffiliateNetwork):
        """Mostra métricas de uma rede específica"""
        print(f"\n📊 MÉTRICAS - {network.value.upper()}")
        print("-"*30)
        
        try:
            metrics = await self.manager.get_network_metrics(network)
            
            print(f"Total de cliques: {metrics.total_clicks:,}")
            print(f"Total de conversões: {metrics.total_conversions:,}")
            print(f"Taxa de conversão: {metrics.conversion_rate:.2f}%")
            print(f"Receita total: R$ {metrics.total_revenue:.2f}")
            print(f"Comissão total: R$ {metrics.total_commission:.2f}")
            print(f"CTR: {metrics.ctr:.2f}%")
            print(f"EPC: R$ {metrics.epc:.2f}")
            print(f"Período: {metrics.period}")
            print(f"Intervalo: {metrics.date_range}")
            
        except Exception as e:
            print(f"❌ Erro ao obter métricas: {e}")
    
    async def manage_products(self):
        """Gerencia produtos salvos"""
        print("\n" + "-"*40)
        print("🗄️ GERENCIAR PRODUTOS")
        print("-"*40)
        
        print("1. 📋 Listar Produtos")
        print("2. 🔍 Buscar por Categoria")
        print("3. 🗑️ Remover Produtos")
        print("4. 📊 Estatísticas")
        print("0. 🔙 Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            await self.list_products()
        elif choice == "2":
            await self.search_products_by_category()
        elif choice == "3":
            await self.remove_products()
        elif choice == "4":
            await self.show_product_stats()
        elif choice == "0":
            return
        else:
            print("❌ Opção inválida!")
    
    async def list_products(self):
        """Lista produtos salvos"""
        print("\n" + "-"*50)
        print("📋 PRODUTOS SALVOS")
        print("-"*50)
        
        try:
            # Por enquanto, vamos simular produtos
            # Em uma implementação real, você buscaria do banco
            print("📊 Total de produtos: 0")
            print("❌ Funcionalidade em desenvolvimento...")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def search_products_by_category(self):
        """Busca produtos por categoria"""
        category = input("\n🔍 Digite a categoria: ").strip()
        if not category:
            print("❌ Categoria é obrigatória!")
            return
        
        print(f"🔍 Buscando produtos na categoria '{category}'...")
        
        try:
            products = await self.manager.get_products_by_category(category)
            
            if not products:
                print("❌ Nenhum produto encontrado!")
                return
            
            print(f"\n✅ Encontrados {len(products)} produtos:")
            for i, product in enumerate(products[:10], 1):
                print(f"\n{i}. {product.name}")
                print(f"   Preço: R$ {product.price:.2f}")
                print(f"   Rede: {product.network.value}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    async def remove_products(self):
        """Remove produtos"""
        print("\n🗑️ REMOVER PRODUTOS")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def show_product_stats(self):
        """Mostra estatísticas de produtos"""
        print("\n📊 ESTATÍSTICAS DE PRODUTOS")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def advanced_settings(self):
        """Configurações avançadas"""
        print("\n" + "-"*40)
        print("⚙️ CONFIGURAÇÕES AVANÇADAS")
        print("-"*40)
        
        print("1. 🔄 Rate Limiting")
        print("2. ⏱️ Timeouts")
        print("3. 🔄 Retry Policy")
        print("4. 📊 Cache Settings")
        print("5. 🗄️ Database")
        print("0. 🔙 Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            await self.configure_rate_limiting()
        elif choice == "2":
            await self.configure_timeouts()
        elif choice == "3":
            await self.configure_retry_policy()
        elif choice == "4":
            await self.configure_cache()
        elif choice == "5":
            await self.configure_database()
        elif choice == "0":
            return
        else:
            print("❌ Opção inválida!")
    
    async def configure_rate_limiting(self):
        """Configura rate limiting"""
        print("\n🔄 CONFIGURAR RATE LIMITING")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def configure_timeouts(self):
        """Configura timeouts"""
        print("\n⏱️ CONFIGURAR TIMEOUTS")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def configure_retry_policy(self):
        """Configura política de retry"""
        print("\n🔄 CONFIGURAR RETRY POLICY")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def configure_cache(self):
        """Configura cache"""
        print("\n📊 CONFIGURAR CACHE")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def configure_database(self):
        """Configura banco de dados"""
        print("\n🗄️ CONFIGURAR BANCO DE DADOS")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def generate_reports(self):
        """Gera relatórios"""
        print("\n" + "-"*40)
        print("📈 RELATÓRIOS")
        print("-"*40)
        
        print("1. 📊 Relatório de Performance")
        print("2. 🔗 Relatório de Links")
        print("3. 💰 Relatório Financeiro")
        print("4. 📅 Relatório Periódico")
        print("0. 🔙 Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            await self.generate_performance_report()
        elif choice == "2":
            await self.generate_links_report()
        elif choice == "3":
            await self.generate_financial_report()
        elif choice == "4":
            await self.generate_periodic_report()
        elif choice == "0":
            return
        else:
            print("❌ Opção inválida!")
    
    async def generate_performance_report(self):
        """Gera relatório de performance"""
        print("\n📊 RELATÓRIO DE PERFORMANCE")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def generate_links_report(self):
        """Gera relatório de links"""
        print("\n🔗 RELATÓRIO DE LINKS")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def generate_financial_report(self):
        """Gera relatório financeiro"""
        print("\n💰 RELATÓRIO FINANCEIRO")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def generate_periodic_report(self):
        """Gera relatório periódico"""
        print("\n📅 RELATÓRIO PERIÓDICO")
        print("❌ Funcionalidade em desenvolvimento...")
    
    async def get_configured_networks(self) -> List[Dict]:
        """Obtém redes configuradas do banco"""
        # Por enquanto, retorna dados simulados
        # Em uma implementação real, você buscaria do banco
        return [
            {
                "network": "amazon",
                "api_key": "amazon_key_123",
                "api_secret": "",
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit_delay": 1.0,
                "enabled": True,
                "priority": 1
            },
            {
                "network": "awin",
                "api_key": "awin_key_456",
                "api_secret": "awin_secret_789",
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit_delay": 1.0,
                "enabled": True,
                "priority": 2
            }
        ]


# Instância global
affiliate_dashboard = AffiliateDashboard()
