# Load the libraries
import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
df_viz = pd.read_csv('df_viz_processed.csv')

# Convert 'Order Date' to datetime format
df_viz['Order Date'] = pd.to_datetime(df_viz['Order Date'])

# Page Title, Main title and description
st.set_page_config(page_title="Nichola_Foley", page_icon=":bar_chart:", layout="wide")
st.title("Retail Sales Data for Our Company 💸")
st.write("A breakdown of sales data by Overall Sales, Account Manager and Product.")

# Sidebar Menu
menu_options = ['Home', 'Sales Overview', 'Sales by Account Manager', 'Sales by Product Category']
selected_option = st.sidebar.selectbox('Select a Page', menu_options)

# Function to format numbers with dollar sign and thousand separators
def format_currency(value):
    return "${:,.2f}".format(value)

# Function to get year options including 'All Years'
def get_year_options(df):
    years = sorted(df['Order Date'].dt.year.unique(), reverse=True)
    return ['All Years'] + years

# Define a color map for years 
year_colors = {
    '2017': 'red',
    '2016': 'green',
    '2015': 'purple',
    '2014': 'orange',
    '2013': 'magenta',
}

# Function to get color based on selected year
def get_line_color(year):
    return year_colors.get(str(year), 'blue')

# Function to get title with selected year
def get_page_title(page_name, selected_year):
    if selected_year != 'All Years':
        return f"{page_name} - {selected_year}"
    else:
        return page_name

# Home Page
if selected_option == 'Home':
    st.markdown("### Welcome to the homepage! 👋 \n You can interact with the sales data of the company by selecting a page from the sidebar.  \nYou can chose between a general Sales overview, view how the Account Managers sales look or  \ntake a look into how our products are delivering in the Products Category section.")
    

# Sales Overview section
elif selected_option == 'Sales Overview':
    st.markdown("### Sales Overview 📶")
    # Year selection
    year_options = get_year_options(df_viz)
    selected_year = st.sidebar.selectbox("Select Year", year_options)

    # Customer type dropdown
    customer_types = ['All Customers'] + sorted(df_viz['Customer Type'].unique())
    selected_customer_type = st.sidebar.selectbox("Select Customer Type", customer_types)

    # Filter data based on selected year and customer type
    if selected_year == 'All Years':
        filtered_df = df_viz
    else:
        filtered_df = df_viz[df_viz['Order Date'].dt.year == int(selected_year)]

    if selected_customer_type != 'All Customers':
        filtered_df = filtered_df[filtered_df['Customer Type'] == selected_customer_type]

    # Update line chart based on selected year and customer type
    sales_over_time = filtered_df.groupby('Order Date')['Total'].sum().reset_index()
    line_chart_title = f"Total Sales Over Time for {selected_customer_type} ({selected_year})"
    line_color = get_line_color(selected_year)
    line_chart = px.line(sales_over_time, x='Order Date', y='Total', title=line_chart_title)
    line_chart.update_traces(line=dict(color=line_color))

    # Calculate and display card visuals
    total_sales = filtered_df['Total'].sum()
    total_profit = filtered_df['Profit Margin'].sum()
    
    # Line chart and cards side by side
    col1, col2 = st.columns(2)
    col1.plotly_chart(line_chart)

    col2.markdown(f"<h3><b>Total Sales for {selected_customer_type} ({selected_year})</b></h3>\n<h2>{format_currency(total_sales)}</h2>", unsafe_allow_html=True)
    col2.markdown("<br>", unsafe_allow_html=True)
    col2.markdown(f"<h3><b>Total Profit for {selected_customer_type} ({selected_year})</b></h3>\n<h2>{format_currency(total_profit)}</h2>", unsafe_allow_html=True)

    
    # Title for the customer type table
    st.markdown(f"### Top 10 Orders for {selected_customer_type} ({selected_year})")

    # Select specific columns for display
    columns_to_display = [
        'Order No', 'Order Date', 'Customer Name', 'City', 'Customer Type', 
        'Account Manager', 'Order Priority', 'Product Category', 
        'Profit Margin', 'Discount %', 'Total'
    ]
    filtered_df = filtered_df[columns_to_display].nlargest(10, 'Total')

    # Display filtered data
    st.write(filtered_df)

# Account Managers section
elif selected_option == 'Sales by Account Manager':
    st.markdown("### Account Manager Overview 🤑")
    # Year selection
    year_options = get_year_options(df_viz)
    selected_year = st.sidebar.selectbox("Select Year", year_options)

    # Filter data based on selected year
    if selected_year == 'All Years':
        df_viz_filtered = df_viz
    else:
        df_viz_filtered = df_viz[df_viz['Order Date'].dt.year == int(selected_year)]

    # Top 5 Account Managers
    top_account_managers = df_viz_filtered.groupby('Account Manager')['Total'].sum().nlargest(5).reset_index()

    # Create a bar chart for Top 5 acc Managers
    bar_chart = px.bar(top_account_managers, x='Total', y='Account Manager', orientation='h', 
                       title=get_page_title("Top 5 Account Managers by Sales for ", selected_year),
                       category_orders={'Account Manager': top_account_managers['Account Manager'].tolist()})

    bar_chart.update_layout(yaxis={'categoryorder': 'total ascending'})  

    st.plotly_chart(bar_chart)

    # Account Manager Dropdown
    all_account_managers = sorted(df_viz_filtered['Account Manager'].unique())
    selected_account_manager = st.sidebar.selectbox("Select Account Manager", all_account_managers, index=0)

    # Filter data based on selected account manager and year
    if selected_year == 'All Years':
        sales_by_manager = df_viz_filtered[df_viz_filtered['Account Manager'] == selected_account_manager]
    else:
        sales_by_manager = df_viz_filtered[(df_viz_filtered['Account Manager'] == selected_account_manager) & (df_viz_filtered['Order Date'].dt.year == int(selected_year))]

    # Check if there are sales for the selected account manager in the selected year
    if not sales_by_manager.empty:
        # Sales over time for selected account manager
        sales_over_time_manager = sales_by_manager.groupby('Order Date')['Total'].sum().reset_index()

        # Check if there are sufficient data points for the line chart, need at least 2
        if len(sales_over_time_manager) > 1:  
            line_chart_manager = px.line(sales_over_time_manager, x='Order Date', y='Total', title=f'Total Sales Over Time for {selected_account_manager} ({selected_year})')
            line_chart_manager.update_traces(line=dict(color=get_line_color(selected_year)))
            st.plotly_chart(line_chart_manager)
        else:
            st.write(f"Not enough data available to generate a line chart for {selected_account_manager} in {selected_year}.")
    else:
        st.write(f"{selected_account_manager} had no sales in {selected_year}.")

# Product Categories section
elif selected_option == 'Sales by Product Category':
    # Year selection
    year_options = get_year_options(df_viz)
    selected_year_prod_cat = st.sidebar.selectbox("Select Year", year_options, index=0)
    selected_year = str(selected_year_prod_cat)  

    # Product Category Dropdown
    selected_category = st.sidebar.selectbox("Select Product Category", ['All Product Categories'] + sorted(df_viz['Product Category'].unique()), index=0)

    # Order Priority Dropdown
    selected_order_priority = st.sidebar.selectbox("Select Order Priority", ['All Priorities'] + sorted(df_viz['Order Priority'].unique()), index=0)

    st.write("### Product Category: ", selected_category, "🚀")

    # Filter data based on selected category and year
    if selected_category == 'All Product Categories':
        category_filtered_df = df_viz
    else:
        category_filtered_df = df_viz[df_viz['Product Category'] == selected_category]

    if selected_year_prod_cat != 'All Years':
        category_filtered_df = category_filtered_df[category_filtered_df['Order Date'].dt.year == int(selected_year_prod_cat)]

    # Sales Over Time for Selected Category
    sales_over_time_category = category_filtered_df.groupby('Order Date')['Total'].sum().reset_index()
    line_chart_category = px.line(sales_over_time_category, x='Order Date', y='Total', title=f'Total Sales Over Time for {selected_category} ({selected_year})')
    line_chart_category.update_traces(line=dict(color=get_line_color(selected_year_prod_cat)))

    # Display line chart and table side by side
    col1, col2 = st.columns(2)  
    col1.plotly_chart(line_chart_category)
    
    # Add space after the line chart
    st.write("\n\n")

    # Top 10 Products in Selected Category
    top_10_products = category_filtered_df.groupby('Product Name')['Total'].sum().nlargest(10).reset_index()
    col2.write(f"### Top 10 Products in {selected_category} ({selected_year})")
    col2.write(top_10_products.style.set_properties(**{'font-size': '12px'}))  

    # Filter data based on selected order priority
    if selected_order_priority != 'All Priorities':
        priority_filtered_df = category_filtered_df[category_filtered_df['Order Priority'] == selected_order_priority]
    else:
        priority_filtered_df = category_filtered_df

    # Bar chart for Total orders per Order Priority
    orders_per_priority = category_filtered_df.groupby('Order Priority')['Total'].count().reset_index().rename(columns={'Total': 'Order Count'})
    bar_chart_priority = px.bar(orders_per_priority, x='Order Priority', y='Order Count', 				
				title=f'Total Orders per Order Priority in {selected_category} ({selected_year})')

    # Display bar chart and top 5 orders table side by side
    col3, col4 = st.columns(2)
    col3.plotly_chart(bar_chart_priority)

    # Top 5 Orders per Order Priority
    top_5_orders = priority_filtered_df.nlargest(5, 'Total')[['Order No', 'Customer Type', 'Account Manager', 'Total']]
    col4.write(f"### Top 5 Orders per Order Priority for {selected_order_priority} ({selected_year})")
    col4.write(top_5_orders.style.set_properties(**{'font-size': '12px'}))  
