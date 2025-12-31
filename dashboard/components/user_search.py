"""
User Search page for the LOGIC dashboard.
Provides comprehensive user activity search and analysis across all log sources.
"""

import streamlit as st
from services.data_service import search_users_in_logs, extract_all_users


def render_user_search():
    """Render the user search page"""
    st.header("User Search & Analysis")
    
    # User search section
    st.subheader("Search for Specific Users")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_user = st.text_input("Enter username to search:", placeholder="e.g., yanna, administrator, john.doe")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("Search", type="primary")
    
    if search_user or search_button:
        if search_user:
            with st.spinner("Searching for user activities..."):
                results = search_users_in_logs(search_user)
                
                if results:
                    st.success(f"Found {len(results)} events for user: {search_user}")
                    
                    # Group results by log source
                    log_groups = {}
                    for result in results:
                        if result['log_source'] not in log_groups:
                            log_groups[result['log_source']] = []
                        log_groups[result['log_source']].append(result)
                    
                    # Display results by log source
                    for log_source, log_results in log_groups.items():
                        with st.expander(f"{log_source} - {len(log_results)} events"):
                            for result in log_results[:50]:  # Limit to first 50 for performance
                                st.markdown(f"""
                                **Event ID:** {result['event_id']} | **Time:** {result['timestamp']}  
                                **User Field:** {result['user_field']} = `{result['user_value']}`
                                """)
                                
                                # Show important event details for security analysis
                                if result['event']:
                                    event = result['event']
                                    
                                    # Create a security-focused display
                                    security_details = {}
                                    
                                    # Core identification fields
                                    security_details['Event ID'] = event.get('event_id', 'Unknown')
                                    security_details['Timestamp'] = event.get('timestamp', 'Unknown')
                                    security_details['Computer'] = event.get('computer', 'Unknown')
                                    security_details['Record ID'] = event.get('record_id', 'Unknown')
                                    
                                    # Extract event_data if it exists
                                    event_data = event.get('event_data', {})
                                    
                                    # User and authentication fields (most important for security)
                                    user_fields = ['SubjectUserName', 'SubjectUserSid', 'SubjectDomainName', 'SubjectLogonId',
                                                 'TargetUserName', 'TargetUserSid', 'TargetDomainName', 'TargetLogonId']
                                    
                                    for field in user_fields:
                                        if field in event_data and event_data[field] not in [None, '-', '']:
                                            security_details[field] = event_data[field]
                                    
                                    # Process and system activity fields  
                                    process_fields = ['ProcessId', 'ProcessName', 'NewProcessId', 'NewProcessName', 
                                                    'ParentProcessName', 'CommandLine', 'CallerProcessId', 'CallerProcessName']
                                    
                                    for field in process_fields:
                                        if field in event_data and event_data[field] not in [None, '-', '']:
                                            security_details[field] = event_data[field]
                                    
                                    # Authentication and network fields
                                    auth_fields = ['LogonType', 'LogonProcessName', 'AuthenticationPackageName', 
                                                 'WorkstationName', 'IpAddress', 'IpPort', 'LogonGuid']
                                    
                                    for field in auth_fields:
                                        if field in event_data and event_data[field] not in [None, '-', '']:
                                            security_details[field] = event_data[field]
                                    
                                    # Privilege and access fields
                                    privilege_fields = ['PrivilegeList', 'AccessGranted', 'TokenElevationType', 
                                                      'ImpersonationLevel', 'MandatoryLabel']
                                    
                                    for field in privilege_fields:
                                        if field in event_data and event_data[field] not in [None, '-', '']:
                                            security_details[field] = event_data[field]
                                    
                                    # Security event specific fields
                                    if event.get('event_id') == '4624':  # Successful logon
                                        st.success("Successful Logon Event")
                                    elif event.get('event_id') == '4625':  # Failed logon
                                        st.error("Failed Logon Event")
                                    elif event.get('event_id') == '4634':  # Logoff
                                        st.info("Logoff Event")
                                    elif event.get('event_id') == '4720':  # User account created
                                        st.warning("User Account Created")
                                    elif event.get('event_id') == '4688':  # Process creation
                                        st.info("Process Creation")
                                    elif event.get('event_id') == '4648':  # Logon with explicit credentials
                                        st.warning("Explicit Credential Logon")
                                    
                                    # Display in organized columns
                                    if len(security_details) > 8:
                                        col1, col2 = st.columns(2)
                                        items = list(security_details.items())
                                        mid = len(items) // 2
                                        
                                        with col1:
                                            for key, value in items[:mid]:
                                                st.write(f"**{key}:** `{value}`")
                                        
                                        with col2:
                                            for key, value in items[mid:]:
                                                st.write(f"**{key}:** `{value}`")
                                    else:
                                        for key, value in security_details.items():
                                            st.write(f"**{key}:** `{value}`")
                                
                                st.markdown("---")
                            
                            if len(log_results) > 50:
                                st.info(f"Showing first 50 events out of {len(log_results)} total")
                else:
                    st.warning(f"No events found for user: {search_user}")
        else:
            st.info("Enter a username to search")
    
    # Show all users section
    st.subheader("All Users Found in Logs")
    
    if st.button("Load All Users"):
        with st.spinner("Extracting users from logs..."):
            all_users = extract_all_users()
            
            if all_users:
                st.success(f"Found {len(all_users)} unique users")
                
                # Display users in columns
                cols = st.columns(4)
                for i, user in enumerate(all_users):
                    with cols[i % 4]:
                        if st.button(user, key=f"user_{i}"):
                            # Auto-fill the search box with clicked user
                            st.session_state.search_user = user
                            st.rerun()
            else:
                st.warning("No users found in logs")