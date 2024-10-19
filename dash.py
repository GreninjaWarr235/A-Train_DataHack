import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# Title of the dashboard
st.title('Streamlit Dashboard')

# Bar Chart
st.header('Bar Graph Example')

# Data for the bar chart
categories = ['A', 'B', 'C', 'D']
values = [10, 24, 36, 20]

# Create a dynamic bar chart using plotly
bar_chart = go.Figure([go.Bar(x=categories, y=values, marker_color='lightblue')])

# Customize layout to make it more appealing with animation and layout tweaks
bar_chart.update_layout(
    title="Bar Chart Example",
    xaxis_title="Categories",
    yaxis_title="Values",
    template="plotly_dark",  
    height=500,
    width=700,
    transition={'duration': 500},  # Animation for smooth transitions
)

# Display the bar chart using Streamlit
st.plotly_chart(bar_chart)

# Pie Chart
st.header('Pie Chart Example')

# Data for pie chart
labels = ['Category A', 'Category B', 'Category C', 'Category D']
sizes = [10, 24, 36, 20]
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

# Create pie chart with a small animation
pie_chart = go.Figure(go.Pie(labels=labels, values=sizes, marker_colors=colors, hole=0.3))

# Add animation for pie chart
pie_chart.update_traces(pull=[0.1, 0, 0, 0], rotation=90, textinfo="percent+label")
pie_chart.update_layout(transition={'duration': 500})

# Display the pie chart using Streamlit
st.plotly_chart(pie_chart)


# Circular Progress Chart Function
def circular_progress_chart(percentage, label):
    fig = go.Figure(go.Pie(
        values=[percentage, 100 - percentage],
        marker=dict(colors=['blue', 'lightgray']),
        hole=.7,
        direction='clockwise',
        textinfo='none',
        showlegend=False,
    ))

    # Update the layout for annotations and margins
    fig.update_layout(
        annotations=[dict(text=f'{percentage}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
        height=200, width=200,
        margin=dict(l=20, r=20, t=20, b=20),
        transition={'duration': 300},  # Smooth transitions for loading effect
    )
    
    return fig


# Create a column layout to align progress circles horizontally
st.header('Progress Circles (Circular)')

# Create three columns to place the charts side by side
col1, col2, col3, col4 = st.columns(4)

# Display progress charts in each column
with col1:
    st.plotly_chart(circular_progress_chart(25, "Percentage 1"), use_container_width=True)
with col2:
    st.plotly_chart(circular_progress_chart(50, "Percentage 2"), use_container_width=True)
with col3:
    st.plotly_chart(circular_progress_chart(75, "Percentage 3"), use_container_width=True)
with col4:
    st.plotly_chart(circular_progress_chart(100, "Percentage 4"), use_container_width=True)

