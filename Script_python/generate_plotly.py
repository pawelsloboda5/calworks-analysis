"""Generate interactive Plotly visualizations for CalWORKs analysis."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_eligibility_flow(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create simplified parallel categories diagram showing eligibility pathways."""
    
    # Sample data for better visibility
    plot_data = df.copy()
    if len(plot_data) > 1000:
        # Stratified sampling to maintain proportions
        plot_data = (plot_data.groupby('eligible_calworks')
                    .apply(lambda x: x.sample(n=min(500, len(x)), random_state=42))
                    .reset_index(drop=True))
    
    # Create meaningful income categories based on MBSAC
    plot_data['income_to_mbsac'] = plot_data['monthly_income'] / plot_data['MBSAC']
    plot_data['income_category'] = pd.cut(
        plot_data['income_to_mbsac'],
        bins=[-float('inf'), 0.01, 0.5, 0.8, 1.2, float('inf')],
        labels=['No Income', 'Very Low Income', 'Low Income', 'Near MBSAC', 'Above MBSAC']
    )
    
    # Create household type category
    plot_data['household_type'] = 'Single Person'
    plot_data.loc[plot_data['NP'] == 2, 'household_type'] = 'Two Person'
    plot_data.loc[plot_data['NP'] > 2, 'household_type'] = 'Family (3+)'
    
    # Create work and assistance category (fixed conditions)
    conditions = [
        (plot_data['working_members'] > 0) & 
        ((plot_data['food_stamps_receipent'] == 1) | (plot_data['public_assistance_receipent'] == 1)),
        
        (plot_data['working_members'] > 0),
        
        ((plot_data['food_stamps_receipent'] == 1) | (plot_data['public_assistance_receipent'] == 1)),
        
        (plot_data['working_members'] == 0) & 
        (plot_data['food_stamps_receipent'] == 0) & 
        (plot_data['public_assistance_receipent'] == 0)
    ]
    choices = ['Working with Assistance', 'Working Only', 'Assistance Only', 'No Work or Assistance']
    plot_data['status'] = np.select(conditions, choices, default='Other')

    # Create parallel categories diagram
    fig = go.Figure(go.Parcats(
        dimensions=[
            {
                'label': 'Household Type',
                'values': plot_data['household_type']
            },
            {
                'label': 'Income Level',
                'values': plot_data['income_category']
            },
            {
                'label': 'Work & Assistance',
                'values': plot_data['status']
            },
            {
                'label': 'CalWORKs',
                'values': plot_data['eligible_calworks'].map({True: 'Eligible', False: 'Not Eligible'})
            }
        ],
        line={
            'color': plot_data['income_to_mbsac'],
            'colorscale': 'RdYlBu',
            'shape': 'hspline',
            'cmin': 0,
            'cmax': 1.5
        },
        hoveron='color',
        hovertemplate='Count: %{count}<br>Percentage: %{probability:.1%}<br>Income/MBSAC: %{color:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': 'CalWORKs Eligibility Pathways Analysis<br>' +
                   '<sub>Sample of San Francisco Households (2022) - Color shows Income/MBSAC ratio</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1200,
        height=800,
        margin=dict(t=100, b=100)
    )

    fig.write_html(viz_dir / 'eligibility_flow.html')

def create_income_distribution(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create income distribution visualization by eligibility status."""
    
    fig = go.Figure()

    # Add MBSAC reference ranges with improved styling
    mbsac_ranges = df.groupby('NP')['MBSAC'].mean()
    colors = ['rgba(255,0,0,0.2)', 'rgba(255,0,0,0.3)', 'rgba(255,0,0,0.4)', 'rgba(255,0,0,0.5)']
    
    for i, (size, mbsac) in enumerate(mbsac_ranges.items()):
        if size <= 4:  # Show only up to 4-person households for clarity
            fig.add_vline(
                x=mbsac, 
                line_dash="dash", 
                line_color=colors[i-1], 
                line_width=2,
                annotation_text=f"{size}-person MBSAC: ${mbsac:,.0f}",
                annotation_position="top",
                annotation=dict(
                    font=dict(size=10, color="red"),
                    bordercolor="red",
                    borderwidth=1,
                    borderpad=4,
                    bgcolor="white"
                )
            )

    # Add distributions with improved styling
    for eligible, color, name in [(True, 'rgba(0,128,0,0.6)', 'CalWORKs Eligible'), 
                                 (False, 'rgba(255,0,0,0.6)', 'Not Eligible')]:
        subset = df[df['eligible_calworks'] == eligible]
        
        # Calculate histogram data for more control over appearance
        hist_data = np.histogram(
            subset['monthly_income'].clip(0, 10000),
            bins=50,
            density=True
        )
        
        # Add filled area
        fig.add_trace(go.Scatter(
            x=hist_data[1],
            y=np.concatenate([hist_data[0], [0]]),
            fill='tozeroy',
            name=name,
            line_color=color,
            fillcolor=color.replace('0.6', '0.3'),
            hovertemplate="Income: $%{x:,.0f}<br>Density: %{y:.4f}<extra></extra>"
        ))

    # Update layout with improved styling
    fig.update_layout(
        title={
            'text': 'Monthly Income Distribution by CalWORKs Eligibility<br>' +
                   '<sup>San Francisco County, 2022 (Income capped at $10,000 for visibility)</sup>',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20)
        },
        xaxis=dict(
            title="Monthly Income ($)",
            title_font=dict(size=14),
            tickformat="$,.0f",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title="Distribution Density",
            title_font=dict(size=14),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        width=1200,
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        plot_bgcolor='rgba(240,240,240,0.3)',
        paper_bgcolor='white',
        margin=dict(t=100, b=50, l=50, r=50)
    )

    # Add annotations for key insights
    median_eligible = df[df['eligible_calworks']]['monthly_income'].median()
    median_not_eligible = df[~df['eligible_calworks']]['monthly_income'].median()
    
    fig.add_annotation(
        text=f"Median Income (Eligible): ${median_eligible:,.0f}",
        x=median_eligible,
        y=0.0003,
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        arrowwidth=2,
        arrowsize=1,
        font=dict(color="green", size=10)
    )
    
    fig.add_annotation(
        text=f"Median Income (Not Eligible): ${median_not_eligible:,.0f}",
        x=median_not_eligible,
        y=0.0002,
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        arrowwidth=2,
        arrowsize=1,
        font=dict(color="red", size=10)
    )

    try:
        fig.write_html(viz_dir / 'income_distribution.html')
    except Exception as e:
        logger.error(f"Error saving income distribution visualization: {str(e)}")

def create_risk_analysis(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create visualization showing households at risk of losing eligibility."""
    
    # Focus on eligible households and create a copy
    plot_data = df[df['eligible_calworks']].copy()
    
    # Filter out zero or negative incomes for ratio calculation
    plot_data = plot_data[plot_data['monthly_income'] > 0]
    
    # Create risk categories
    plot_data['income_to_mbsac'] = plot_data['monthly_income'] / plot_data['MBSAC']
    plot_data['risk_level'] = pd.cut(
        plot_data['income_to_mbsac'],
        bins=[0, 0.3, 0.6, 0.8, 1.0],
        labels=['Low Risk (0-30% MBSAC)', 'Moderate Risk (30-60% MBSAC)', 
                'High Risk (60-80% MBSAC)', 'Very High Risk (80-100% MBSAC)']
    )
    
    # Drop rows with NaN risk levels
    plot_data = plot_data.dropna(subset=['risk_level'])
    
    # Create employment category
    plot_data['employment'] = 'Not Working'
    plot_data.loc[plot_data['working_members'] > 0, 'employment'] = 'Working'
    
    # Create assistance category
    conditions = [
        (plot_data['food_stamps_receipent'] == 1) & (plot_data['public_assistance_receipent'] == 1),
        (plot_data['food_stamps_receipent'] == 1),
        (plot_data['public_assistance_receipent'] == 1)
    ]
    choices = ['Both Programs', 'Food Stamps Only', 'Public Assistance Only']
    plot_data['assistance'] = np.select(conditions, choices, default='No Assistance')
    
    # Create summary data for visualization
    summary_data = []
    
    # Process each level of hierarchy
    for risk in plot_data['risk_level'].unique():
        risk_group = plot_data[plot_data['risk_level'] == risk]
        risk_count = len(risk_group)
        risk_avg_income = risk_group['monthly_income'].mean()
        risk_avg_ratio = risk_group['income_to_mbsac'].mean()
        
        summary_data.append({
            'risk_level': risk,
            'employment': '',
            'assistance': '',
            'count': risk_count,
            'avg_income': risk_avg_income,
            'avg_ratio': risk_avg_ratio
        })
        
        for emp in risk_group['employment'].unique():
            emp_group = risk_group[risk_group['employment'] == emp]
            emp_count = len(emp_group)
            emp_avg_income = emp_group['monthly_income'].mean()
            emp_avg_ratio = emp_group['income_to_mbsac'].mean()
            
            summary_data.append({
                'risk_level': risk,
                'employment': emp,
                'assistance': '',
                'count': emp_count,
                'avg_income': emp_avg_income,
                'avg_ratio': emp_avg_ratio
            })
            
            for asst in emp_group['assistance'].unique():
                asst_group = emp_group[emp_group['assistance'] == asst]
                asst_count = len(asst_group)
                asst_avg_income = asst_group['monthly_income'].mean()
                asst_avg_ratio = asst_group['income_to_mbsac'].mean()
                
                summary_data.append({
                    'risk_level': risk,
                    'employment': emp,
                    'assistance': asst,
                    'count': asst_count,
                    'avg_income': asst_avg_income,
                    'avg_ratio': asst_avg_ratio
                })
    
    # Convert to DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Create sunburst chart
    fig = px.sunburst(
        summary_df,
        path=['risk_level', 'employment', 'assistance'],
        values='count',
        color='avg_ratio',
        color_continuous_scale='RdYlBu_r',
        color_continuous_midpoint=0.5,
        custom_data=['count', 'avg_income', 'avg_ratio']
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="""
        <b>%{label}</b><br>
        Number of Households: %{customdata[0]:,.0f}<br>
        Avg Monthly Income: $%{customdata[1]:,.2f}<br>
        Avg Income/MBSAC: %{customdata[2]:.1%}
        <extra></extra>
        """
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Risk Analysis of CalWORKs Eligible Households<br>' +
                   '<sub>Size shows number of households, color shows income/MBSAC ratio</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1000,
        height=1000,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    fig.write_html(viz_dir / 'risk_analysis.html')

def create_household_treemap(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create treemap visualization showing household distribution and eligibility."""
    
    # Create a copy and prepare data
    plot_data = df.copy()
    
    # Calculate income to MBSAC ratio
    plot_data['income_to_mbsac'] = plot_data['monthly_income'] / plot_data['MBSAC']
    
    # Add root column for single hierarchy
    plot_data['root'] = 'All SF Households'
    
    # Create household size category
    plot_data['size_category'] = pd.cut(
        plot_data['NP'],
        bins=[-float('inf'), 1, 2, 4, float('inf')],
        labels=['Single Person', 'Two Person', 'Small Family (3-4)', 'Large Family (5+)']
    )
    
    # Create income category
    plot_data['income_category'] = pd.cut(
        plot_data['monthly_income'],
        bins=[-float('inf'), 0, 2500, 5000, 10000, float('inf')],
        labels=['No Income', '$0-$2.5k', '$2.5k-$5k', '$5k-$10k', '$10k+']
    )
    
    # Create eligibility status
    plot_data['eligibility'] = plot_data['eligible_calworks'].map({
        True: 'CalWORKs Eligible',
        False: 'Not Eligible'
    })
    
    # Aggregate data for visualization - modified to handle zero counts
    agg_data = (plot_data.groupby(['root', 'size_category', 'income_category', 'eligibility'])
                .agg({
                    'monthly_income': 'sum',
                    'NP': 'mean',
                    'MBSAC': 'mean',
                    'income_to_mbsac': 'mean'
                })
                .reset_index())
    
    # Filter out any rows with NaN or zero values
    agg_data = agg_data.dropna()
    agg_data = agg_data[agg_data['monthly_income'] > 0]
    
    # Only proceed if we have data to visualize
    if len(agg_data) == 0:
        logger.warning("No valid data for treemap visualization")
        return
    
    # Create treemap
    fig = px.treemap(
        agg_data,
        path=[px.Constant("All SF Households"), 'size_category', 'income_category', 'eligibility'],
        values='monthly_income',
        color='income_to_mbsac',
        color_continuous_scale='RdYlBu',
        color_continuous_midpoint=1.0,
        custom_data=['NP', 'monthly_income', 'MBSAC', 'income_to_mbsac']
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Household Distribution by Size, Income, and CalWORKs Eligibility<br>' +
                   '<sub>Size shows total monthly income, color shows income/MBSAC ratio</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1200,
        height=800,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="""
        <b>%{label}</b><br>
        Total Monthly Income: $%{value:,.2f}<br>
        Avg Household Size: %{customdata[0]:.1f}<br>
        Avg MBSAC: $%{customdata[2]:,.2f}<br>
        Income/MBSAC: %{customdata[3]:.2%}
        <extra></extra>
        """,
        root_color="lightgrey"
    )
    
    try:
        fig.write_html(viz_dir / 'household_treemap.html')
    except Exception as e:
        logger.error(f"Error saving treemap visualization: {str(e)}")

def create_eligibility_funnel(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create funnel chart showing progression through eligibility stages."""
    
    # Calculate stage counts
    total_households = len(df)
    income_eligible = df['income_eligible'].sum()
    assistance_eligible = (df['food_stamps_receipent'] | df['public_assistance_receipent']).sum()
    working_households = (df['working_members'] > 0).sum()
    calworks_eligible = df['eligible_calworks'].sum()
    
    # Create funnel data
    fig = go.Figure(go.Funnel(
        name='Eligibility Pipeline',
        y=[
            'Total Households',
            'Income Eligible',
            'Current Assistance',
            'Working Households',
            'CalWORKs Eligible'
        ],
        x=[
            total_households,
            income_eligible,
            assistance_eligible,
            working_households,
            calworks_eligible
        ],
        textposition="auto",
        textinfo="value+percent initial",
        opacity=0.85,
        marker={
            "color": ["royalblue", "mediumslateblue", "darkviolet", "mediumpurple", "rebeccapurple"],
            "line": {"width": [2, 2, 2, 2, 2], "color": ["white", "white", "white", "white", "white"]}
        },
        connector={"line": {"color": "royalblue", "dash": "dot", "width": 2}}
    ))
    
    # Add detailed funnel for assistance breakdown
    assistance_data = go.Funnel(
        name='Assistance Breakdown',
        y=[
            'Eligible for Assistance',
            'Food Stamps',
            'Public Assistance',
            'Both Programs'
        ],
        x=[
            assistance_eligible,
            df['food_stamps_receipent'].sum(),
            df['public_assistance_receipent'].sum(),
            (df['food_stamps_receipent'] & df['public_assistance_receipent']).sum()
        ],
        textposition="inside",
        textinfo="value+percent previous",
        marker={
            "color": ["darkviolet", "plum", "orchid", "mediumorchid"]
        }
    )
    
    fig.add_trace(assistance_data)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'CalWORKs Eligibility Pipeline<br>' +
                   '<sub>Progression through eligibility stages and assistance program breakdown</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1200,
        height=800,
        showlegend=True,
        margin=dict(t=100, l=25, r=25, b=25)
    )
    
    # Add explanatory annotation
    fig.add_annotation(
        text=(
            "Main funnel shows overall eligibility progression<br>"
            "Secondary funnel breaks down assistance program participation"
        ),
        xref="paper", yref="paper",
        x=0, y=-0.1,
        showarrow=False,
        font=dict(size=10)
    )
    
    fig.write_html(viz_dir / 'eligibility_funnel.html')

def generate_all_plotly_visualizations(df: pd.DataFrame, viz_dir: Path) -> None:
    """Generate all Plotly visualizations."""
    logger.info("Generating Plotly visualizations...")
    
    try:
        plotly_dir = viz_dir / "plotly"
        plotly_dir.mkdir(parents=True, exist_ok=True)
        
        create_eligibility_flow(df, plotly_dir)
        create_income_distribution(df, plotly_dir)
        create_risk_analysis(df, plotly_dir)
        create_household_treemap(df, plotly_dir)
        create_eligibility_funnel(df, plotly_dir)
        
        logger.info(f"Successfully generated Plotly visualizations in {plotly_dir}")
        
    except Exception as e:
        logger.error(f"Error generating Plotly visualizations: {str(e)}")
        raise
