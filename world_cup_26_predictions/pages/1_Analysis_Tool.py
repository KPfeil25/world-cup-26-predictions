import streamlit as st


from player_analytics.player_analytics_tab import run_analytics_tab

def main():
    """
    Main entry point for the World Cup Player Analytics app.
    Sets up a tabbed interface with a Home tab, Player Analytics tab, and an About tab.
    """

    st.set_page_config(page_title="World Cup Player Analytics", layout="wide")
    st.title("World Cup 2026 Player Analytics")

    # Create tabs for navigation
    tabs = st.tabs(["Player Analytics", "Team Analytics"])

    with tabs[0]:
        # Displays the playeranalytics page
        run_analytics_tab()

    with tabs[1]:
        st.header("Team Analytics")
    

if __name__ == "__main__":
    main()
