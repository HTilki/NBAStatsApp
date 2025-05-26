"""
Charts module for NBAStatsApp.

This module contains reusable chart functions used across the application,
extracted from player_profile_old.py and team_stats_old.py.
"""

import plotly.express as px
import polars as pl
from typing import Optional
from plotly.graph_objects import Figure


def season_metric_chart(
    trend_data: pl.DataFrame,
    splits_df: pl.DataFrame,
    metric_name: str,
    metric_column: str,
    opponent: Optional[str] = None,
    y_suffix: str = "",
) -> Figure:
    """
    Create a scatter plot for a season's performance on a specific metric.

    Args:
        trend_data (pl.DataFrame): The filtered player/team data
        metric_name (str): Display name for the metric
        metric_column (str): Column name in the dataframe
        opponent (str, optional): Selected opponent. Defaults to None.
        y_suffix (str, optional): Suffix for y-axis label. Defaults to "".

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    is_percentage = metric_name.lower() in [
        "field_goal_percent",
        "two_point_percent",
        "three_point_percent",
        "free_throw_percent",
        "fg_pct",
        "two_p_pct",
        "three_p_pct",
        "ft_pct",
    ]
    if is_percentage:
        display_values = trend_data[metric_column] * 100
    else:
        display_values = trend_data[metric_column]
    # Create a color array to highlight selected team
    if opponent != "All Teams":
        trend_data_opponent = trend_data.with_columns(
            pl.when(pl.col("opponent") == opponent)
            .then(pl.lit(f"vs {opponent}"))
            .otherwise(pl.lit("vs Other"))
            .alias("team_color"),
        )
        fig_trend = px.scatter(
            x=trend_data_opponent["date"],
            y=display_values,
            color=trend_data_opponent["team_color"],
            labels={"x": "Date", "y": f"{metric_name}{y_suffix}"},
            trendline="lowess",
            trendline_color_override="green",
            trendline_scope="overall",
            color_discrete_map={
                # TODO add custom hexadecimal colors of opponent
                f"vs {opponent}": "red",
                "vs Other": "rgba(3, 199, 253, 0.5)",
            },
        )
    else:
        fig_trend = px.scatter(
            x=trend_data["date"],
            y=display_values,
            labels={"x": "Date", "y": f"{metric_name}{y_suffix}"},
            trendline="lowess",
            trendline_color_override="green",
            trendline_scope="overall",
            color_discrete_sequence=["rgba(3, 199, 253, 0.5)"],
        )
    fig_trend.add_hline(
        y=splits_df.filter(pl.col("Location") == "Overall")["value"].item(),
        line_dash="dash",
        line_color="red",
        annotation_text="Season Average",
    )

    return fig_trend


def career_metric_chart(
    season_data: pl.DataFrame,
    metric: str,
    metric_name: str,
    with_annotations: bool = True,
):
    """
    Create a line chart showing a metric's progression over multiple seasons.

    Args:
        season_data (pl.DataFrame): Data aggregated by season
        metric (str): Column name for the metric to display
        metric_name (str): Display name for the metric
        with_annotations (bool, optional): Whether to add annotations for games played. Defaults to True.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    # Create the line chart
    fig = px.line(
        season_data,
        x="season",
        y=metric,
        markers=True,
        hover_data=["games_played"] if "games_played" in season_data.columns else None,
        custom_data=["games_played"] if "games_played" in season_data.columns else None,
    )

    fig.update_traces(line_width=3, marker_size=10)
    fig.update_yaxes(title=metric_name)
    fig.update_xaxes(title="Season")

    # Add games played annotations if requested and available
    if with_annotations and "games_played" in season_data.columns:
        for i, row in enumerate(season_data.iter_rows(named=True)):
            fig.add_annotation(
                x=row["season"],
                y=row[metric],
                text=f"GP: {row['games_played']}",
                showarrow=False,
                yshift=15,
                font=dict(size=10),
            )

    return fig


def player_shot_chart(player_season_trend, shot_categories_selected):
    """
    Create a multi-line chart showing shooting statistics over seasons.

    Args:
        player_season_trend (pl.DataFrame): Player shooting data by season
        shot_categories_selected (list): List of shot categories to include

    Returns:
        plotly.graph_objects.Figure: The plotly figure object or None if no data
    """
    # Define shooting stat categories
    shooting_stats = {
        "Field Goals": ["fg_pct", "fgm", "fga"],
        "2-Point Shots": ["two_p_pct", "two_pm", "two_pa"],
        "3-Point Shots": ["three_p_pct", "three_pm", "three_pa"],
        "Free Throws": ["ft_pct", "ftm", "fta"],
    }

    # Define colors for each category
    colors = {
        "Field Goals": ["#E90000", "#FF4D4D", "#FC8282"],  # Red shades
        "2-Point Shots": ["#AD5F00", "#FFA54F", "#FFDAB9"],  # Orange shades
        "3-Point Shots": ["#0000FF", "#4D4DFF", "#9999FF"],  # Blue shades
        "Free Throws": ["#008300", "#4DFF4D", "#99FF99"],  # Green shades
    }

    # Generate data based on selected shooting stat categories
    shooting_stats_data = []
    for category in shot_categories_selected:
        selected_stats = shooting_stats[category]

        for stat in selected_stats:
            # Set appropriate metric name for display
            metric_names = {
                "fg_pct": "FG%",
                "fgm": "FGM",
                "fga": "FGA",
                "two_p_pct": "2P%",
                "two_pm": "2PM",
                "two_pa": "2PA",
                "three_p_pct": "3P%",
                "three_pm": "3PM",
                "three_pa": "3PA",
                "ft_pct": "FT%",
                "ftm": "FTM",
                "fta": "FTA",
            }

            metric_name = metric_names.get(stat, stat.upper())

            # Add data points for this stat
            for row in player_season_trend.iter_rows(named=True):
                shooting_stats_data.append(
                    {
                        "season": row["season"],
                        "value": row[stat],
                        "metric": metric_name,
                        "games_played": row.get("games_played", 0),
                    }
                )

    # Only create visualization if data is available
    if not shooting_stats_data:
        return None

    shooting_stats_df = pl.DataFrame(shooting_stats_data)

    # Create a color sequence for all metrics
    color_sequence = []
    for category in shot_categories_selected:
        color_sequence.extend(colors[category])

    # Create the figure
    fig = px.line(
        shooting_stats_df,
        x="season",
        y="value",
        color="metric",
        markers=True,
        hover_data=["games_played"]
        if "games_played" in shooting_stats_df.columns
        else None,
        labels={
            "season": "Season",
            "value": "Value",
            "metric": "Metric",
            "games_played": "Games Played",
        },
        color_discrete_sequence=color_sequence,
    )

    # Update line thickness and marker size
    fig.update_traces(line_width=2, marker_size=8)

    return fig


def win_percentage_chart(win_pct_data, reference_line=50):
    """
    Create a bar chart showing win percentages by team/location.

    Args:
        win_pct_data (list): List of dictionaries with 'Team' and 'value' keys
        reference_line (float, optional): Value for reference line. Defaults to 50.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if not win_pct_data:
        return None

    # Convert to DataFrame and format percentages
    win_pct_df = pl.DataFrame(win_pct_data)
    if "value" in win_pct_df.columns:
        win_pct_df = win_pct_df.with_columns(pl.col("value").mul(100).round(1))

    # Create win percentage bar chart
    fig = px.bar(
        win_pct_df,
        x="Team",
        y="value",
        text="value",
        color="Team",
        labels={
            "Team": "Location",
            "value": "Win Percentage (%)",
        },
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig.update_traces(texttemplate="%{text:.1f}%")
    fig.add_hline(
        y=reference_line,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"{reference_line}%",
    )

    return fig


def win_percentage_opponent_chart(
    win_pct_data: pl.DataFrame, reference_line: float = 0.5
):
    """
    Create a bar chart showing win percentages by team.

    Args:
        win_pct_data (pl.DataFrame): Data with win percentages by opponent
        reference_line (float, optional): Value for reference line. Defaults to 50.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if win_pct_data.is_empty():
        return None

    # Convert to DataFrame and format percentages
    fig = px.bar(
        win_pct_data,
        x="opponent",
        y="win_pct",
        text="win_pct",
        labels={"opponent": "Opponent", "win_pct": "Win Percentage"},
        color="win_pct",
        color_continuous_scale="RdYlGn",
    )

    fig.update_traces(texttemplate="%{text:.3f}")
    fig.add_hline(
        y=reference_line,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"{reference_line}%",
    )

    return fig


def team_performance_trend_chart(
    season_trend, metric="win_percentage", y_label=None, format_as_percent=False
):
    """
    Create a line chart showing team performance trends over seasons.

    Args:
        season_trend (pl.DataFrame): Team data aggregated by season
        metric (str, optional): Metric to display. Defaults to "win_percentage".
        y_label (str, optional): Y-axis label. Defaults to metric name.
        format_as_percent (bool, optional): Whether to format y-axis as percentage. Defaults to False.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if y_label is None:
        y_label = metric.replace("_", " ").title()

    fig = px.line(
        season_trend,
        x="season",
        y=metric,
        markers=True,
        labels={
            "season": "Season",
            metric: y_label,
        },
    )

    fig.update_traces(line_width=3, marker_size=10)

    if format_as_percent:
        fig.update_layout(yaxis_tickformat=".0%")
        # Add 50% win rate reference line for win percentage
        if metric == "win_percentage":
            fig.add_hline(
                y=0.5,
                line_dash="dash",
                line_color="red",
                annotation_text="50% Win Rate",
            )

    return fig


def opponent_comparison_chart(
    vs_data: pl.DataFrame, metric_columns: list[str], metric_names=None
):
    """
    Create a bar chart comparing metrics against different opponents.

    Args:
        vs_data (pl.DataFrame): Data with stats against different opponents
        metric_columns (list): List of metrics to compare
        metric_names (dict, optional): Mapping of column names to display names. Defaults to None.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if metric_names is None:
        metric_names = {col: col.replace("_", " ").title() for col in metric_columns}

    # Prepare data for visualization
    chart_data = []
    for col in metric_columns:
        for row in vs_data.iter_rows(named=True):
            chart_data.append(
                {
                    "opponent": row["opponent"],
                    "value": row[col],
                    "metric": metric_names.get(col, col),
                    "games_played": row.get("games_played", 0),
                }
            )

    chart_df = pl.DataFrame(chart_data)

    # Create the visualization
    fig = px.bar(
        chart_df,
        x="opponent",
        y="value",
        color="metric",
        barmode="group",
        hover_data=["games_played"] if "games_played" in chart_df.columns else None,
        labels={
            "opponent": "Opponent",
            "value": "Value",
            "metric": "Metric",
            "games_played": "Games Played",
        },
    )

    return fig


def multi_metric_season_chart(
    season_data: pl.DataFrame, metrics: list[str], metric_names=None, colors=None
):
    """
    Create a line chart showing multiple metrics over seasons.

    Args:
        season_data (pl.DataFrame): Data aggregated by season
        metrics (list): List of metric columns to display
        metric_names (dict, optional): Mapping of column names to display names. Defaults to None.
        colors (list, optional): List of colors for each metric. Defaults to None.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if metric_names is None:
        metric_names = {m: m.upper() for m in metrics}

    # Prepare data for visualization
    chart_data = []
    for metric in metrics:
        display_name = metric_names.get(metric, metric.upper())
        for row in season_data.iter_rows(named=True):
            chart_data.append(
                {
                    "season": row["season"],
                    "value": row[metric],
                    "metric": display_name,
                    "games_played": row.get("games_played", 0),
                }
            )

    chart_df = pl.DataFrame(chart_data)

    # Create the visualization
    fig = px.line(
        chart_df,
        x="season",
        y="value",
        color="metric",
        markers=True,
        hover_data=["games_played"] if "games_played" in chart_df.columns else None,
        labels={
            "season": "Season",
            "value": "Value",
            "metric": "Metric",
            "games_played": "Games Played",
        },
        color_discrete_sequence=colors,
    )

    fig.update_traces(line_width=2, marker_size=8)

    return fig


def location_bar_chart(
    data: pl.DataFrame, metric_name: str, y_suffix: str = ""
) -> Figure:
    """
    Create a bar chart comparing metrics across different locations.
    Args:
        data (pl.DataFrame): Data with stats by location
        metric_name (str): Display name for the metric
        y_suffix (str, optional): Suffix for y-axis label. Defaults to "".
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    # Create comparison bar chart
    fig_splits = px.bar(
        data,
        x="Location",
        y="value",
        text="value",
        color="Location",
        labels={
            "Location": "Location",
            "value": f"{metric_name}{y_suffix}",
        },
    )
    # Update bar chart properties
    fig_splits.update_traces(texttemplate="%{text:.1f}" + y_suffix)
    fig_splits.update_layout(
        yaxis_title=f"{metric_name.title()}{y_suffix}",
    )
    return fig_splits


def stat_bar_chart(
    data: pl.DataFrame,
    x_col: str,
    y_col: str | list,
    title: str,
    color_col: Optional[str] = None,
    stack: bool = False,
    labels: Optional[dict] = None,
    colors: Optional[list] = None,
    hover_data: Optional[list] = None,
    custom_hovertemplate: Optional[str] = None,
    **kwargs,
) -> Figure:
    """
    Create a bar chart for a specific statistic.

    Args:
        data (pl.DataFrame): Data to visualize
        x_col (str): Column name for x-axis
        y_col (str or list): Column name(s) for y-axis - can be a string or list of strings
        title (str): Title of the chart
        color_col (str, optional): Column name for color coding. Defaults to None.
        stack (bool, optional): Whether to stack bars for multiple y columns. Defaults to False.
        labels (dict, optional): Custom labels for columns. Defaults to None.
        colors (list, optional): Custom colors for bars. Defaults to None.
        hover_data (list, optional): Additional columns to include in hover data. Defaults to None.
        custom_hovertemplate (str, optional): Custom hover template. Defaults to None.

    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    # Set default labels
    default_labels = {x_col: x_col.replace("_", " ").title()}

    # Handle single column vs multiple columns for y-axis
    if isinstance(y_col, list):
        # For multiple y columns
        barmode = "stack" if stack else "group"

        # Melt the dataframe for multiple columns
        melted_data = data.melt(
            id_vars=[x_col] + (hover_data if hover_data else []),
            value_vars=y_col,
            variable_name="Metric",
            value_name="value",
        )

        # Create figure with melted data
        fig = px.bar(
            melted_data,
            x=x_col,
            y="value",
            color="Metric",
            barmode=barmode,
            text="value",
            title=title,
            color_discrete_sequence=colors,
            hover_data=hover_data,
            **kwargs,
        )

        # Apply custom hover template if provided
        if custom_hovertemplate:
            fig.update_traces(hovertemplate=custom_hovertemplate)
        # Otherwise provide a default simplified hover
        elif not hover_data:
            custom_hovertemplate = (
                "<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<extra></extra>"
            )
            fig.update_traces(hovertemplate=custom_hovertemplate)

        # Apply custom labels to the color/metric legend
        if labels:
            fig.for_each_trace(
                lambda t: t.update(
                    name=labels.get(t.name, t.name),
                    legendgroup=labels.get(t.name, t.name),
                )
            )

    else:
        # For single y column
        default_labels[y_col] = y_col.replace("_", " ").title()

        # Create standard bar chart
        fig = px.bar(
            data,
            x_col,
            y_col,
            color=color_col,
            text=y_col,
            title=title,
            color_discrete_sequence=colors,
            hover_data=hover_data,
            **kwargs,
        )

        # Apply custom hover template if provided
        if custom_hovertemplate:
            fig.update_traces(hovertemplate=custom_hovertemplate)
        # Otherwise provide a default simplified hover
        elif not hover_data:
            custom_hovertemplate = "<b>%{x}</b><br>%{y:.1f}<extra></extra>"
            fig.update_traces(hovertemplate=custom_hovertemplate)

    # Apply labels
    final_labels = default_labels.copy()
    if labels:
        final_labels.update(labels)
    fig.update_layout(xaxis_title=final_labels.get(x_col, x_col), yaxis_title="Value")

    # Format text labels
    fig.update_traces(texttemplate="%{text:.1f}")

    return fig
