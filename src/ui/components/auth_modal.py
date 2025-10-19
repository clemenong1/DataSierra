"""
Authentication modal component
"""

import streamlit as st
from typing import Optional, Callable
from ...services.auth_service import AuthService


class AuthModalComponent:
    """Component for handling authentication modal UI"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def render_auth_button(self) -> bool:
        """
        Render the authentication button in the header
        
        Returns:
            True if authentication modal should be shown
        """
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col3:
            # Check if Firebase is properly initialized
            if not self.auth_service.is_initialized():
                # Show a more helpful error message when possible
                init_err = getattr(self.auth_service, 'initialization_error', None)
                if init_err:
                    st.error(f"🔧 Auth not configured: {init_err}")
                else:
                    st.error("🔧 Auth not configured")
                st.markdown("If you're running locally, set the GOOGLE_APPLICATION_CREDENTIALS env var or place a service account JSON in the project root. See README for details.")
                return False
            
            if self.auth_service.is_authenticated():
                # Show user info and logout button
                user_email = self.auth_service.get_user_email()
                st.markdown(f"**Welcome, {user_email}**")
                
                if st.button("🚪 Logout", key="logout_btn"):
                    self.auth_service.sign_out()
                    st.rerun()
            else:
                # Show login button
                if st.button("🔐 Login", key="login_btn", type="primary"):
                    return True
        
        return False
    
    def render_auth_modal(self, show_modal: bool = False) -> bool:
        """
        Render the authentication modal
        
        Args:
            show_modal: Whether to show the modal
            
        Returns:
            True if authentication was successful
        """
        if not show_modal:
            return False
        
        # Don't show modal if user is already authenticated
        if self.auth_service.is_authenticated():
            # Clear any existing auth mode from session state
            if 'auth_mode' in st.session_state:
                del st.session_state.auth_mode
            return False
        
        # Create modal using container and columns for older Streamlit versions
        with st.container():
            st.markdown("---")
            return self._render_auth_form()
    
    def _render_auth_form(self) -> bool:
        """
        Render the authentication form inside the modal
        
        Returns:
            True if authentication was successful
        """
        # Initialize form mode in session state
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'login'
        
        # Header
        st.markdown("### Log in/Create an Account")
        st.markdown("Sign in to upload and analyze your data files")
        
        # Mode toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", key="mode_login", 
                        type="primary" if st.session_state.auth_mode == 'login' else "secondary"):
                st.session_state.auth_mode = 'login'
                st.rerun()
        
        with col2:
            if st.button("📝 Create Account", key="mode_signup",
                        type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
                st.session_state.auth_mode = 'signup'
                st.rerun()
        
        st.markdown("---")
        
        # Form
        with st.form("auth_form"):
            # Email input
            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email address",
                help="We'll use this to identify your account"
            )
            
            # Password input
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                help="Must be at least 6 characters long"
            )
            
            # Confirm password for signup
            if st.session_state.auth_mode == 'signup':
                confirm_password = st.text_input(
                    "🔒 Confirm Password",
                    type="password",
                    placeholder="Confirm your password"
                )
            else:
                confirm_password = password
            
            # Submit button
            submit_text = "Sign In" if st.session_state.auth_mode == 'login' else "Create Account"
            submit_button = st.form_submit_button(f"🚀 {submit_text}", type="primary")
            
            # Handle form submission
            if submit_button:
                return self._handle_auth_submission(email, password, confirm_password)
        
        # Additional options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Need help?**")
            st.markdown("• Check your email and password")
            st.markdown("• Ensure password is 6+ characters")
        
        with col2:
            st.markdown("**Security**")
            st.markdown("• Your data is encrypted")
            st.markdown("• We never store passwords")
        
        return False
    
    def _handle_auth_submission(self, email: str, password: str, confirm_password: str) -> bool:
        """
        Handle authentication form submission
        
        Args:
            email: User email
            password: User password
            confirm_password: Password confirmation
            
        Returns:
            True if authentication was successful
        """
        # Validate inputs
        if not email or not password:
            st.error("Please fill in all required fields")
            return False
        
        if not self.auth_service.validate_email(email):
            st.error("Please enter a valid email address")
            return False
        
        if st.session_state.auth_mode == 'signup':
            if password != confirm_password:
                st.error("Passwords do not match")
                return False
            
            is_valid, error_msg = self.auth_service.validate_password(password)
            if not is_valid:
                st.error(error_msg)
                return False
        
        # Attempt authentication
        if st.session_state.auth_mode == 'login':
            success, message = self.auth_service.sign_in(email, password)
        else:
            success, message = self.auth_service.sign_up(email, password)
        
        if success:
            st.success(message)
            # Clear the modal by removing auth_mode from session state
            if 'auth_mode' in st.session_state:
                del st.session_state.auth_mode
            st.rerun()
            return True
        else:
            st.error(message)
            return False
    
    def render_protected_action_modal(self, action_name: str, action_description: str) -> bool:
        """
        Render a modal for protected actions (like file upload)
        
        Args:
            action_name: Name of the protected action
            action_description: Description of what the action does
            
        Returns:
            True if user should proceed with the action
        """
        with st.container():
            st.markdown("---")
            st.markdown(f"### 🔒 {action_name} Requires Authentication")
            st.markdown(f"**{action_description}**")
            st.markdown("Please sign in to continue with this action.")
            
            # Quick auth form
            with st.form("quick_auth_form"):
                email = st.text_input("📧 Email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_submit = st.form_submit_button("🔑 Sign In", type="primary")
                with col2:
                    signup_submit = st.form_submit_button("📝 Create Account")
                
                if login_submit and email and password:
                    success, message = self.auth_service.sign_in(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                        return True
                    else:
                        st.error(message)
                
                if signup_submit and email and password:
                    success, message = self.auth_service.sign_up(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                        return True
                    else:
                        st.error(message)
            
            # Cancel button
            if st.button("❌ Cancel", key="cancel_protected_action"):
                return False
        
        return False
