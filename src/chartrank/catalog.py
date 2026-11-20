"""Chart catalog.

Declarative table mapping (plot type of x, plot type of y, intent) to the
candidate charts, in the specification's order (section 6.2): the first one is
the default recommendation (★). Adding a chart means adding a word to a list,
not writing a new ``if``.
"""

#: Intents accepted by ``suggest()`` and ``recommend()`` (EF-20).
INTENTS = ("distribution", "compare", "relationship", "composition", "trend")

#: A discrete column with at most this many distinct values is drawn as a
#: category (decision of 16 Nov 2026, e.g. Pclass with 3 values).
DISCRETE_AS_CATEGORY_MAX = 10

#: Semantic type (from the profiler) -> plot type (how to draw it).
#: ``None`` means the column is never drawn (identifiers, free text...).
_PLOT_TYPES: dict[str, str | None] = {
    "continuous": "numeric",
    "category": "category",
    "ordinal": "category",  # keeps its natural order when drawn
    "high_cardinality": "category",  # the top N rule applies later
    "boolean": "boolean",
    "date": "date",
    "id": None,
    "text": None,
    "empty": None,
    "constant": None,
}

_CAT_CAT = ("grouped_bar", "stacked_bar_100", "count_heatmap")

#: (plot type of x, plot type of y, intent) -> candidate chart kinds, ★ first.
CATALOG: dict[tuple[str, str, str], tuple[str, ...]] = {
    ("category", "numeric", "compare"): ("box", "violin", "bar_median", "strip"),
    ("category", "numeric", "distribution"): ("histogram_overlay", "density_by_group"),
    ("numeric", "numeric", "relationship"): ("scatter", "hexbin", "scatter_trend"),
    ("category", "category", "compare"): _CAT_CAT,
    ("category", "category", "composition"): _CAT_CAT,
    ("date", "numeric", "trend"): ("line", "line_rolling", "area"),
    ("date", "category", "composition"): ("stacked_area_100", "stacked_bar_period"),
    ("numeric", "boolean", "compare"): (
        "box_by_class",
        "histogram_overlay",
        "rate_by_bin",
    ),
}


def plot_type(semantic_type: str, n_distinct: int) -> str | None:
    """Turn a semantic type into a plot type.

    Args:
        semantic_type: Type detected by the profiler (e.g. ``"discrete"``).
        n_distinct: Number of distinct values of the column.

    Returns:
        ``"numeric"``, ``"category"``, ``"boolean"``, ``"date"``, or ``None``
        if the column cannot be drawn.

    Example:
        >>> plot_type("discrete", 3), plot_type("discrete", 15)
        ('category', 'numeric')
    """
    if semantic_type == "discrete":
        return "category" if n_distinct <= DISCRETE_AS_CATEGORY_MAX else "numeric"
    return _PLOT_TYPES[semantic_type]


def candidates(type_x: str, type_y: str, intent: str) -> tuple[str, ...]:
    """Return the candidate chart kinds, ★ first, or ``()`` if none.

    A boolean that has no row of its own is drawn as a category with two
    values (e.g. Survived vs Fare uses the category vs numeric charts).
    """
    for tx, ty in ((type_x, type_y), (_as_category(type_x), _as_category(type_y))):
        kinds = CATALOG.get((tx, ty, intent))
        if kinds:
            return kinds
    return ()


def possible_intents(type_x: str, type_y: str) -> list[str]:
    """List the intents that have at least one chart for these plot types."""
    return [intent for intent in INTENTS if candidates(type_x, type_y, intent)]


def _as_category(plot_type: str) -> str:
    """Replace "boolean" by "category" (the fallback used by ``candidates``)."""
    return "category" if plot_type == "boolean" else plot_type
