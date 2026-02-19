import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def diversity(data:[np.ndarray,np.ndarray],bins:[np.ndarray, np.ndarray]):
    H,_,_ = np.histogram2d(data[0],data[1],bins)
    divers = np.sum(H>0)
    return divers



def plot_time_diversity_plotly(content_random, content_imgep=None, name=None, title=None, label_algo='imgep', num_bank=4, num_row=2, show=False):
    # Create subplots with the same layout as original
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            f"Core0: imgep vs random",
            f"Core1: imgep vs random",
            "Core0 Time Difference",
            "Core1 Time Difference",
            #"Core0 vs Core1 Together"
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"colspan": 2, "secondary_y": False}, None]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )

    # Calculate bins and diversity for core0
    bins_core0 = np.arange(0, 400, 5)
    diversity_time_rand_core0 = diversity([content_random['memory_perf']['core0']['time_core0'], content_random['memory_perf']['mutual']['time_core0']], [bins_core0, bins_core0])
    diversity_time_imgep_core0 = diversity([content_imgep['memory_perf']['core0']['time_core0'], content_imgep['memory_perf']['mutual']['time_core0']], [bins_core0, bins_core0])

    # Create hover text for core0 scatter plots
    hover_imgep_core0 = [
        f"<b>IMGEP - Sample {i}</b><br>"
        f"Core0 Alone: {content_imgep['memory_perf']['core0']['time_core0'][i]:.2f}<br>"
        f"Core0 Together: {content_imgep['memory_perf']['mutual']['time_core0'][i]:.2f}<br>"
        f"Difference: {content_imgep['memory_perf']['mutual']['time_core0'][i] - content_imgep['memory_perf']['core0']['time_core0'][i]:.2f}<br>"
        f"miss_ratio bank [0] isolation,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][0]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] isolation,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][1]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] isolation,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][2]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] isolation,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][3]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_imgep['memory_program']['core0'][i]}<br>"
        f"code 1: {content_imgep['memory_program']['core1'][i]}<br>"
        f"<extra>IMGEP Core0 Data</extra>"
        for i in range(len(content_imgep['memory_perf']['core0']['time_core0']))
    ]

    hover_random_core0 = [
        f"<b>Random - Sample {i}</b><br>"
        f"Core0 Alone: {content_random['memory_perf']['core0']['time_core0'][i]:.2f}<br>"
        f"Core0 Together: {content_random['memory_perf']['mutual']['time_core0'][i]:.2f}<br>"
        f"miss_ratio bank [0] isolation,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][0]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] isolation,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][1]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] isolation,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][2]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] isolation,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][3]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_random['memory_program']['core0'][i]}<br>"
        f"code 1: {content_random['memory_program']['core1'][i]}<br>"
        f"<extra>Random Core0 Data</extra>"
        for i in range(len(content_random['memory_perf']['core0']['time_core0']))
    ]

    # Plot 1: Core0 scatter
    fig.add_trace(
        go.Scatter(
            x=content_imgep['memory_perf']['core0']['time_core0'],
            y=content_imgep['memory_perf']['mutual']['time_core0'],
            mode='markers',
            name='imgep',
            opacity=0.5,
            marker=dict(size=8, color='blue'),  # Explicitly set color
            hovertext=hover_imgep_core0,
            hoverinfo='text'
        ), row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=content_random['memory_perf']['core0']['time_core0'],
            y=content_random['memory_perf']['mutual']['time_core0'],
            mode='markers',
            name='random',
            opacity=0.5,
            marker=dict(size=8, color='orange'),  # Explicitly set color
            hovertext=hover_random_core0,
            hoverinfo='text'
        ), row=1, col=1
    )

    # Add diagonal line
    max_val_core0 = max(np.max(content_imgep['memory_perf']['core0']['time_core0']),
                        np.max(content_imgep['memory_perf']['mutual']['time_core0']),
                        np.max(content_random['memory_perf']['core0']['time_core0']),
                        np.max(content_random['memory_perf']['mutual']['time_core0']))
    fig.add_trace(
        go.Scatter(
            x=[0, max_val_core0],
            y=[0, max_val_core0],
            mode='lines',
            line=dict(color='red', width=2),
            name='y=x',
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=1
    )

    # Update subplot 1
    fig.update_xaxes(title_text='time[isolation], core0', row=1, col=1, gridcolor='lightgray', gridwidth=1)
    fig.update_yaxes(title_text='time[non-isolation], core0', row=1, col=1, gridcolor='lightgray', gridwidth=1)

    # Calculate bins and diversity for core1
    bins_core1 = np.arange(0,400, 5)
    diversity_time_rand_core1 = diversity([content_random['memory_perf']['core1']['time_core1'], content_random['memory_perf']['mutual']['time_core1']], [bins_core1, bins_core1])
    diversity_time_imgep_core1 = diversity([content_imgep['memory_perf']['core1']['time_core1'], content_imgep['memory_perf']['mutual']['time_core1']], [bins_core1, bins_core1])

    # Create hover text for core1 scatter plots
    hover_imgep_core1 = [
        f"<b>IMGEP - Sample {i}</b><br>"
        f"Core1 Alone: {content_imgep['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"Core1 Together: {content_imgep['memory_perf']['mutual']['time_core1'][i]:.2f}<br>"
        f"Difference: {content_imgep['memory_perf']['mutual']['time_core1'][i] - content_imgep['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"miss_ratio bank [0] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][0]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][0]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][1]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][1]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][2]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][2]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][3]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][3]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_imgep['memory_program']['core0'][i]}<br>"
        f"code 1: {content_imgep['memory_program']['core1'][i]}<br>"
        f"<extra>IMGEP Core1 Data</extra>"
        for i in range(len(content_imgep['memory_perf']['core1']['time_core1']))
    ]

    hover_random_core1 = [
        f"<b>Random - Sample {i}</b><br>"
        f"Core1 Alone: {content_random['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"Core1 Together: {content_random['memory_perf']['mutual']['time_core1'][i]:.2f}<br>"
        f"Difference: {content_random['memory_perf']['mutual']['time_core1'][i] - content_random['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"miss_ratio bank [0] isolation,mutual: {content_random['memory_perf']['core1']['miss_ratios_global'][i][0]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] isolation,mutual: {content_random['memory_perf']['core1']['miss_ratios_global'][i][1]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] isolation,mutual: {content_random['memory_perf']['core1']['miss_ratios_global'][i][2]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] isolation,mutual: {content_random['memory_perf']['core1']['miss_ratios_global'][i][3]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_random['memory_program']['core0'][i]}<br>"
        f"code 1: {content_random['memory_program']['core1'][i]}<br>"
        f"<extra>Random Core1 Data</extra>"
        for i in range(len(content_random['memory_perf']['core1']['time_core1']))
    ]

    # Plot 2: Core1 scatter
    fig.add_trace(
        go.Scatter(
            x=content_imgep['memory_perf']['core1']['time_core1'],
            y=content_imgep['memory_perf']['mutual']['time_core1'],
            mode='markers',
            name='imgep',
            opacity=0.5,
            marker=dict(size=8, color='blue'),  # Explicitly set color
            hovertext=hover_imgep_core1,
            hoverinfo='text',
            showlegend=False  # Hide legend for duplicate trace
        ), row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=content_random['memory_perf']['core1']['time_core1'],
            y=content_random['memory_perf']['mutual']['time_core1'],
            mode='markers',
            name='random',
            opacity=0.5,
            marker=dict(size=8, color='orange'),  # Explicitly set color
            hovertext=hover_random_core1,
            hoverinfo='text',
            showlegend=False  # Hide legend for duplicate trace
        ), row=1, col=2
    )

    # Add diagonal line for core1
    max_val_core1 = max(np.max(content_imgep['memory_perf']['core1']['time_core1']),
                        np.max(content_imgep['memory_perf']['mutual']['time_core1']),
                        np.max(content_random['memory_perf']['core1']['time_core1']),
                        np.max(content_random['memory_perf']['mutual']['time_core1']))
    fig.add_trace(
        go.Scatter(
            x=[0, max_val_core1],
            y=[0, max_val_core1],
            mode='lines',
            line=dict(color='red', width=2),
            name='y=x',
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=2
    )

    # Update subplot 2
    fig.update_xaxes(title_text='time[isolation], core1', row=1, col=2, gridcolor='lightgray', gridwidth=1)
    fig.update_yaxes(title_text='time[non-isolation], core1', row=1, col=2, gridcolor='lightgray', gridwidth=1)

    # Plot 3: Core0 time difference histogram
    # Fix: Use showlegend=False for histograms to prevent duplicate legend entries
    fig.add_trace(
        go.Histogram(
            x=content_imgep['memory_perf']['mutual']['time_core0'] - content_imgep['memory_perf']['core0']['time_core0'],
            xbins=dict(start=-100, end=100, size=5),
            name='imgep',  # Keep the same name for proper grouping
            opacity=0.5,
            marker_color='blue',  # Use same color as scatter plot
            hovertemplate="<b>IMGEP Core0 Time Difference</b><br>"
                        "Bin: %{x}<br>"
                        "Count: %{y}<br>"
                        "<extra></extra>",
            showlegend=False  # This prevents duplicate legend entry
        ), row=2, col=1
    )

    fig.add_trace(
        go.Histogram(
            x=content_random['memory_perf']['mutual']['time_core0'] - content_random['memory_perf']['core0']['time_core0'],
            xbins=dict(start=-100, end=100, size=5),
            name='random',  # Keep the same name for proper grouping
            opacity=0.5,
            marker_color='orange',  # Use same color as scatter plot
            hovertemplate="<b>Random Core0 Time Difference</b><br>"
                        "Bin: %{x}<br>"
                        "Count: %{y}<br>"
                        "<extra></extra>",
            showlegend=False  # This prevents duplicate legend entry
        ), row=2, col=1
    )

    fig.update_xaxes(title_text='time[non-isolation] - time[isolation]', row=2, col=1)

    # Plot 4: Core1 time difference histogram
    fig.add_trace(
        go.Histogram(
            x=content_imgep['memory_perf']['mutual']['time_core1'] - content_imgep['memory_perf']['core1']['time_core1'],
            xbins=dict(start=-100, end=100, size=5),
            name='imgep',  # Keep the same name for proper grouping
            opacity=0.5,
            marker_color='blue',  # Use same color as scatter plot
            hovertemplate="<b>IMGEP Core1 Time Difference</b><br>"
                        "Bin: %{x}<br>"
                        "Count: %{y}<br>"
                        "<extra></extra>",
            showlegend=False  # This prevents duplicate legend entry
        ), row=2, col=2
    )

    fig.add_trace(
        go.Histogram(
            x=content_random['memory_perf']['mutual']['time_core1'] - content_random['memory_perf']['core1']['time_core1'],
            xbins=dict(start=-100, end=100, size=5),
            name='random',  # Keep the same name for proper grouping
            opacity=0.5,
            marker_color='orange',  # Use same color as scatter plot
            hovertemplate="<b>Random Core1 Time Difference</b><br>"
                        "Bin: %{x}<br>"
                        "Count: %{y}<br>"
                        "<extra></extra>",
            showlegend=False  # This prevents duplicate legend entry
        ), row=2, col=2
    )

    fig.update_xaxes(title_text='time[non-isolation] - time[isolation]', row=2, col=2)

    # Update subplot titles with diversity values
    fig.layout.annotations[0].update(text=f'imgep:{diversity_time_imgep_core0:.2f}, rand:{diversity_time_rand_core0:.2f}')
    fig.layout.annotations[1].update(text=f'imgep:{diversity_time_imgep_core1:.2f}, rand:{diversity_time_rand_core1:.2f}')

    hover_imgep_diff = [
        f"<b>IMGEP - Sample {i}</b><br>"
        f"Core0 Alone: {content_imgep['memory_perf']['core0']['time_core0'][i]:.2f},Core1 Alone: {content_imgep['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"Core0 Together: {content_imgep['memory_perf']['mutual']['time_core0'][i]:.2f}"
        f"Core1 Together: {content_imgep['memory_perf']['mutual']['time_core1'][i]:.2f}<br>"
        f"miss_ratio bank [0] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][0]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][0]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][1]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][1]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][2]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][2]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] core 0, core 1,mutual: {content_imgep['memory_perf']['core0']['miss_ratios_global'][i][3]:.2f},{content_imgep['memory_perf']['core1']['miss_ratios_global'][i][3]:.2f},{content_imgep['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_imgep['memory_program']['core0'][i]}<br>"
        f"code 1: {content_imgep['memory_program']['core1'][i]}<br>"
        f"<extra>IMGEP Core1 Data</extra>"
        for i in range(len(content_imgep['memory_perf']['core1']['time_core1']))
    ]

    hover_random_diff = [
        f"<b>IMGEP - Sample {i}</b><br>"
        f"Core0 Alone: {content_random['memory_perf']['core0']['time_core0'][i]:.2f},Core1 Alone: {content_random['memory_perf']['core1']['time_core1'][i]:.2f}<br>"
        f"Core0 Together: {content_random['memory_perf']['mutual']['time_core0'][i]:.2f}"
        f"Core1 Together: {content_random['memory_perf']['mutual']['time_core1'][i]:.2f}<br>"
        f"miss_ratio bank [0] core 0, core 1,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][0]:.2f},{content_random['memory_perf']['core1']['miss_ratios_global'][i][0]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][0]:.2f}<br>"
        f"miss_ratio bank [1] core 0, core 1,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][1]:.2f},{content_random['memory_perf']['core1']['miss_ratios_global'][i][1]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][1]:.2f}<br>"
        f"miss_ratio bank [2] core 0, core 1,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][2]:.2f},{content_random['memory_perf']['core1']['miss_ratios_global'][i][2]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][2]:.2f}<br>"
        f"miss_ratio bank [3] core 0, core 1,mutual: {content_random['memory_perf']['core0']['miss_ratios_global'][i][3]:.2f},{content_random['memory_perf']['core1']['miss_ratios_global'][i][3]:.2f},{content_random['memory_perf']['mutual']['miss_ratios_global'][i][3]:.2f}<br>"
        f"code 0: {content_random['memory_program']['core0'][i]}<br>"
        f"code 1: {content_random['memory_program']['core1'][i]}<br>"
        f"<extra>IMGEP Core1 Data</extra>"
        for i in range(len(content_random['memory_perf']['core1']['time_core1']))
    ]

    fig.add_trace(
        go.Scatter(
            x=content_imgep['memory_perf']['mutual']['diff_time_core0'],
            y=content_imgep['memory_perf']['mutual']['diff_time_core1'],
            mode='markers',
            name='imgep',
            opacity=0.5,
            marker=dict(size=8, color='blue'),  # Explicitly set color
            hovertext=hover_imgep_diff,
            hoverinfo='text',
            showlegend=False  # Hide legend for duplicate trace
        ), row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=content_random['memory_perf']['mutual']['diff_time_core0'],
            y=content_random['memory_perf']['mutual']['diff_time_core1'],
            mode='markers',
            name='random',
            opacity=0.5,
            marker=dict(size=8, color='orange'),  # Explicitly set color
            hovertext=hover_random_diff,
            hoverinfo='text',
            showlegend=False  # Hide legend for duplicate trace
        ), row=3, col=1
    )



    fig.update_xaxes(title_text='time[non-isolation] - time[isolation], core 0', row=3, col=1)
    fig.update_yaxes(title_text='time[non-isolation] - time[isolation], core 1', row=3, col=1)



    # Enhanced hover configuration
    fig.update_layout(
        height=1000,
        width=1200,
        title_text=title if title else None,
        title_x=0.5,
        title_font_size=15,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='closest',
        hoverdistance=100,
        spikedistance=1000,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial",
            bordercolor="black",
            align="left",
            namelength=-1,
        )
    )

    # Add custom CSS for better tooltip positioning
    fig.update_layout(
        template="plotly_white"
    )

    # For even more control, you can add custom JavaScript
    if show:
        fig.show(config={
            'displayModeBar': True,
            'scrollZoom': True,
            'hoverlabel': {
                'bgcolor': 'white',
                'font': {'size': 12},
                'bordercolor': 'black',
            }
        })
    else:
        fig.show(config={
            'displayModeBar': True,
            'scrollZoom': True
        })

    # Save or show
    if name:
        k = 0
        while os.path.isfile(f'{name}_{k}.png'):
            k += 1
        fig.write_image(f'{name}_{k}.png')
        fig.write_image(f'{name}_{k}.pdf')
        fig.write_html(f'{name}_{k}.html')
    return fig
# Alternative: Create an HTML file with custom CSS for even better tooltip control
def save_plot_with_custom_tooltips(fig, filename="plot_with_tooltips.html"):
    """Save the plot as HTML with custom CSS for better tooltip positioning"""
    
    custom_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            .js-plotly-plot .plotly .hoverlayer .hovertext {
                max-width: 400px !important;
                white-space: normal !important;
                background: white !important;
                border: 2px solid #000 !important;
                border-radius: 5px !important;
                padding: 10px !important;
                font-size: 12px !important;
                box-shadow: 3px 3px 10px rgba(0,0,0,0.3) !important;
            }
            .js-plotly-plot .plotly .hoverlabel {
                transform: translate(20px, -50%) !important; /* Move tooltip away from cursor */
            }
        </style>
    </head>
    <body>
        <div id="plot"></div>
        <script>
            Plotly.react('plot', %s, %s);
            
            // Additional JavaScript to handle tooltip positioning
            document.getElementById('plot').on('plotly_hover', function(data) {
                // Optional: Custom tooltip handling
                console.log('Hover data:', data);
            });
        </script>
    </body>
    </html>
    """ % (fig.to_json(), fig.layout.to_json())
    
    with open(filename, 'w') as f:
        f.write(custom_html)
    
    print(f"Plot saved as {filename} with enhanced tooltips")

# Usage example:
# fig = plot_time_diversity_plotly(content_random, content_imgep, show=True)
# save_plot_with_custom_tooltips(fig, "my_plot.html")
