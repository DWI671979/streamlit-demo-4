import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_KEY = "a3f417b116fa4104b3c547e8ee9d32e1"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.news-card {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.metric-box {
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📰 News Filters")

country_options = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp"
}

selected_country = st.sidebar.selectbox(
    "Select Location",
    list(country_options.keys())
)

selected_category = st.sidebar.selectbox(
    "Select Topic",
    [
        "general",
        "business",
        "entertainment",
        "health",
        "science",
        "sports",
        "technology"
    ]
)

keyword = st.sidebar.text_input(
    "Search Keyword",
    placeholder="AI, Tesla, Cricket..."
)

article_count = st.sidebar.slider(
    "Number of Articles",
    5,
    100,
    20,
    5
)

# --------------------------------------------------
# FETCH NEWS
# --------------------------------------------------

@st.cache_data(ttl=300)
def fetch_news(country, category, page_size):

    params = {
        "apiKey": API_KEY,
        "country": country,
        "category": category,
        "pageSize": page_size
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None

# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------

st.title("📰 Advanced News Dashboard")
st.write(
    "Browse trending news articles by location, topic and keywords."
)

with st.spinner("Fetching latest news..."):

    news_data = fetch_news(
        country_options[selected_country],
        selected_category,
        article_count
    )

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if news_data and news_data.get("status") == "ok":

    articles = news_data.get("articles", [])

    # Keyword filtering
    if keyword:

        filtered_articles = []

        for article in articles:

            title = article.get("title", "")
            desc = article.get("description", "")

            combined = f"{title} {desc}".lower()

            if keyword.lower() in combined:
                filtered_articles.append(article)

        articles = filtered_articles

    # Metrics
    col1, col2, col3 = st.columns(3)

    sources = set()

    for article in articles:
        sources.add(
            article.get("source", {}).get("name")
        )

    col1.metric("Articles Found", len(articles))
    col2.metric("Sources", len(sources))
    col3.metric("Country", selected_country)

    st.divider()

    # Create dataframe
    table_data = []

    for article in articles:

        table_data.append({
            "Title": article.get("title"),
            "Source": article.get("source", {}).get("name"),
            "Published": article.get("publishedAt"),
            "URL": article.get("url")
        })

    df = pd.DataFrame(table_data)

    # Download CSV
    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="news_articles.csv",
        mime="text/csv"
    )

    # Summary Table
    with st.expander("📊 Article Summary Table"):

        st.dataframe(
            df,
            use_container_width=True
        )

    st.divider()

    # News Cards
    for article in articles:

        title = article.get("title", "No Title")
        source = article.get("source", {}).get("name", "Unknown")
        description = article.get("description", "")
        image = article.get("urlToImage")
        url = article.get("url")
        published = article.get("publishedAt")

        col1, col2 = st.columns([1, 3])

        with col1:

            if image:
                st.image(
                    image,
                    use_container_width=True
                )

        with col2:

            st.subheader(title)

            st.caption(
                f"📰 {source} | 📅 {published}"
            )

            if description:
                st.write(description)

            if url:
                st.markdown(
                    f"[Read Full Article]({url})"
                )

        st.divider()

else:
    st.error(
        "Failed to retrieve news articles. Check API key or connection."
    )