#!/usr/bin/env python3
"""
Test script to verify FIX.Z API functionality
"""

import sys
import os
sys.path.insert(0, '.')

from api.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

def test_fixz_api():
    print("=== Testing FIX.Z API Endpoints ===\n")
    
    # Test versions endpoint
    print("1. Testing /api/versions")
    response = client.get('/api/versions')
    if response.status_code == 200:
        versions = response.json()
        print(f"✓ Available versions: {versions}")
        assert 'FIX.Z' in versions
    else:
        print(f"✗ Error: {response.status_code}")
        return False
    
    # Test search with FIX.Z
    print("\n2. Testing search with FIX.Z")
    response = client.get('/api/search?version=FIX.Z&query=Order&limit=5')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data['results'])} results for 'Order' in FIX.Z")
        for i, result in enumerate(data['results'][:3], 1):
            print(f"   {i}. {result['type']}: {result['name']} ({result['id']})")
    else:
        print(f"✗ Search failed: {response.status_code}")
        return False
    
    # Test FIX.Z direct message access
    print("\n3. Testing FIX.Z direct message access")
    response = client.get('/api/FIX.Z/msg/D')
    if response.status_code == 200:
        msg = response.json()
        print(f"✓ FIX.Z message 'D': {msg['name']}")
        print(f"   Description: {msg['description'][:80]}...")
    else:
        print(f"✗ Direct access failed: {response.status_code}")
        return False
    
    # Test FIX.Z field access
    print("\n4. Testing FIX.Z field access")
    response = client.get('/api/fields/11?version=FIX.Z')
    if response.status_code == 200:
        field = response.json()
        print(f"✓ FIX.Z field 11: {field['name']} ({field['type']})")
        print(f"   Description: {field['description']}")
    else:
        print(f"✗ Field access failed: {response.status_code}")
        return False
    
    # Test FIX.Z components
    print("\n5. Testing FIX.Z components")
    response = client.get('/api/components?version=FIX.Z&limit=3')
    if response.status_code == 200:
        components = response.json()
        print(f"✓ FIX.Z has {len(components)} components")
        for i, comp in enumerate(components[:3], 1):
            print(f"   {i}. {comp['name']} ({comp['component_type']})")
    else:
        print(f"✗ Components access failed: {response.status_code}")
        return False
    
    # Test FIX.Z codesets
    print("\n6. Testing FIX.Z codesets")
    response = client.get('/api/codesets/54?version=FIX.Z')
    if response.status_code == 200:
        codeset = response.json()
        print(f"✓ FIX.Z field 54 (Side) has {len(codeset)} enum values")
        for i, enum_val in enumerate(codeset[:3], 1):
            print(f"   {i}. {enum_val['value']}: {enum_val['symbolic_name']}")
    else:
        print(f"✗ Codesets access failed: {response.status_code}")
        return False
    
    print("\n✅ All FIX.Z API tests passed!")
    return True

if __name__ == "__main__":
    success = test_fixz_api()
    if not success:
        sys.exit(1)
