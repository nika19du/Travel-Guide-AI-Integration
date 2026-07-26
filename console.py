from rich.console import Console
from rich.table import Table

from models import TravelGuideAnswer
# Pretty console output using Rich.
console = Console(force_terminal=True, color_system="truecolor")

def print_travel_answer(
    answer: TravelGuideAnswer
) -> None:

    table = Table(title="Travel Period Comparison")

    table.add_column(
        "Destination",
        style="cyan",
        no_wrap=True
    )
    table.add_column(
        "Category",
        style="green"
    )
    table.add_column(
        "Purpose",
        style="magenta"
    )
    table.add_column(
        "Recommended period",
        style="yellow",
        min_width=30
    )

    for index, destination in enumerate(answer.destinations):

        first_row = True

        for period in destination.best_periods:

            table.add_row(
                destination.destination if first_row else "",
                "Best",
                period.purpose.capitalize(),
                period.period
            )

            first_row = False

        for period in destination.cheapest_periods:

            table.add_row(
                "" if not first_row else destination.destination,
                "Cheapest",
                period.purpose.capitalize(),
                period.period
            )

            first_row = False

        # Divider between destinations
        if index < len(answer.destinations) - 1:
            table.add_section()

    console.print(table)

    # ------------------------
    # Sources
    # ------------------------

    sources = Table(title="Sources")

    sources.add_column(
        "Destination",
        style="cyan",
        no_wrap=True
    )

    sources.add_column(
        "Source",
        style="green"
    )

    sources.add_column(
        "Pages",
        style="yellow"
    )

    for destination in answer.destinations:

        sources.add_row(
            destination.destination,
            ", ".join(destination.source_files),
            ", ".join(map(str, destination.source_pages))
        )

    console.print()
    console.print(sources)

    # ------------------------
    # Missing information
    # ------------------------

    has_missing = any(
        destination.missing_information
        for destination in answer.destinations
    )

    if has_missing:

        console.print()

        missing = Table(title="Missing Information")

        missing.add_column(
            "Destination",
            style="cyan"
        )

        missing.add_column(
            "Missing",
            style="red"
        )

        for destination in answer.destinations:

            if destination.missing_information:

                missing.add_row(
                    destination.destination,
                    ", ".join(destination.missing_information)
                )

        console.print(missing)

    console.print()

    console.print(
        f"[bold green]Destinations analysed:[/bold green] "
        f"{len(answer.destinations)}"
    )