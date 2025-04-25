import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def maternal_mortality_helper(df):
    # Cleaning the data
    maternal_df = df[['country', 'alpha_3_code', 'time_period', 'obs_value', 'Population, total']]

    # Making the dataset more readable
    maternal_df = maternal_df.rename(columns={
        'country': 'Country',
        'alpha_3_code': 'CountryCode',
        'time_period': 'Year',
        'obs_value': 'MaternalDeaths',
        'Population, total': 'Population'
    })

    # Plotting the heat map
    fig = px.choropleth(
        maternal_df,
        locations='Country',
        locationmode='country names',
        color='MaternalDeaths',
        color_continuous_scale='Plasma',
        animation_frame='Year',  # This makes the heat map animated by year
        hover_name='Country',
        hover_data={
            'MaternalDeaths': True,
            'Population': True, 
            'Year': False,    
            'Country': False
        },
        title='Maternal Deaths Over Year (2000 - 2020)'
    )

    # Customize the layout to improve the slider appearance
    fig.update_layout(
        title='Maternal Deaths Over Year (2000 - 2020)',
        geo=dict(showcoastlines=True),
        coloraxis_colorbar=dict(title='Value'),
        sliders=[{
            'currentvalue': {
                'prefix': 'Year: ',
                'visible': True,
                'font': {'size': 16}
            }
        }]
    )

    # Setting the color spectrum
    fig.update_layout(coloraxis_colorbar=dict(title='Value', tickformat=".0f"))
    fig.update_coloraxes(cmin=1, cmax=120000, colorscale='Plasma', colorbar_title='Value', colorbar_tickformat=".0f")
    fig.update_traces(zmin=1, zmax=120000, selector=dict(type='choropleth'))
    
    # Show the interactive figure
    fig.show()

def correlation_HB_LE_helper(df):
    # Prepare the data
    df = df[['country', 'time_period', 
                    'Life expectancy at birth, total (years)', 
                    'Hospital beds (per 1,000 people)']]

    # Rename for simplicity
    df = df.rename(columns={
        'country': 'Country',
        'time_period': 'Year',
        'Life expectancy at birth, total (years)': 'Life_Expectancy',
        'Hospital beds (per 1,000 people)': 'Hospital_Beds'
    })

    # Flag rows with complete data
    df['has_data'] = ~(
        df['Life_Expectancy'].isna() | df['Hospital_Beds'].isna()
    )

    # Create animated scatter plot
    fig = px.scatter(
        df,
        x="Hospital_Beds",
        y="Life_Expectancy",
        animation_frame="Year",
        animation_group="Country",
        color="has_data",
        color_discrete_map={True: "dodgerblue", False: "lightgray"},
        hover_name="Country",
        hover_data={
            "has_data":False,
            "Life_Expectancy": True,
            "Hospital_Beds": True
        },
        labels={
            "Hospital_Beds": "Hospital Beds per 1,000 People",
            "Life_Expectancy": "Life Expectancy (Years)"
        },
        title="Life Expectancy vs Hospital Beds Over Time"
    )

    # Improve layout and transitions
    fig.update_traces(marker=dict(opacity=0.8))
    fig.update_layout(
        xaxis_title="Hospital Beds per 1,000 People",
        yaxis_title="Life Expectancy (Years)",
        hovermode='closest',
        transition_duration=500,
        legend_title_text='Complete Data'
    )

    fig.show()

def birth_rate_vs_GDP_helper(df):
    df = df[['country', 'time_period', 'GDP per capita (constant 2015 US$)', 'Birth rate, crude (per 1,000 people)', 'Population, total']]

    df = df.rename(columns = {
        'country': 'Country',
        'time_period': 'Year',
        'GDP per capita (constant 2015 US$)': 'GDP_Per_Capita',
        'Birth rate, crude (per 1,000 people)': 'Birth_Rate',
        'Population, total': 'Population'
    })

    # Ensure Year is clean
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int).astype(str)

    # Flag GDP presence
    df['has_gdp'] = df['GDP_Per_Capita'].notna()

    # Conditionally forward fill Birth Rate only if GDP is not missing
    df['Birth_Rate_Filled'] = df['Birth_Rate']  # Copy for fill

    df['Birth_Rate_Filled'] = df.groupby('Country').apply(
        lambda group: group['Birth_Rate'].ffill() if group['GDP_Per_Capita'].notna().any() else group['Birth_Rate']
    ).reset_index(level=0, drop=True)

    # Replace NaN GDP with 0 for visual x-axis handling (optional)
    df['GDP_Per_Capita_Display'] = df['GDP_Per_Capita'].fillna(0)

    df['Population'] = df['Population'].fillna(1)

    # Animated scatter plot
    fig = px.scatter(
        df,
        x="GDP_Per_Capita_Display",
        y="Birth_Rate_Filled",
        animation_frame="Year",
        animation_group="Country",
        size="Population",
        color="has_gdp",
        color_discrete_map={True: 'coral', False: 'lightgray'},
        hover_name="Country",
        hover_data={
            "has_gdp": False,
            "GDP_Per_Capita": True,
            "Birth_Rate": True,
            "Population": True
        },
        labels={
            "GDP_Per_Capita_Display": "GDP per Capita",
            "Birth_Rate_Filled": "Crude Birth Rate"
        },
        title="Crude Birth Rate vs GDP per Capita Over Time"
    )

    # Layout tweaks
    fig.update_layout(
        xaxis_title="GDP per Capita (constant 2015 USD)",
        yaxis_title="Crude Birth Rate (per 1,000 people)",
        transition_duration=500,
        legend_title_text='Has GDP Data'
    )

    fig.show()

def vaccination_coverage_helper(df):
    df = df[['country', 'time_period', 'obs_value', 'current_age', 'Population, total']]

    df = df.rename(columns = {
        'country': 'Country',
        'time_period': 'Year',
        'obs_value': 'SurvivalPercent',
        'current_age': 'Birth_Rate',
        'Population, total': 'Population'
    })

    # Drop rows with missing values
    df = df.dropna(subset=['Country', 'Year', 'Population', 'SurvivalPercent'])

    # Ensure correct types
    df['Year'] = df['Year'].astype(str)

    # Get list of years
    years = sorted(df['Year'].unique())

    # Create a frame for each year
    frames = []
    for year in years:
        data_year = df[df['Year'] == year]
        frame = go.Frame(
            data=[
                go.Treemap(
                    labels=data_year['Country'],
                    parents=[""] * len(data_year),  # No hierarchy
                    values=data_year['Population'],
                    marker=dict(
                        colors=data_year['SurvivalPercent'],
                        colorscale='Viridis',
                        colorbar=dict(title='Vaccination %')
                    ),
                    textinfo='label+value+text',
                    text=data_year['SurvivalPercent'].round(1).astype(str) + '%'
                )
            ],
            name=year
        )
        frames.append(frame)

    # Initial frame (first year)
    initial_data = df[df['Year'] == years[0]]

    # Base figure
    fig = go.Figure(
        data=[
            go.Treemap(
                labels=initial_data['Country'],
                parents=[""] * len(initial_data),
                values=initial_data['Population'],
                marker=dict(
                    colors=initial_data['SurvivalPercent'],
                    colorscale='Viridis',
                    colorbar=dict(title='Vaccination %')
                ),
                textinfo='label+value+text',
                text=initial_data['SurvivalPercent'].round(1).astype(str) + '%'
            )
        ],
        frames=frames,
        layout=go.Layout(
            title='Vaccination Coverage vs Population (with Year Slider)',
            updatemenus=[
                {
                    "buttons": [
                        {
                            "args": [None, {"frame": {"duration": 1000, "redraw": True},
                                            "fromcurrent": True}],
                            "label": "Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate"}],
                            "label": "Pause",
                            "method": "animate"
                        }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }
            ],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Year: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 500},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [{
                    "args": [[year], {"frame": {"duration": 0, "redraw": True},
                                    "mode": "immediate"}],
                    "label": year,
                    "method": "animate"
                } for year in years]
            }]
        )
    )

    fig.show()