print("Python environment test")
print("=====================")

import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test if we can import the deal_scoring module
try:
    from src.app.queue.deal_scoring import compute_deal_score, PriceStats, DealPolicy
    print("\n✅ Successfully imported deal_scoring module")
    
    # Test a simple score calculation
    offer = {
        'id': 'test_offer',
        'name': 'Test Product',
        'category': 'electronics',
        'price': 2000.00,
        'list_price': 3000.00,
        'seller': 'Test Seller',
        'platform': 'test'
    }
    
    price_stats = PriceStats(
        mean_90d=Decimal('2800.00'),
        p25_90d=Decimal('2600.00'),
        low_40d=Decimal('2100.00'),
        low_90d=Decimal('2050.00'),
        low_180d=Decimal('2000.00')
    )
    
    policy = DealPolicy(trusted_sellers={"Magazine Luiza", "Kabum"})
    score = compute_deal_score(offer, price_stats, policy)
    
    print(f"\nTest score calculation:")
    print(f"- Score: {score.score:.2f}")
    print(f"- Level: {score.level}")
    print("Reasons:")
    for reason in score.reasons:
        print(f"  - {reason}")
        
    print("\n✅ Deal scoring test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error importing deal_scoring module: {e}")
    print("\nMake sure you have installed all dependencies and the module is in the Python path.")
    print("Try running: pip install -e ." if os.path.exists("setup.py") else "Install dependencies and try again.")
