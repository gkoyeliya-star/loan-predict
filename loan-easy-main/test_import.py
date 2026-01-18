# Test if app can be imported
import sys
from pathlib import Path

parent_dir = str(Path(__file__).parent)
sys.path.insert(0, parent_dir)

try:
    print("Testing imports...")
    from app_auth import app
    print("✓ app_auth imported successfully")
    print(f"✓ App name: {app.name}")
    print(f"✓ Routes: {[rule.rule for rule in app.url_map.iter_rules()][:5]}")
    print("\n✓ All imports successful!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
