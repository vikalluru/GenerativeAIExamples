#!/usr/bin/env python3
"""
Debug script to investigate vector retrieval issues with VannaManager
"""
import os
import sys
from src.predictive_maintenance_agent.vanna_util import NIMVanna, CustomEmbeddingFunction

def debug_vector_retrieval():
    """Debug what training examples are retrieved for a specific query"""
    
    print("🔍 VECTOR RETRIEVAL DEBUG INVESTIGATION")
    print("=" * 60)
    
    # Create Vanna instance
    vn = NIMVanna(
        VectorConfig={
            "client": "persistent",
            "path": "database",
            "embedding_function": CustomEmbeddingFunction(
                api_key=os.getenv("NVIDIA_API_KEY"), 
                model="nvidia/nv-embedqa-e5-v5")
        },
        LLMConfig={
            "api_key": os.getenv("NVIDIA_API_KEY"),
            "model": "meta/llama-3.1-405b-instruct"
        }
    )
    
    # Connect to database
    vn.connect_to_sqlite("PredM_db/nasa_turbo.db")
    vn.allow_llm_to_see_data = True
    vn.disable_auto_training()
    
    # Test query that's causing issues
    test_query = "Retrieve time in cycles, all sensor measurements and RUL value for engine unit 24 from FD001 test and RUL tables"
    
    print(f"📝 TEST QUERY: {test_query}")
    print()
    
    # Get similar training examples
    print("🔍 RETRIEVING SIMILAR TRAINING EXAMPLES...")
    try:
        # Use Vanna's internal method to get similar examples
        similar_examples = vn.get_similar_question_sql(test_query, n_results=10)
        
        print(f"📊 FOUND {len(similar_examples)} SIMILAR EXAMPLES:")
        print("-" * 50)
        
        for i, example in enumerate(similar_examples, 1):
            question = example.get('question', 'N/A')
            sql = example.get('sql', 'N/A')
            
            print(f"\n{i}. QUESTION: {question}")
            print(f"   SQL: {sql}")
            
            # Check for contamination indicators
            if 'JOIN rul_data' in sql:
                print("   ❌ CONTAMINATED: Contains JOIN rul_data")
            elif 'MAX(time_in_cycles)' in sql:
                print("   ✅ FIXED: Contains calculated RUL")
            else:
                print("   ❓ OTHER: Different pattern")
        
        print("\n" + "=" * 60)
        print("🎯 SIMILARITY SEARCH ANALYSIS:")
        
        contaminated_count = sum(1 for ex in similar_examples if 'JOIN rul_data' in ex.get('sql', ''))
        fixed_count = sum(1 for ex in similar_examples if 'MAX(time_in_cycles)' in ex.get('sql', ''))
        
        print(f"   Contaminated examples retrieved: {contaminated_count}")
        print(f"   Fixed examples retrieved: {fixed_count}")
        
        if contaminated_count > 0:
            print("   🚨 PROBLEM: Contaminated examples being retrieved!")
        elif fixed_count == 0:
            print("   🚨 PROBLEM: No fixed examples being retrieved!")
        else:
            print("   ✅ GOOD: Fixed examples are being retrieved")
        
    except Exception as e:
        print(f"❌ ERROR retrieving similar examples: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 GENERATING SQL FOR TEST QUERY...")
    
    try:
        generated_sql = vn.generate_sql(test_query)
        print(f"📝 GENERATED SQL: {generated_sql}")
        
        if 'JOIN rul_data' in generated_sql:
            print("❌ CONTAMINATED SQL GENERATED!")
        elif 'MAX(time_in_cycles)' in generated_sql:
            print("✅ FIXED SQL GENERATED!")
        else:
            print("❓ UNEXPECTED SQL PATTERN")
            
    except Exception as e:
        print(f"❌ ERROR generating SQL: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 INVESTIGATION COMPLETE")

if __name__ == "__main__":
    debug_vector_retrieval() 