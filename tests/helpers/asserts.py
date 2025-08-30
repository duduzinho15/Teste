"""
Funções de assert personalizadas para testes do Garimpeiro Geek
"""

def assert_aliexpress_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido do AliExpress.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    # Verificar se é um shortlink do AliExpress
    return "aliexpress.com" in url and ("/item/" in url or "/product/" in url)


def assert_mercadolivre_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido do Mercado Livre.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    # Verificar se é um shortlink do Mercado Livre
    return "mercadolivre.com.br" in url and "/p/" in url


def assert_amazon_asin(url: str) -> bool:
    """
    Verifica se uma URL contém um ASIN válido da Amazon.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se contiver ASIN válido
    """
    import re
    # ASIN é um código de 10 caracteres alfanuméricos
    asin_pattern = r'/[A-Z0-9]{10}'
    return bool(re.search(asin_pattern, url))


def assert_shopee_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido da Shopee.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    return "shopee.com.br" in url and ("/product/" in url or "/item/" in url)


def assert_magalu_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido da Magazine Luiza.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    return "magazineluiza.com.br" in url and "/p/" in url


def assert_awin_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido da Awin.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    return "awin.com" in url or "awin1.com" in url


def assert_rakuten_shortlink(url: str) -> bool:
    """
    Verifica se uma URL é um shortlink válido da Rakuten.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for um shortlink válido
    """
    return "rakuten.com" in url or "rakuten.com.br" in url


def assert_valid_price(price: str) -> bool:
    """
    Verifica se um preço é válido.
    
    Args:
        price: Preço a ser verificado
        
    Returns:
        True se for um preço válido
    """
    import re
    # Padrão para preços em reais
    price_pattern = r'R\$\s*\d+[.,]\d{2}'
    return bool(re.search(price_pattern, price))


def assert_valid_discount(discount: str) -> bool:
    """
    Verifica se um desconto é válido.
    
    Args:
        discount: Desconto a ser verificado
        
    Returns:
        True se for um desconto válido
    """
    import re
    # Padrão para descontos em porcentagem
    discount_pattern = r'\d+%\s*OFF'
    return bool(re.search(discount_pattern, discount))
