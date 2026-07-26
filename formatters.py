from models import TravelGuideAnswer

def format_travel_answer_as_markdown(
    answer: TravelGuideAnswer
) -> str:
    lines = ["# Answer"]

    for destination in answer.destinations:
        lines.append(f"\n## {destination.destination}")

        lines.append("\n### Best time")

        if destination.best_periods:
            for period in destination.best_periods:
                lines.append(
                    f"- **{period.purpose}:** {period.period}"
                )
        else:
            lines.append("- No information found.")

        lines.append("\n### Cheapest time")

        if destination.cheapest_periods:
            for period in destination.cheapest_periods:
                lines.append(
                    f"- **{period.purpose}:** {period.period}"
                )
        else:
            lines.append("- No information found.")

        if destination.source_files:
            sources = ", ".join(destination.source_files)
            lines.append(f"\n**Sources:** {sources}")

        if destination.source_pages:
            pages = ", ".join(
                str(page)
                for page in destination.source_pages
            )
            lines.append(f"**Pages:** {pages}")

        if destination.missing_information:
            lines.append("\n### Missing information")

            for item in destination.missing_information:
                lines.append(f"- {item}")

    return "\n".join(lines)