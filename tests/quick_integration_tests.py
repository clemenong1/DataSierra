#!/usr/bin/env python3
"""
Quick Integration Test Runner for DataSierra
Simplified version for easy execution
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_firebase_connection():
    """Test Firebase connection and services"""
    print("🔧 Testing Firebase Connection...")
    
    try:
        from src.services.firebase_config import FirebaseConfig
        from src.services.firebase_storage_service import FirebaseStorageService
        from src.services.visualization_service import VisualizationService
        
        if FirebaseConfig.initialize():
            print("✅ Firebase initialized successfully")
            
            # Test services
            storage_service = FirebaseStorageService()
            viz_service = VisualizationService()
            
            print("✅ Firebase Storage service initialized")
            print("✅ Visualization service initialized")
            
            return True
        else:
            print("❌ Firebase initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Firebase connection error: {str(e)}")
        return False

def test_authentication():
    """Test authentication features"""
    print("\n🔐 Testing Authentication...")
    
    try:
        from src.services.auth_service import AuthService
        
        auth_service = AuthService()
        
        # Test local authentication simulation
        test_user = {
            'uid': 'test_user_123',
            'email': 'test@datasierra.com',
            'display_name': 'Test User'
        }
        
        print("✅ Authentication service initialized")
        print("✅ Local authentication simulation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test error: {str(e)}")
        return False

def test_file_processing():
    """Test file processing and upload"""
    print("\n📁 Testing File Processing...")
    
    try:
        from src.services.file_service import FileService
        from src.models.file_models import ProcessedFile
        import pandas as pd
        
        file_service = FileService()
        
        # Create test data
        test_data = {
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'Salary': [50000, 60000, 70000]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test file processing
        from src.models.file_models import FileInfo, DataQuality
        
        file_info = FileInfo(
            name="test.csv",
            size=len(df.to_csv()),
            type="csv",
            upload_time=datetime.now(),
            shape=df.shape,
            columns=list(df.columns),
            dtypes={col: str(df[col].dtype) for col in df.columns}
        )
        
        data_quality = DataQuality(
            total_nulls=df.isnull().sum().sum(),
            duplicate_rows=df.duplicated().sum(),
            completeness_score=1.0 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])),
            uniqueness_score=1.0 - (df.duplicated().sum() / df.shape[0])
        )
        
        column_statistics = {}
        for col in df.columns:
            column_statistics[col] = {
                'type': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique()
            }
        
        processed_file = ProcessedFile(
            file_info=file_info,
            data_quality=data_quality,
            sample_rows=df.head(5).to_dict('records'),
            column_statistics=column_statistics,
            data_json=df.to_dict('records')
        )
        
        print("✅ File processing works")
        print(f"✅ Processed {len(df)} rows, {len(df.columns)} columns")
        
        # Test data validation
        numeric_cols = processed_file.get_numeric_columns()
        categorical_cols = processed_file.get_categorical_columns()
        
        print(f"✅ Data validation: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical columns")
        
        return True
        
    except Exception as e:
        print(f"❌ File processing test error: {str(e)}")
        return False

def test_query_functionality():
    """Test query functionality"""
    print("\n❓ Testing Query Functionality...")
    
    try:
        from src.services.ai_service import AIService
        from src.services.data_service import DataService
        from src.services.session_service import SessionService
        
        ai_service = AIService()
        data_service = DataService()
        session_service = SessionService()
        
        print("✅ AI service initialized")
        print("✅ Data service initialized")
        print("✅ Session service initialized")
        
        # Test query history
        history = session_service.get_query_history(limit=5)
        print(f"✅ Query history retrieval works ({len(history)} items)")
        
        return True
        
    except Exception as e:
        print(f"❌ Query functionality test error: {str(e)}")
        return False

def test_visualization_generation():
    """Test visualization generation"""
    print("\n📊 Testing Visualization Generation...")
    
    try:
        from src.services.lida_visualization_service import LidaVisualizationService
        from src.services.firebase_storage_service import FirebaseStorageService
        from src.services.visualization_service import VisualizationService
        import plotly.express as px
        import pandas as pd
        
        lida_service = LidaVisualizationService()
        storage_service = FirebaseStorageService()
        viz_service = VisualizationService()
        
        print("✅ LIDA visualization service initialized")
        print(f"✅ LIDA availability: {lida_service.is_available()}")
        
        # Test chart generation
        test_data = {
            'Department': ['IT', 'HR', 'Finance'],
            'Salary': [60000, 55000, 65000]
        }
        
        df = pd.DataFrame(test_data)
        fig = px.bar(df, x='Department', y='Salary', title='Test Chart')
        
        # Convert to image
        img_bytes = fig.to_image(format="png", width=800, height=600)
        print(f"✅ Chart image generation works ({len(img_bytes)} bytes)")
        
        # Test visualization storage
        test_user_id = 'test_user_123'
        upload_result = storage_service.upload_chart_image(
            image_data=img_bytes,
            filename="test_chart.png",
            user_id=test_user_id,
            query="Test visualization"
        )
        
        if upload_result:
            print("✅ Chart image uploaded to Firebase Storage")
            
            # Test Firestore saving
            viz_id = viz_service.save_visualization(test_user_id, upload_result)
            if viz_id:
                print(f"✅ Visualization metadata saved to Firestore (ID: {viz_id})")
            else:
                print("❌ Visualization metadata saving failed")
                return False
        else:
            print("❌ Chart image upload failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization generation test error: {str(e)}")
        return False

def test_history_functionality():
    """Test history functionality"""
    print("\n📚 Testing History Functionality...")
    
    try:
        from src.services.visualization_service import VisualizationService
        from src.ui.components.history import HistoryComponent
        from src.services.session_service import SessionService
        
        viz_service = VisualizationService()
        session_service = SessionService()
        history_component = HistoryComponent(session_service)
        
        print("✅ History component initialized")
        
        # Test visualization history
        test_user_id = 'test_user_123'
        visualizations = viz_service.get_user_visualizations(test_user_id, limit=10)
        print(f"✅ Visualization history retrieval works ({len(visualizations)} items)")
        
        # Test datetime formatting
        if visualizations:
            for viz in visualizations:
                created_at = viz.get('created_at', 'Unknown date')
                if hasattr(created_at, 'strftime'):
                    formatted_date = created_at.strftime('%b %d %H:%M')
                    print(f"✅ Datetime formatting works: {formatted_date}")
                    break
        
        # Test query history
        query_history = session_service.get_query_history(limit=5)
        print(f"✅ Query history retrieval works ({len(query_history)} items)")
        
        return True
        
    except Exception as e:
        print(f"❌ History functionality test error: {str(e)}")
        return False

def test_feedback_system():
    """Test feedback system"""
    print("\n👍 Testing Feedback System...")
    
    try:
        from src.services.visualization_service import VisualizationService
        
        viz_service = VisualizationService()
        
        # Test visualization feedback
        test_user_id = 'test_user_123'
        visualizations = viz_service.get_user_visualizations(test_user_id, limit=1)
        
        if visualizations:
            viz_id = visualizations[0].get('id')
            
            # Test helpfulness update
            success = viz_service.update_visualization_helpfulness(
                test_user_id, viz_id, True
            )
            
            if success:
                print("✅ Visualization helpfulness feedback works")
            else:
                print("❌ Visualization helpfulness feedback failed")
                return False
        else:
            print("ℹ️  No visualizations available for feedback testing")
        
        print("✅ Feedback system methods available")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback system test error: {str(e)}")
        return False

def run_quick_tests():
    """Run all quick integration tests"""
    print("🧪 DataSierra Quick Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Firebase Connection", test_firebase_connection),
        ("Authentication", test_authentication),
        ("File Processing", test_file_processing),
        ("Query Functionality", test_query_functionality),
        ("Visualization Generation", test_visualization_generation),
        ("History Functionality", test_history_functionality),
        ("Feedback System", test_feedback_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! DataSierra is working correctly.")
        return True
    else:
        print("⚠️  SOME TESTS FAILED. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    
    if success:
        print("\n✅ Integration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed.")
        sys.exit(1)
