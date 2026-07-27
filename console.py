from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models import AskAIResult, TravelGuideAnswer


console = Console()


def print_comparison_table(
    answer: TravelGuideAnswer
) -> None:
    """
    Prints a compact comparison table when two or more
    destinations are included in the answer.
    """

    if len(answer.destinations) < 2:
        return

    table = Table(
        title="Travel Comparison",
        title_style="bold cyan",
        header_style="bold",
        show_header=True,
        show_lines=True,
        expand=True,
        padding=(0, 1),
    )

    table.add_column(
        "Destination",
        style="bold cyan",
        no_wrap=True,
        min_width=12,
        max_width=18,
    )

    table.add_column(
        "Category",
        style="bold",
        min_width=18,
        ratio=1,
    )

    table.add_column(
        "Recommendation",
        ratio=3,
    )

    for destination in answer.destinations:
        if destination.items:
            first_item = True

            for item in destination.items:
                table.add_row(
                    (
                        destination.destination
                        if first_item
                        else ""
                    ),
                    item.title,
                    item.description,
                )

                first_item = False
        else:
            table.add_row(
                destination.destination,
                "Summary",
                destination.summary,
            )

    console.print()
    console.print(table)
    console.print()


def print_destination_details(
    answer: TravelGuideAnswer
) -> None:
    """
    Prints detailed information for every destination.
    """

    for destination in answer.destinations:
        console.rule(
            f"[bold cyan]{destination.destination}[/bold cyan]"
        )

        console.print()

        summary_panel = Panel(
            destination.summary,
            title="Summary",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        )

        console.print(summary_panel)

        if destination.items:
            console.print()

            information_table = Table(
                header_style="bold",
                show_header=True,
                show_lines=False,
                expand=True,
                padding=(0, 1),
                box=None,
            )

            information_table.add_column(
                "Category",
                style="bold cyan",
                min_width=20,
                max_width=28,
            )

            information_table.add_column(
                "Details",
                ratio=3,
            )

            for item in destination.items:
                information_table.add_row(
                    item.title,
                    item.description,
                )

            console.print(information_table)

        if destination.missing_information:
            console.print()

            missing_text = Text()

            for index, missing_item in enumerate(
                destination.missing_information,
                start=1,
            ):
                missing_text.append(
                    f"{index}. ",
                    style="bold yellow",
                )
                missing_text.append(
                    f"{missing_item}\n"
                )

            console.print(
                Panel(
                    missing_text,
                    title="Missing Information",
                    title_align="left",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )

        console.print()


def print_sources(
    answer: TravelGuideAnswer
) -> None:
    """
    Prints source files and pages used for each
    destination.
    """

    destinations_with_sources = [
        destination
        for destination in answer.destinations
        if (
            destination.source_files
            or destination.source_pages
        )
    ]

    if not destinations_with_sources:
        return

    console.rule("[bold]Sources[/bold]")
    console.print()

    sources_table = Table(
        show_header=True,
        header_style="bold",
        show_lines=False,
        box=None,
        padding=(0, 1),
    )

    sources_table.add_column(
        "Destination",
        style="bold cyan",
        no_wrap=True,
        min_width=12,
    )

    sources_table.add_column(
        "Source file",
        min_width=24,
    )

    sources_table.add_column(
        "Pages",
        justify="right",
        no_wrap=True,
    )

    for destination in destinations_with_sources:
        source_files = ", ".join(
            destination.source_files
        )

        source_pages = ", ".join(
            str(page)
            for page in destination.source_pages
        )

        sources_table.add_row(
            destination.destination,
            source_files or "-",
            source_pages or "-",
        )

    console.print(sources_table)


def print_result_summary(
    answer: TravelGuideAnswer
) -> None:
    """
    Prints a compact footer with result statistics.
    """

    destination_count = len(answer.destinations)

    label = (
        "destination"
        if destination_count == 1
        else "destinations"
    )

    console.print()
    console.print(
        Text.assemble(
            ("Analysed ", "dim"),
            (
                str(destination_count),
                "bold cyan",
            ),
            (
                f" {label}",
                "dim",
            ),
        )
    )


def print_travel_answer(
    answer: TravelGuideAnswer
) -> None:
    if not answer.destinations:
        console.print(
            Panel(
                "No destination information was found.",
                border_style="yellow",
            )
        )
        return

    is_comparison = len(answer.destinations) >= 2

    if is_comparison:
        print_comparison_table(answer)
    else:
        print_destination_details(answer)

    print_sources(answer)
    print_result_summary(answer)


def print_ai_result(
    result: AskAIResult
) -> None:
    """
    Prints the AI result according to the requested
    output format.
    """

    requested_format = result.intent.format.strip().lower()

    if requested_format == "text":
        print_travel_answer(result.answer)
        return

    if requested_format == "audio":
        console.print(
            Panel(
                "Audio output is not implemented yet.",
                border_style="yellow",
            )
        )
        return

    if requested_format == "image":
        console.print(
            Panel(
                "Image output is not implemented yet.",
                border_style="yellow",
            )
        )
        return

    console.print(
        Panel(
            (
                "Unsupported output format: "
                f"{requested_format}"
            ),
            border_style="yellow",
        )
    )