"""
Test script for the FIX Dictionary API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import FIXDictionaryParser
from models import FIXVersion, SearchType
import json

def test_parser():
    """Test the FIX dictionary parser"""
    print("Testing FIX Dictionary Parser...")
    
    # Initialize parser
    resources_path = "resources/dict"
    if not os.path.exists(resources_path):
        print(f"Resources path not found: {resources_path}")
        return False
    
    parser = FIXDictionaryParser(resources_path)
    
    # Test basic loading
    print(f"Available versions: {list(parser.data.keys())}")
    
    for version in FIXVersion:
        print(f"\n=== Testing {version.value} ===")
        
        # Test messages
        messages = parser.get_messages(version)
        print(f"Messages loaded: {len(messages)}")
        if messages:
            print(f"Sample message: {messages[0].name} ({messages[0].msg_type})")
        
        # Test fields
        fields = parser.get_fields(version)
        print(f"Fields loaded: {len(fields)}")
        if fields:
            print(f"Sample field: {fields[0].name} (tag {fields[0].tag})")
        
        # Test components
        components = parser.get_components(version)
        print(f"Components loaded: {len(components)}")
        if components:
            print(f"Sample component: {components[0].name}")
        
        # Test enums
        enums = parser.get_enums(version)
        print(f"Enums loaded: {len(enums)}")
        if enums:
            print(f"Sample enum: Tag {enums[0].tag}, Value {enums[0].value}")
        
        # Test search
        search_results = parser.search("Order", SearchType.ALL, version)
        print(f"Search results for 'Order': {len(search_results)}")
        
        # Test specific lookups
        new_order_msg = parser.get_message_by_type("D", version)
        if new_order_msg:
            print(f"Found NewOrderSingle: {new_order_msg.name}")
        
        clordid_field = parser.get_field_by_tag(11, version)
        if clordid_field:
            print(f"Found ClOrdID field: {clordid_field.name}")
        
        side_enums = parser.get_enums_for_field(54, version)
        print(f"Side field enums: {len(side_enums)}")
    
    print("\nParser test completed successfully!")
    return True

def test_search_examples():
    """Test various search examples"""
    print("\n=== Testing Search Examples ===")
    
    parser = FIXDictionaryParser("resources/dict")
    version = FIXVersion.FIX_5_0_SP2
    
    # Test cases
    test_cases = [
        ("Order", SearchType.ALL, False, False),
        ("^Order", SearchType.ALL, False, True),
        ("Limit", SearchType.FIELD, False, False),
        ("Session", SearchType.MESSAGE, False, False),
        ("[0-9]{3}", SearchType.ALL, False, True),
    ]
    
    for query, search_type, match_abbr, is_regex in test_cases:
        results = parser.search(query, search_type, version, match_abbr, is_regex)
        print(f"Query: '{query}' ({search_type.value}, regex={is_regex}) -> {len(results)} results")
        
        # Show first few results
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result.name} ({result.type.value})")

if __name__ == "__main__":
    try:
        if test_parser():
            test_search_examples()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
