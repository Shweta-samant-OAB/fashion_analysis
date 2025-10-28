import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(page_title="Fashion Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Define consistent color scheme and font settings
BRAND_COLOR = '#2E86AB'  # Primary blue
COLORS_3_SHADES = ['#2E86AB', '#5FA8D3', '#A4C8E1']  # Blue shades for gender
COLOR_PALETTE = ['#2E86AB', '#5FA8D3', '#A4C8E1', '#C8E1F2', '#1A5F7A']

# Consistent font and layout settings
FONT_SIZE = 12
TITLE_FONT_SIZE = 16
LABEL_FONT_SIZE = 11

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

# Main title
st.markdown('<h1 class="main-header">🎨 Fashion Product Analytics Dashboard</h1>', unsafe_allow_html=True)

# File uploader - only show if no file uploaded yet
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if not st.session_state.data_loaded:
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.data_loaded = True
        st.rerun()
else:
    uploaded_file = st.session_state.uploaded_file

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    
    # Brand filter
    if 'brand' in df.columns:
        brands = ['All'] + sorted(df['brand'].dropna().unique().tolist())
        selected_brand = st.sidebar.multiselect("Select Brand(s)", brands, default=['All'])
    
    # Product Type filter
    if 'Product-Type' in df.columns:
        product_types = ['All'] + sorted(df['Product-Type'].dropna().unique().tolist())
        selected_product = st.sidebar.multiselect("Select Product Type(s)", product_types, default=['All'])
    
    # Sub-Category filter
    if 'Sub-Category' in df.columns:
        subcategories = ['All'] + sorted(df['Sub-Category'].dropna().unique().tolist())
        selected_subcategory = st.sidebar.multiselect("Select Sub-Category", subcategories, default=['All'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'brand' in df.columns and 'All' not in selected_brand:
        filtered_df = filtered_df[filtered_df['brand'].isin(selected_brand)]
    
    if 'Product-Type' in df.columns and 'All' not in selected_product:
        filtered_df = filtered_df[filtered_df['Product-Type'].isin(selected_product)]
    
    if 'Sub-Category' in df.columns and 'All' not in selected_subcategory:
        filtered_df = filtered_df[filtered_df['Sub-Category'].isin(selected_subcategory)]
    
    # Key Metrics Row
    st.header("📊 Key Metrics Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(filtered_df))
    with col2:
        if 'brand' in df.columns:
            st.metric("Brands", filtered_df['brand'].nunique())
    with col3:
        if 'Product-Type' in df.columns:
            st.metric("Product Types", filtered_df['Product-Type'].nunique())
    with col4:
        if 'Gender-Target' in df.columns:
            st.metric("Gender Categories", filtered_df['Gender-Target'].nunique())
    
    # Main Dashboard Layout
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Brand Analysis", "🎯 Market Trends", "👥 Demographics", "🎨 Product Insights"])
    
    # TAB 1: Brand Analysis
    with tab1:
        st.subheader("Brand-wise Product Distribution")
        
        if 'brand' in df.columns and 'Product-Type' in df.columns:
            col1, col2 = st.columns([1, 1.8])
            
            with col1:
                brand_counts = filtered_df['brand'].value_counts().head(10).reset_index()
                brand_counts.columns = ['Brand', 'Count']

                # Unique color palette with 10 distinct colors (no similar shades)
                PIE_COLOR_PALETTE = ['#FF6B6B', '#45B7D1', '#FFA07A', '#F7DC6F', 
                                      '#BB8FCE', '#E85D75', '#52B788', '#F4A261', '#9B59B6']

                fig_donut = px.pie(
                    brand_counts,
                    values='Count',
                    names='Brand',
                    title='Market Share',
                    hole=0.45,
                    color_discrete_sequence=PIE_COLOR_PALETTE
                )
                fig_donut.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=11,
                    pull=[0.03]*len(brand_counts)
                )
                fig_donut.update_layout(
                    height=550,
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE,
                    title_x=0.5,
                    title_y=0.95,
                    margin=dict(t=80, b=20, l=20, r=20),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=0.98,
                        xanchor="left",
                        x=1.02,
                        bgcolor="rgba(255,255,255,0.5)"
                    )
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            
            with col2:
                # 📊 Stacked bar chart with brand-product distribution
                brand_product = filtered_df.groupby(['brand', 'Product-Type']).size().reset_index(name='Count')
                top_brands = filtered_df['brand'].value_counts().head(15).index
                brand_product = brand_product[brand_product['brand'].isin(top_brands)]

                fig_brand = px.bar(
                    brand_product,
                    x='brand',
                    y='Count',
                    color='Product-Type',
                    title='Brands by Product Type Distribution',
                    text='Count',
                    color_discrete_sequence=COLOR_PALETTE
                )

                fig_brand.update_traces(
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    insidetextanchor='middle'
                )

                # Calculate y-axis scale dynamically
                max_brand_count = brand_product.groupby('brand')['Count'].sum().max()
                y_max = max_brand_count * 1.15

                fig_brand.update_layout(
                    xaxis_tickangle=-45,
                    height=900,  # Increased height for better spacing between scales
                    xaxis_title='Brand',
                    yaxis_title='Product Count',
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.01,
                        bgcolor="rgba(255,255,255,0.5)"
                    ),
                    yaxis=dict(
                        range=[0, y_max],
                        dtick=10,  # Scale difference of 5
                        gridcolor='rgba(200,200,200,0.3)',
                        gridwidth=1
                    ),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE,
                    title_x=0.4,
                    margin=dict(t=80, b=60, l=40, r=40),
                    paper_bgcolor="white"
                )
                st.plotly_chart(fig_brand, use_container_width=True)
    
    # TAB 2: Market Trends
    with tab2:
        st.subheader("Market Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Color trends - annotations inside center
            if 'Primary-Color' in df.columns:
                color_trends = filtered_df['Primary-Color'].value_counts().head(10).reset_index()
                color_trends.columns = ['Color', 'Count']
                
                max_color_count = color_trends['Count'].max()
                y_max = max_color_count * 1.15
                
                fig_color = px.bar(color_trends, 
                                  x='Color', y='Count',
                                  title='Top 10 Primary Colors in Market',
                                  text='Count',
                                  color_discrete_sequence=[BRAND_COLOR])
                fig_color.update_traces(
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    insidetextanchor='middle'
                )
                fig_color.update_layout(
                    xaxis_tickangle=-45, 
                    height=400,
                    showlegend=False,
                    yaxis=dict(range=[0, y_max]),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_color, use_container_width=True)
        
        with col2:
            # Occasion trends - annotations inside center
            if 'Occasion-Fit' in df.columns:
                occasion_data = filtered_df['Occasion-Fit'].dropna().str.split(',', expand=True).stack().str.strip()
                occasion_counts = occasion_data.value_counts().head(10).reset_index()
                occasion_counts.columns = ['Occasion', 'Count']
                
                max_occasion_count = occasion_counts['Count'].max()
                y_max = max_occasion_count * 1.15
                
                fig_occasion = px.bar(occasion_counts,
                                     x='Occasion', y='Count',
                                     title='Top 10 Occasions',
                                     text='Count',
                                     color_discrete_sequence=[BRAND_COLOR])
                fig_occasion.update_traces(
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    insidetextanchor='middle'
                )
                fig_occasion.update_layout(
                    xaxis_tickangle=-45, 
                    height=400,
                    showlegend=False,
                    yaxis=dict(range=[0, y_max]),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_occasion, use_container_width=True)
        
        # Pattern and Design - reduced width
        col3, col4 = st.columns(2)
        
        with col3:
            if 'Pattern-Type' in df.columns:
                pattern_trends = filtered_df['Pattern-Type'].value_counts().head(8).reset_index()
                pattern_trends.columns = ['Pattern', 'Count']
                
                max_pattern_count = pattern_trends['Count'].max()
                y_max = max_pattern_count * 1.15
                
                fig_pattern = go.Figure(go.Bar(
                    x=pattern_trends['Pattern'],
                    y=pattern_trends['Count'],
                    text=pattern_trends['Count'],
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    marker_color=BRAND_COLOR,
                    width=0.5
                ))
                fig_pattern.update_layout(
                    title='Pattern Type Distribution',
                    height=400,
                    showlegend=False,
                    xaxis_tickangle=-45,
                    xaxis_title='Pattern',
                    yaxis_title='Count',
                    yaxis=dict(range=[0, y_max]),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_pattern, use_container_width=True)
        
        with col4:
            if 'Design-Complexity' in df.columns:
                design_trends = filtered_df['Design-Complexity'].value_counts().head(8).reset_index()
                design_trends.columns = ['Design', 'Count']
                
                max_design_count = design_trends['Count'].max()
                y_max = max_design_count * 1.15
                
                fig_design = go.Figure(go.Bar(
                    x=design_trends['Design'],
                    y=design_trends['Count'],
                    text=design_trends['Count'],
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    marker_color=BRAND_COLOR,
                    width=0.5
                ))
                fig_design.update_layout(
                    title='Design Complexity Distribution',
                    height=400,
                    showlegend=False,
                    xaxis_tickangle=-45,
                    xaxis_title='Design',
                    yaxis_title='Count',
                    yaxis=dict(range=[0, y_max]),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_design, use_container_width=True)
        
        # Color Palette - horizontal bar chart
        if 'Color-Palette-Type' in df.columns:
            st.subheader("Color Palette Distribution")
            palette_trends = filtered_df['Color-Palette-Type'].value_counts().reset_index()
            palette_trends.columns = ['Palette Type', 'Count']
            palette_trends = palette_trends.sort_values('Count', ascending=True)
            
            fig_palette = go.Figure(go.Bar(
                y=palette_trends['Palette Type'],
                x=palette_trends['Count'],
                orientation='h',
                text=palette_trends['Count'],
                textposition='inside',
                textfont_size=LABEL_FONT_SIZE,
                marker_color=BRAND_COLOR,
                width=0.6
            ))
            
            max_palette_count = palette_trends['Count'].max()
            x_max = max_palette_count * 1.15
            
            fig_palette.update_layout(
                title='Color Palette Type Distribution',
                height=400,
                showlegend=False,
                xaxis_title='Count',
                yaxis_title='Palette Type',
                bargap=0.3,
                xaxis=dict(range=[0, x_max]),
                font=dict(size=FONT_SIZE),
                title_font_size=TITLE_FONT_SIZE
            )
            st.plotly_chart(fig_palette, use_container_width=True)
    
    # TAB 3: Demographics
    with tab3:
        st.subheader("Target Demographics Analysis")
        
        col1, col2 = st.columns([0.9, 1.1])
        
        with col1:
            # Gender distribution - reduced width
            if 'Gender-Target' in df.columns:
                gender_counts = filtered_df['Gender-Target'].value_counts().reset_index()
                gender_counts.columns = ['Gender', 'Count']
                
                max_gender_count = gender_counts['Count'].max()
                y_max = max_gender_count * 1.15
                
                fig_gender = go.Figure(go.Bar(
                    x=gender_counts['Gender'],
                    y=gender_counts['Count'],
                    text=gender_counts['Count'],
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    marker_color=BRAND_COLOR,
                    width=0.4
                ))
                fig_gender.update_layout(
                    title='Gender-wise Product Distribution',
                    height=400,
                    showlegend=False,
                    xaxis_title='Gender',
                    yaxis_title='Product Count',
                    yaxis=dict(range=[0, y_max]),
                    margin=dict(l=40, r=40, t=60, b=40),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            # Age group distribution - same width as gender
            if 'Age-Target' in df.columns:
                age_counts = filtered_df['Age-Target'].value_counts().reset_index()
                age_counts.columns = ['Age Group', 'Count']
                
                max_age_count = age_counts['Count'].max()
                y_max = max_age_count * 1.15
                
                fig_age = go.Figure(go.Bar(
                    x=age_counts['Age Group'],
                    y=age_counts['Count'],
                    text=age_counts['Count'],
                    textposition='inside',
                    textfont_size=LABEL_FONT_SIZE,
                    marker_color=BRAND_COLOR,
                    width=0.4  # Same width as gender chart
                ))
                fig_age.update_layout(
                    title='Age Target Distribution',
                    height=400,
                    showlegend=False,
                    xaxis_title='Age Group',
                    yaxis_title='Product Count',
                    yaxis=dict(range=[0, y_max]),
                    margin=dict(l=40, r=40, t=60, b=40),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE
                )
                st.plotly_chart(fig_age, use_container_width=True)
        
        # Gender × Brand analysis with 3 shades
        if 'Gender-Target' in df.columns and 'brand' in df.columns:
            st.subheader("Gender Distribution Across Top Brands")
            top_brands = filtered_df['brand'].value_counts().head(10).index
            gender_brand = filtered_df[filtered_df['brand'].isin(top_brands)]
            gender_brand_counts = gender_brand.groupby(['brand', 'Gender-Target']).size().reset_index(name='Count')
            
            # Create color mapping for genders
            unique_genders = gender_brand_counts['Gender-Target'].unique()
            color_map = {gender: COLORS_3_SHADES[i % 3] for i, gender in enumerate(unique_genders)}
            
            fig_gender_brand = px.bar(gender_brand_counts,
                                     x='brand', y='Count',
                                     color='Gender-Target',
                                     title='Gender Distribution by Top 10 Brands',
                                     barmode='group',
                                     text='Count',
                                     color_discrete_map=color_map)
            fig_gender_brand.update_traces(
                textposition='inside',
                textfont_size=LABEL_FONT_SIZE,
                insidetextanchor='middle'
            )
            
            max_gender_brand = gender_brand_counts.groupby('brand')['Count'].max().max()
            y_max = max_gender_brand * 1.15
            
            fig_gender_brand.update_layout(
                xaxis_tickangle=-45, 
                height=500,
                xaxis_title='Brand',
                yaxis_title='Product Count',
                yaxis=dict(range=[0, y_max]),
                font=dict(size=FONT_SIZE),
                title_font_size=TITLE_FONT_SIZE
            )
            st.plotly_chart(fig_gender_brand, use_container_width=True)
        
        # Occasion by Gender with 3 shades and annotations - adjusted scale
        if 'Occasion-Fit' in df.columns and 'Gender-Target' in df.columns:
            st.subheader("Occasion Preferences by Gender")
            
            occasion_gender = filtered_df[['Occasion-Fit', 'Gender-Target']].dropna()
            occasion_list = []
            for idx, row in occasion_gender.iterrows():
                occasions = row['Occasion-Fit'].split(',')
                for occ in occasions:
                    occasion_list.append({'Occasion': occ.strip(), 'Gender': row['Gender-Target']})
            
            if occasion_list:
                occ_gender_df = pd.DataFrame(occasion_list)
                occ_gender_counts = occ_gender_df.groupby(['Occasion', 'Gender']).size().reset_index(name='Count')
                
                top_occasions = occ_gender_df['Occasion'].value_counts().head(10).index
                occ_gender_counts = occ_gender_counts[occ_gender_counts['Occasion'].isin(top_occasions)]
                
                # Use same 3 shades
                unique_genders = occ_gender_counts['Gender'].unique()
                color_map = {gender: COLORS_3_SHADES[i % 3] for i, gender in enumerate(unique_genders)}
                
                # Calculate max value for proper y-axis range
                occasion_totals = occ_gender_counts.groupby('Occasion')['Count'].sum()
                max_value = occasion_totals.max()
                y_max = max_value * 1.15
                
                fig_occ_gender = px.bar(occ_gender_counts,
                                       x='Occasion', y='Count',
                                       color='Gender',
                                       title='Top 10 Occasions by Gender',
                                       barmode='stack',
                                       text='Count',
                                       color_discrete_map=color_map)
                fig_occ_gender.update_traces(
                    textposition='inside',
                    textfont_size=11,
                    insidetextanchor='middle'
                )
                fig_occ_gender.update_layout(
                    xaxis_tickangle=-45, 
                    height=1000,  # Increased height for better spacing between scales
                    xaxis_title='Occasion',
                    yaxis_title='Product Count',
                    yaxis=dict(
                        range=[0, y_max],
                        dtick=20,  # Scale difference of 10
                        gridcolor='rgba(200,200,200,0.3)',
                        gridwidth=1
                    ),
                    font=dict(size=12),
                    title_font_size=16
                )
                st.plotly_chart(fig_occ_gender, use_container_width=True)
    
    # TAB 4: Product Insights
    with tab4:
        # Sub-Category at top
        if 'Sub-Category' in df.columns:
            st.subheader("Sub-Category Distribution")
            subcat_counts = filtered_df['Sub-Category'].value_counts().head(15).reset_index()
            subcat_counts.columns = ['Sub-Category', 'Count']
            
            max_subcat_count = subcat_counts['Count'].max()
            y_max = max_subcat_count * 1.15
            
            fig_subcat = px.bar(subcat_counts,
                               x='Sub-Category', y='Count',
                               title='Top 15 Sub-Categories',
                               text='Count',
                               color_discrete_sequence=[BRAND_COLOR])
            fig_subcat.update_traces(
                textposition='inside',
                textfont_size=LABEL_FONT_SIZE,
                insidetextanchor='middle'
            )
            fig_subcat.update_layout(
                xaxis_tickangle=-45, 
                height=500,
                showlegend=False,
                xaxis_title='Sub-Category',
                yaxis_title='Product Count',
                yaxis=dict(range=[0, y_max]),
                font=dict(size=FONT_SIZE),
                title_font_size=TITLE_FONT_SIZE
            )
            st.plotly_chart(fig_subcat, use_container_width=True)
        
        st.subheader("Detailed Product Characteristics")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Layering position - horizontal bar chart (sorted descending)
            if 'Layering-Position' in df.columns:
                layering_counts = (
                    filtered_df['Layering-Position']
                    .value_counts()
                    .reset_index()
                )
                layering_counts.columns = ['Position', 'Count']
                layering_counts = layering_counts.sort_values('Count', ascending=False)

                total = layering_counts['Count'].sum()

                fig_layer = go.Figure(go.Bar(
                    y=layering_counts['Position'],
                    x=layering_counts['Count'],
                    orientation='h',
                    text=[f"{count} ({count/total*100:.1f}%)" for count in layering_counts['Count']],
                    textposition='inside',
                    textfont=dict(size=LABEL_FONT_SIZE),
                    marker_color=COLOR_PALETTE[0]
                ))

                fig_layer.update_layout(
                    title='Layering Position Distribution',
                    height=550,
                    xaxis_title='Count',
                    yaxis_title='Layering Position',
                    yaxis=dict(autorange='reversed'),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE,
                    showlegend=False,
                    bargap=0.25,
                    margin=dict(l=80, r=40, t=60, b=40)
                )

                st.plotly_chart(fig_layer, use_container_width=True)


        with col2:
            # Texture quality - horizontal bar chart (sorted descending)
            if 'Texture-Quality' in df.columns:
                texture_counts = filtered_df['Texture-Quality'].value_counts().reset_index()
                texture_counts.columns = ['Texture', 'Count']
                texture_counts = texture_counts.sort_values('Count', ascending=False)

                total_texture = texture_counts['Count'].sum()

                fig_texture = go.Figure(go.Bar(
                    y=texture_counts['Texture'],
                    x=texture_counts['Count'],
                    orientation='h',
                    text=[f"{count} ({count/total_texture*100:.1f}%)" for count in texture_counts['Count']],
                    textposition='inside',
                    textfont=dict(size=LABEL_FONT_SIZE),
                    marker_color=COLOR_PALETTE[1]
                ))

                fig_texture.update_layout(
                    title='Texture Quality Distribution',
                    height=550,
                    xaxis_title='Count',
                    yaxis_title='Texture Quality',
                    yaxis=dict(autorange='reversed'),
                    font=dict(size=FONT_SIZE),
                    title_font_size=TITLE_FONT_SIZE,
                    showlegend=False,
                    bargap=0.25,
                    margin=dict(l=80, r=40, t=60, b=40)
                )

                st.plotly_chart(fig_texture, use_container_width=True)

        
        # Silhouette - horizontal bar, descending
        if 'Silhouette' in df.columns:
            st.subheader("Silhouette Trends")
            silhouette_counts = filtered_df['Silhouette'].value_counts().head(12).reset_index()
            silhouette_counts.columns = ['Silhouette', 'Count']
            silhouette_counts = silhouette_counts.sort_values('Count', ascending=True)
            
            max_silhouette_count = silhouette_counts['Count'].max()
            x_max = max_silhouette_count * 1.15
            
            fig_silhouette = go.Figure(go.Bar(
                y=silhouette_counts['Silhouette'],
                x=silhouette_counts['Count'],
                orientation='h',
                text=silhouette_counts['Count'],
                textposition='inside',
                textfont_size=LABEL_FONT_SIZE,
                marker_color=BRAND_COLOR
            ))
            fig_silhouette.update_layout(
                title='Top 12 Silhouettes',
                height=500,
                showlegend=False,
                xaxis_title='Count',
                yaxis_title='Silhouette Type',
                xaxis=dict(range=[0, x_max]),
                font=dict(size=FONT_SIZE),
                title_font_size=TITLE_FONT_SIZE
            )
            st.plotly_chart(fig_silhouette, use_container_width=True)
    
    # Download filtered data
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Export Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_fashion_data.csv',
        mime='text/csv',
    )
    
    # Show raw data
    if st.sidebar.checkbox("Show Raw Data"):
        st.subheader("Raw Data View")
        st.dataframe(filtered_df, use_container_width=True)
    
    # Option to upload new file
    st.sidebar.markdown("---")
    if st.sidebar.button("Upload New File"):
        st.session_state.data_loaded = False
        st.session_state.uploaded_file = None
        st.rerun()

else:
    st.info("👆 Please upload a CSV file to get started!")
