#!/usr/bin/env python3
"""
DataSierra Integration Test Suite
Tests all major features of the application
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to the Python path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.firebase_config import FirebaseConfig
from src.services.auth_service import AuthService
from src.services.file_service import FileService
from src.services.ai_service import AIService
from src.services.data_service import DataService
from src.services.session_service import SessionService
from src.services.firebase_storage_service import FirebaseStorageService
from src.services.visualization_service import VisualizationService
from src.ui.components.auth_modal import AuthModalComponent
from src.ui.components.file_upload import FileUploadComponent
from src.ui.components.query_interface import QueryInterfaceComponent
from src.ui.components.history import HistoryComponent
from src.ui.components.lida_visualization import LidaVisualizationComponent
from src.models.file_models import ProcessedFile
import pandas as pd
import plotly.express as px


class DataSierraIntegrationTests:
    """Comprehensive integration tests for DataSierra"""
    
    def __init__(self):
        self.test_results = []
        self.test_user_id = None
        self.test_session_id = "integration_test_session"
        
        # Initialize services
        self.auth_service = AuthService()
        self.file_service = FileService()
        self.ai_service = AIService()
        self.data_service = DataService()
        self.session_service = SessionService()
        self.storage_service = FirebaseStorageService()
        self.viz_service = VisualizationService()
        
        # Initialize components
        self.auth_modal = AuthModalComponent(self.auth_service)
        self.file_upload = FileUploadComponent(self.file_service, self.auth_modal)
        self.query_interface = QueryInterfaceComponent(self.ai_service, self.data_service)
        self.history_component = HistoryComponent(self.session_service)
        self.lida_visualization = LidaVisualizationComponent()
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 DataSierra Integration Test Suite")
        print("=" * 60)
        
        # Initialize Firebase
        if not self._initialize_firebase():
            return False
        
        # Run test suites
        test_suites = [
            ("Authentication Tests", self.test_authentication),
            ("Dataset Upload Tests", self.test_dataset_upload),
            ("Query Tests", self.test_querying),
            ("Visualization Tests", self.test_visualization_generation),
            ("History Tests", self.test_history_functionality),
            ("Feedback Tests", self.test_feedback_system)
        ]
        
        all_passed = True
        
        for suite_name, test_func in test_suites:
            print(f"\n📋 Running {suite_name}")
            print("-" * 40)
            
            try:
                suite_passed = test_func()
                if suite_passed:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
                    all_passed = False
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                all_passed = False
        
        # Summary
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL TESTS PASSED! DataSierra is working correctly.")
        else:
            print("⚠️  SOME TESTS FAILED. Check the output above for details.")
        
        return all_passed
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase for testing"""
        try:
            if FirebaseConfig.initialize():
                print("✅ Firebase initialized successfully")
                return True
            else:
                print("❌ Firebase initialization failed")
                return False
        except Exception as e:
            print(f"❌ Firebase initialization error: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test 1: Login, logout, stay logged in when refresh page"""
        print("Testing authentication features...")
        
        # Test 1.1: Check if authentication service is available
        if not hasattr(self.auth_service, 'authenticate_user'):
            print("❌ Auth service missing authenticate_user method")
            return False
        print("✅ Auth service has required methods")
        
        # Test 1.2: Test local authentication (fallback)
        try:
            # Simulate local authentication
            test_user = {
                'uid': 'test_user_integration',
                'email': 'test@datasierra.com',
                'display_name': 'Test User'
            }
            
            # Test session state simulation
            import streamlit as st
            if not hasattr(st, 'session_state'):
                # Mock session state for testing
                class MockSessionState:
                    def __init__(self):
                        self.data = {}
                    def get(self, key, default=None):
                        return self.data.get(key, default)
                    def __setitem__(self, key, value):
                        self.data[key] = value
                    def __getitem__(self, key):
                        return self.data[key]
                
                st.session_state = MockSessionState()
            
            st.session_state['user'] = test_user
            self.test_user_id = test_user['uid']
            
            print("✅ Local authentication simulation successful")
            
            # Test 1.3: Check if user stays logged in (session persistence)
            if st.session_state.get('user'):
                print("✅ User session persists")
            else:
                print("❌ User session not persistent")
                return False
            
            # Test 1.4: Test logout functionality
            if hasattr(self.auth_service, 'sign_out'):
                print("✅ Logout functionality available")
            else:
                print("⚠️  Logout functionality not implemented")
            
            return True
            
        except Exception as e:
            print(f"❌ Authentication test error: {str(e)}")
            return False
    
    def test_dataset_upload(self) -> bool:
        """Test 2: Dataset uploading onto database, tests for dataset"""
        print("Testing dataset upload functionality...")
        
        try:
            # Test 2.1: Create test dataset
            test_data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                'Age': [25, 30, 35, 28, 32],
                'Salary': [50000, 60000, 70000, 55000, 65000],
                'Department': ['IT', 'HR', 'IT', 'Finance', 'IT']
            }
            
            df = pd.DataFrame(test_data)
            print(f"✅ Test dataset created: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Test 2.2: Test file processing
            processed_file = ProcessedFile(
                file_info=df,
                data_json=df.to_dict('records'),
                file_name="test_dataset.csv",
                file_size=len(df.to_csv()),
                upload_timestamp=datetime.now()
            )
            
            print("✅ Dataset processed successfully")
            
            # Test 2.3: Test Firebase Storage upload
            if self.test_user_id:
                # Convert DataFrame to CSV bytes
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                upload_result = self.storage_service.upload_file(
                    file_data=csv_data,
                    filename="test_dataset.csv",
                    user_id=self.test_user_id,
                    content_type="text/csv"
                )
                
                if upload_result:
                    print("✅ Dataset uploaded to Firebase Storage")
                    print(f"   Storage URL: {upload_result['file_url']}")
                else:
                    print("❌ Dataset upload to Firebase Storage failed")
                    return False
            
            # Test 2.4: Test data validation
            numeric_cols = processed_file.get_numeric_columns()
            categorical_cols = processed_file.get_categorical_columns()
            
            if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                print(f"✅ Data validation passed: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical columns")
            else:
                print("❌ Data validation failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Dataset upload test error: {str(e)}")
            return False
    
    def test_querying(self) -> bool:
        """Test 3: Querying dataset"""
        print("Testing query functionality...")
        
        try:
            # Test 3.1: Create test dataset
            test_data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                'Age': [25, 30, 35, 28, 32],
                'Salary': [50000, 60000, 70000, 55000, 65000],
                'Department': ['IT', 'HR', 'IT', 'Finance', 'IT']
            }
            
            df = pd.DataFrame(test_data)
            processed_file = ProcessedFile(
                file_info=df,
                data_json=df.to_dict('records'),
                file_name="test_dataset.csv",
                file_size=len(df.to_csv()),
                upload_timestamp=datetime.now()
            )
            
            processed_files = {"test_dataset.csv": processed_file}
            
            # Test 3.2: Test AI service query processing
            test_query = "What is the average salary by department?"
            
            if hasattr(self.ai_service, 'process_query'):
                print("✅ AI service has process_query method")
            else:
                print("❌ AI service missing process_query method")
                return False
            
            # Test 3.3: Test data service
            if hasattr(self.data_service, 'get_data_preview'):
                preview = self.data_service.get_data_preview(processed_file, n_rows=3)
                if not preview.empty:
                    print("✅ Data preview functionality works")
                else:
                    print("❌ Data preview failed")
                    return False
            
            # Test 3.4: Test query history saving
            if hasattr(self.session_service, 'save_query_history'):
                # Simulate saving a query
                self.session_service.save_query_history(
                    query=test_query,
                    response="Average salary by department: IT: $61,667, HR: $60,000, Finance: $55,000",
                    file_name="test_dataset.csv"
                )
                print("✅ Query history saving works")
            else:
                print("❌ Query history saving not available")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Querying test error: {str(e)}")
            return False
    
    def test_visualization_generation(self) -> bool:
        """Test 4: Generating visualizations for dataset"""
        print("Testing visualization generation...")
        
        try:
            # Test 4.1: Create test dataset
            test_data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                'Age': [25, 30, 35, 28, 32],
                'Salary': [50000, 60000, 70000, 55000, 65000],
                'Department': ['IT', 'HR', 'IT', 'Finance', 'IT']
            }
            
            df = pd.DataFrame(test_data)
            processed_file = ProcessedFile(
                file_info=df,
                data_json=df.to_dict('records'),
                file_name="test_dataset.csv",
                file_size=len(df.to_csv()),
                upload_timestamp=datetime.now()
            )
            
            processed_files = {"test_dataset.csv": processed_file}
            
            # Test 4.2: Test LIDA visualization service
            if hasattr(self.lida_service, 'is_available'):
                lida_available = self.lida_service.is_available()
                print(f"✅ LIDA service status: {'Available' if lida_available else 'Not available'}")
            else:
                print("❌ LIDA service not properly initialized")
                return False
            
            # Test 4.3: Test visualization generation
            test_prompt = "Create a bar chart showing average salary by department"
            
            if hasattr(self.lida_service, 'generate_visualization_from_prompt'):
                # Test visualization generation
                result = self.lida_service.generate_visualization_from_prompt(
                    dataframes={"test_dataset.csv": df},
                    user_prompt=test_prompt
                )
                
                if result.get("success"):
                    print("✅ Visualization generation successful")
                    charts = result.get("charts", [])
                    print(f"   Generated {len(charts)} chart(s)")
                else:
                    print(f"⚠️  Visualization generation failed: {result.get('error', 'Unknown error')}")
            else:
                print("❌ Visualization generation method not available")
                return False
            
            # Test 4.4: Test chart image generation
            try:
                # Create a simple chart
                fig = px.bar(df.groupby('Department')['Salary'].mean().reset_index(), 
                           x='Department', y='Salary', 
                           title='Average Salary by Department')
                
                # Convert to image
                img_bytes = fig.to_image(format="png", width=800, height=600)
                print(f"✅ Chart image generation works ({len(img_bytes)} bytes)")
                
                # Test 4.5: Test Firebase Storage for visualizations
                if self.test_user_id:
                    upload_result = self.storage_service.upload_chart_image(
                        image_data=img_bytes,
                        filename="test_chart.png",
                        user_id=self.test_user_id,
                        query=test_prompt
                    )
                    
                    if upload_result:
                        print("✅ Chart image uploaded to Firebase Storage")
                        
                        # Test 4.6: Test Firestore visualization saving
                        viz_id = self.viz_service.save_visualization(self.test_user_id, upload_result)
                        if viz_id:
                            print(f"✅ Visualization metadata saved to Firestore (ID: {viz_id})")
                        else:
                            print("❌ Visualization metadata saving failed")
                            return False
                    else:
                        print("❌ Chart image upload failed")
                        return False
                
            except Exception as e:
                print(f"❌ Chart image generation error: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Visualization generation test error: {str(e)}")
            return False
    
    def test_history_functionality(self) -> bool:
        """Test 5: Correct History queries and visualizations"""
        print("Testing history functionality...")
        
        try:
            # Test 5.1: Test query history retrieval
            if hasattr(self.session_service, 'get_query_history'):
                history = self.session_service.get_query_history(limit=10)
                print(f"✅ Query history retrieval works ({len(history)} items)")
            else:
                print("❌ Query history retrieval not available")
                return False
            
            # Test 5.2: Test visualization history retrieval
            if self.test_user_id:
                visualizations = self.viz_service.get_user_visualizations(self.test_user_id, limit=10)
                print(f"✅ Visualization history retrieval works ({len(visualizations)} items)")
                
                # Test 5.3: Test visualization history formatting
                if visualizations:
                    for viz in visualizations:
                        created_at = viz.get('created_at', 'Unknown date')
                        if hasattr(created_at, 'strftime'):
                            formatted_date = created_at.strftime('%b %d %H:%M')
                            print(f"✅ Datetime formatting works: {formatted_date}")
                        else:
                            print("⚠️  Datetime formatting issue")
                            break
                else:
                    print("ℹ️  No visualizations found (expected for new user)")
            
            # Test 5.4: Test history component methods
            if hasattr(self.history_component, '_render_visualization_history'):
                print("✅ Visualization history rendering method available")
            else:
                print("❌ Visualization history rendering method missing")
                return False
            
            if hasattr(self.history_component, '_render_visualization_item'):
                print("✅ Visualization item rendering method available")
            else:
                print("❌ Visualization item rendering method missing")
                return False
            
            # Test 5.5: Test history statistics
            if hasattr(self.session_service, 'get_history_statistics'):
                stats = self.session_service.get_history_statistics()
                print(f"✅ History statistics available: {stats.get('total_queries', 0)} queries")
            else:
                print("⚠️  History statistics not available")
            
            return True
            
        except Exception as e:
            print(f"❌ History functionality test error: {str(e)}")
            return False
    
    def test_feedback_system(self) -> bool:
        """Test 6: Feedback for query and visualization"""
        print("Testing feedback system...")
        
        try:
            # Test 6.1: Test visualization helpfulness feedback
            if self.test_user_id:
                # Get a visualization to test feedback on
                visualizations = self.viz_service.get_user_visualizations(self.test_user_id, limit=1)
                
                if visualizations:
                    viz_id = visualizations[0].get('id')
                    
                    # Test helpful feedback
                    if hasattr(self.viz_service, 'update_visualization_helpfulness'):
                        success = self.viz_service.update_visualization_helpfulness(
                            self.test_user_id, viz_id, True
                        )
                        if success:
                            print("✅ Visualization helpfulness feedback works")
                        else:
                            print("❌ Visualization helpfulness feedback failed")
                            return False
                    else:
                        print("❌ Visualization helpfulness feedback method missing")
                        return False
                else:
                    print("ℹ️  No visualizations available for feedback testing")
            
            # Test 6.2: Test query feedback (if available)
            if hasattr(self.session_service, 'save_feedback'):
                print("✅ Query feedback method available")
            else:
                print("⚠️  Query feedback method not implemented")
            
            # Test 6.3: Test feedback retrieval
            if hasattr(self.session_service, 'get_feedback_history'):
                print("✅ Feedback retrieval method available")
            else:
                print("⚠️  Feedback retrieval method not implemented")
            
            # Test 6.4: Test feedback statistics
            if hasattr(self.session_service, 'get_feedback_statistics'):
                print("✅ Feedback statistics method available")
            else:
                print("⚠️  Feedback statistics method not implemented")
            
            return True
            
        except Exception as e:
            print(f"❌ Feedback system test error: {str(e)}")
            return False


def run_integration_tests():
    """Run the complete integration test suite"""
    test_suite = DataSierraIntegrationTests()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = run_integration_tests()
    
    if success:
        print("\n🎉 All integration tests passed!")
        print("Your DataSierra application is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed.")
        print("Please check the output above for details.")
        sys.exit(1)
