import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(page_title="Fashion Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

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
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df

# Main title
st.markdown('<h1 class="main-header">🎨 Fashion Product Analytics Dashboard</h1>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display column names for debugging
    # st.sidebar.write("Detected columns:", df.columns.tolist()[:5])
    
    # Sidebar filters
    # st.sidebar.header("🔍 Filter Options")
    
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
        
        if 'brand' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Product count by brand
                brand_counts = filtered_df['brand'].value_counts().reset_index()
                brand_counts.columns = ['Brand', 'Count']
                
                fig_brand = px.bar(brand_counts.head(15), 
                                  x='Brand', y='Count',
                                  title='Top 15 Brands by Product Count',
                                  color='Count',
                                  color_continuous_scale='Viridis')
                fig_brand.update_layout(xaxis_tickangle=-45, height=500)
                st.plotly_chart(fig_brand, use_container_width=True)
            
            with col2:
                # Brand market share pie chart
                fig_pie = px.pie(brand_counts.head(10), 
                                values='Count', 
                                names='Brand',
                                title='Market Share - Top 10 Brands',
                                hole=0.4)
                fig_pie.update_layout(height=500)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Brand vs Product Type heatmap
            if 'Product-Type' in df.columns:
                st.subheader("Brand × Product Type Analysis")
                brand_product_matrix = pd.crosstab(filtered_df['brand'], filtered_df['Product-Type'])
                
                # Get top 15 brands for cleaner visualization
                top_brands = brand_counts.head(15)['Brand'].tolist()
                brand_product_matrix_filtered = brand_product_matrix.loc[top_brands]
                
                fig_heatmap = px.imshow(brand_product_matrix_filtered,
                                       labels=dict(x="Product Type", y="Brand", color="Count"),
                                       title="Product Distribution Heatmap (Top 15 Brands)",
                                       aspect="auto",
                                       color_continuous_scale='Blues')
                fig_heatmap.update_layout(height=600)
                st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("'brand' column not found in the dataset")
    
    # TAB 2: Market Trends
    with tab2:
        st.subheader("Market Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Color trends
            if 'Primary-Color' in df.columns:
                color_trends = filtered_df['Primary-Color'].value_counts().head(10).reset_index()
                color_trends.columns = ['Color', 'Count']
                
                fig_color = px.bar(color_trends, 
                                  x='Color', y='Count',
                                  title='Top 10 Primary Colors in Market',
                                  color='Count',
                                  color_continuous_scale='Rainbow')
                fig_color.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig_color, use_container_width=True)
            else:
                st.info("Primary-Color column not available")
        
        with col2:
            # Occasion trends
            if 'Occasion-Fit' in df.columns:
                # Handle multiple occasions separated by commas
                occasion_data = filtered_df['Occasion-Fit'].dropna().str.split(',', expand=True).stack().str.strip()
                occasion_counts = occasion_data.value_counts().head(10).reset_index()
                occasion_counts.columns = ['Occasion', 'Count']
                
                fig_occasion = px.bar(occasion_counts,
                                     x='Occasion', y='Count',
                                     title='Top 10 Occasions',
                                     color='Count',
                                     color_continuous_scale='Sunset')
                fig_occasion.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig_occasion, use_container_width=True)
            else:
                st.info("Occasion-Fit column not available")
        
        # Pattern and Design trends
        col3, col4 = st.columns(2)
        
        with col3:
            if 'Pattern-Type' in df.columns:
                pattern_trends = filtered_df['Pattern-Type'].value_counts().head(8).reset_index()
                pattern_trends.columns = ['Pattern', 'Count']
                
                fig_pattern = px.pie(pattern_trends,
                                    values='Count',
                                    names='Pattern',
                                    title='Pattern Type Distribution',
                                    hole=0.3)
                fig_pattern.update_layout(height=400)
                st.plotly_chart(fig_pattern, use_container_width=True)
            else:
                st.info("Pattern-Type column not available")
        
        with col4:
            if 'Design-Complexity' in df.columns:
                design_trends = filtered_df['Design-Complexity'].value_counts().head(8).reset_index()
                design_trends.columns = ['Design', 'Count']
                
                fig_design = px.pie(design_trends,
                                   values='Count',
                                   names='Design',
                                   title='Design Complexity Distribution',
                                   hole=0.3)
                fig_design.update_layout(height=400)
                st.plotly_chart(fig_design, use_container_width=True)
            else:
                st.info("Design-Complexity column not available")
        
        # Material trends
        if 'Primary-Material' in df.columns:
            st.subheader("Material Trends")
            material_trends = filtered_df['Primary-Material'].value_counts().head(12).reset_index()
            material_trends.columns = ['Material', 'Count']
            
            fig_material = px.treemap(material_trends,
                                     path=['Material'],
                                     values='Count',
                                     title='Primary Material Distribution (Treemap)',
                                     color='Count',
                                     color_continuous_scale='Greens')
            fig_material.update_layout(height=500)
            st.plotly_chart(fig_material, use_container_width=True)
        
        # Color Palette Analysis
        if 'Color-Palette-Type' in df.columns:
            st.subheader("Color Palette Trends")
            palette_trends = filtered_df['Color-Palette-Type'].value_counts().head(8).reset_index()
            palette_trends.columns = ['Palette Type', 'Count']
            
            fig_palette = px.bar(palette_trends,
                                x='Palette Type', y='Count',
                                title='Color Palette Type Distribution',
                                color='Count',
                                color_continuous_scale='Rainbow')
            fig_palette.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_palette, use_container_width=True)
    
    # TAB 3: Demographics
    with tab3:
        st.subheader("Target Demographics Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender distribution
            if 'Gender-Target' in df.columns:
                gender_counts = filtered_df['Gender-Target'].value_counts().reset_index()
                gender_counts.columns = ['Gender', 'Count']
                
                fig_gender = px.bar(gender_counts,
                                   x='Gender', y='Count',
                                   title='Gender-wise Product Distribution',
                                   color='Gender',
                                   color_discrete_sequence=px.colors.qualitative.Set2)
                fig_gender.update_layout(height=400)
                st.plotly_chart(fig_gender, use_container_width=True)
            else:
                st.info("Gender-Target column not available")
        
        with col2:
            # Age group distribution
            if 'Age-Target' in df.columns:
                age_counts = filtered_df['Age-Target'].value_counts().reset_index()
                age_counts.columns = ['Age Group', 'Count']
                
                fig_age = px.bar(age_counts,
                                x='Age Group', y='Count',
                                title='Age Target Distribution',
                                color='Count',
                                color_continuous_scale='Teal')
                fig_age.update_layout(height=400)
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("Age-Target column not available")
        
        # Gender × Brand analysis
        if 'Gender-Target' in df.columns and 'brand' in df.columns:
            st.subheader("Gender Distribution Across Top Brands")
            top_brands = filtered_df['brand'].value_counts().head(10).index
            gender_brand = filtered_df[filtered_df['brand'].isin(top_brands)]
            gender_brand_counts = gender_brand.groupby(['brand', 'Gender-Target']).size().reset_index(name='Count')
            
            fig_gender_brand = px.bar(gender_brand_counts,
                                     x='brand', y='Count',
                                     color='Gender-Target',
                                     title='Gender Distribution by Top 10 Brands',
                                     barmode='group')
            fig_gender_brand.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig_gender_brand, use_container_width=True)
        
        # Occasion by Gender
        if 'Occasion-Fit' in df.columns and 'Gender-Target' in df.columns:
            st.subheader("Occasion Preferences by Gender")
            
            # Process occasion data
            occasion_gender = filtered_df[['Occasion-Fit', 'Gender-Target']].dropna()
            occasion_list = []
            for idx, row in occasion_gender.iterrows():
                occasions = row['Occasion-Fit'].split(',')
                for occ in occasions:
                    occasion_list.append({'Occasion': occ.strip(), 'Gender': row['Gender-Target']})
            
            if occasion_list:
                occ_gender_df = pd.DataFrame(occasion_list)
                occ_gender_counts = occ_gender_df.groupby(['Occasion', 'Gender']).size().reset_index(name='Count')
                
                # Get top 10 occasions
                top_occasions = occ_gender_df['Occasion'].value_counts().head(10).index
                occ_gender_counts = occ_gender_counts[occ_gender_counts['Occasion'].isin(top_occasions)]
                
                fig_occ_gender = px.bar(occ_gender_counts,
                                       x='Occasion', y='Count',
                                       color='Gender',
                                       title='Top 10 Occasions by Gender',
                                       barmode='stack')
                fig_occ_gender.update_layout(xaxis_tickangle=-45, height=500)
                st.plotly_chart(fig_occ_gender, use_container_width=True)
    
    # TAB 4: Product Insights
    with tab4:
        st.subheader("Detailed Product Characteristics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Layering position
            if 'Layering-Position' in df.columns:
                layering_counts = filtered_df['Layering-Position'].value_counts().reset_index()
                layering_counts.columns = ['Position', 'Count']
                
                fig_layer = px.pie(layering_counts,
                                  values='Count',
                                  names='Position',
                                  title='Layering Position Distribution',
                                  hole=0.4)
                fig_layer.update_layout(height=400)
                st.plotly_chart(fig_layer, use_container_width=True)
            else:
                st.info("Layering-Position column not available")
        
        with col2:
            # Texture quality
            if 'Texture-Quality' in df.columns:
                texture_counts = filtered_df['Texture-Quality'].value_counts().reset_index()
                texture_counts.columns = ['Texture', 'Count']
                
                fig_texture = px.bar(texture_counts,
                                    x='Texture', y='Count',
                                    title='Texture Quality Distribution',
                                    color='Count',
                                    color_continuous_scale='Purp')
                fig_texture.update_layout(height=400)
                st.plotly_chart(fig_texture, use_container_width=True)
            else:
                st.info("Texture-Quality column not available")
        
        # Silhouette analysis
        if 'Silhouette' in df.columns:
            st.subheader("Silhouette Trends")
            silhouette_counts = filtered_df['Silhouette'].value_counts().head(10).reset_index()
            silhouette_counts.columns = ['Silhouette', 'Count']
            
            fig_silhouette = px.bar(silhouette_counts,
                                   y='Silhouette', x='Count',
                                   title='Top 10 Silhouettes',
                                   orientation='h',
                                   color='Count',
                                   color_continuous_scale='Teal')
            fig_silhouette.update_layout(height=400)
            st.plotly_chart(fig_silhouette, use_container_width=True)
        
        # Embellishment analysis
        if 'Embellishments-Present' in df.columns:
            st.subheader("Embellishment Presence")
            embellishment_counts = filtered_df['Embellishments-Present'].value_counts().reset_index()
            embellishment_counts.columns = ['Embellishment', 'Count']
            
            fig_embellish = px.pie(embellishment_counts,
                                  values='Count',
                                  names='Embellishment',
                                  title='Products with/without Embellishments',
                                  hole=0.4,
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_embellish.update_layout(height=400)
            st.plotly_chart(fig_embellish, use_container_width=True)
        
        # Subcategory analysis
        if 'Sub-Category' in df.columns:
            st.subheader("Sub-Category Distribution")
            subcat_counts = filtered_df['Sub-Category'].value_counts().head(15).reset_index()
            subcat_counts.columns = ['Sub-Category', 'Count']
            
            fig_subcat = px.bar(subcat_counts,
                               x='Sub-Category', y='Count',
                               title='Top 15 Sub-Categories',
                               color='Count',
                               color_continuous_scale='Reds')
            fig_subcat.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig_subcat, use_container_width=True)
        
        # Technical Features
        # if 'Technical-Features' in df.columns:
        #     st.subheader("Technical Features Analysis")
        #     tech_counts = filtered_df['Technical-Features'].value_counts().head(10).reset_index()
        #     tech_counts.columns = ['Feature', 'Count']
            
        #     fig_tech = px.bar(tech_counts,
        #                      y='Feature', x='Count',
        #                      title='Top 10 Technical Features',
        #                      orientation='h',
        #                      color='Count',
        #                      color_continuous_scale='Viridis')
        #     fig_tech.update_layout(height=400)
        #     st.plotly_chart(fig_tech, use_container_width=True)
    
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
        
        # Show column info
        st.subheader("Dataset Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Non-Null Count': [df[col].notna().sum() for col in df.columns],
            'Null Count': [df[col].isna().sum() for col in df.columns],
            'Data Type': [df[col].dtype for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)

else:
    st.info("👆 Please upload a CSV file to get started!")
    st.markdown("""
    ### Expected CSV Format:
    Your CSV should include columns like:
    - **brand** (lowercase)
    - **Product-Type**
    - **Sub-Category**
    - **Primary-Color**, **Secondary-Colors**
    - **Pattern-Type**
    - **Gender-Target**, **Age-Target**
    - **Occasion-Fit**
    - **Primary-Material**
    - **Design-Complexity**
    - **Layering-Position**
    - **Silhouette**
    - **Texture-Quality**
    - **Embellishments-Present**
    - **Technical-Features**
    - And other product attributes...
    """)
