import pandas as pd
import numpy as np
import panel as pn
pn.extension('tabulator')
import hvplot.pandas

df = pd.read_csv("https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv")

df = df.drop(labels=['iso_code', 'trade_co2',
       'cement_co2', 'cement_co2_per_capita', 
       'coal_co2_per_capita', 'flaring_co2', 'flaring_co2_per_capita',
      'gas_co2_per_capita', 'oil_co2_per_capita',
       'other_industry_co2', 'other_co2_per_capita', 'co2_growth_prct',
       'co2_growth_abs', 'co2_per_gdp', 'co2_per_unit_energy',
       'consumption_co2', 'consumption_co2_per_capita',
       'consumption_co2_per_gdp', 'cumulative_co2', 'cumulative_cement_co2',
       'cumulative_coal_co2', 'cumulative_flaring_co2', 'cumulative_gas_co2',
       'cumulative_oil_co2', 'cumulative_other_co2', 'trade_co2_share',
       'share_global_co2', 'share_global_cement_co2', 'share_global_coal_co2',
       'share_global_flaring_co2', 'share_global_gas_co2',
       'share_global_oil_co2', 'share_global_other_co2',
       'share_global_cumulative_co2', 'share_global_cumulative_cement_co2',
       'share_global_cumulative_coal_co2',
       'share_global_cumulative_flaring_co2',
       'share_global_cumulative_gas_co2', 'share_global_cumulative_oil_co2',
       'share_global_cumulative_other_co2', 'total_ghg', 'ghg_per_capita',
       'total_ghg_excluding_lucf', 'ghg_excluding_lucf_per_capita', 'methane',
       'methane_per_capita', 'nitrous_oxide', 'nitrous_oxide_per_capita',
      'primary_energy_consumption', 'energy_per_capita',
       'energy_per_gdp'],axis=1)

df = df.fillna(0)
df['gdp_per_capita'] = np.where(df['population']!= 0, df['gdp']/ df['population'], 0)

df = df.interactive()

slider = pn.widgets.IntSlider(name='Year',start = 1900,end=2020,step=1,value=2000)

yaxis_co2 = 'co2'

continents = ['Asia', 'Europe', 'Africa', 'North America', 'South America']
co2_pipeline = (df[(df.year == slider) &(df.country.isin(continents))]
    .groupby(['country', 'year'])[yaxis_co2].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='year')  
    .reset_index(drop=True)
)

co2_plot = co2_pipeline.hvplot(x = 'year', by='country', y=yaxis_co2,line_width=2, title="CO2 emission by continent",kind='bar')

co2_table = co2_pipeline.pipe(pn.widgets.Tabulator, pagination='remote', page_size = 10, sizing_mode='stretch_width') 

co2_vs_gdp_scatterplot_pipeline = (
    df[(df.year == slider) & (~(df.country.isin(continents)))]
    .groupby(['country', 'year', 'gdp_per_capita'])['co2'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='year')  
    .reset_index(drop=True)
)

co2_vs_gdp_scatterplot = co2_vs_gdp_scatterplot_pipeline.hvplot(x='gdp_per_capita', 
                                                                y='co2', 
                                                                by='country', 
                                                                size=80, kind="scatter", 
                                                                alpha=0.7,
                                                                legend=False, 
                                                                height=500, 
                                                                width=500)

yaxis_co2_source = pn.widgets.RadioButtonGroup(
    name='Y axis', 
    options=['coal_co2', 'oil_co2', 'gas_co2'], 
    button_type='success'
)

continents_excl_world = ['Asia', 'Europe', 'Africa', 'North America', 'South America']

co2_source_bar_pipeline = (
    df[(df.year == slider) & (df.country.isin(continents_excl_world))]
    .groupby(['year', 'country'])[yaxis_co2_source].sum()
    .to_frame()
    .reset_index()
    .sort_values(by='year')  
    .reset_index(drop=True)
)

co2_source_bar_plot = co2_source_bar_pipeline.hvplot(kind='bar', 
                                                     x='country', 
                                                     y=yaxis_co2_source, 
                                                     title='CO2 source by continent')

template = pn.template.FastListTemplate(
    title='World CO2 Emission Dashboard', 
    sidebar=[pn.pane.Markdown("# CO2 Emissions"),  
             pn.pane.Markdown("## Select Year"),   
             slider],
    main=[pn.Row(pn.Column(yaxis_co2, 
                           co2_plot.panel(width=600), margin=(0,30)), 
                 co2_table.panel(width=350)), 
                 pn.Column(yaxis_co2_source, co2_source_bar_plot.panel(width=600))],
    accent_base_color="#88d8b0",
    header_background="#2E8B57",
)
template.show()
template.servable();