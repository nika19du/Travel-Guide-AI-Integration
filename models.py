from typing import List, Literal

from pydantic import  BaseModel, Field

class IntentAnalysis(BaseModel):
    prompt: str = Field(
        description="The complete factual question to answer."
    )
    format: Literal['text', 'image', 'audio'] = Field(
        description="Requested output format."
    )

class TravelPeriod(BaseModel):
    purpose: str = Field(
        description=(
            "The exact reason or travel purpose stated in the source, "
            "such as best weather, beach life, sightseeing, fair prices, "
            "cheaper shoulder-season options, or most economical period. "
            "Do not invent or reuse a category from another destination."
        )
    )

    period: str = Field(
        description=(
            "The complete grouped period as stated in the source. "
            "Preserve ranges and alternatives in one string, for example "
            "'May to September, especially June and September', "
            "'June or September', or 'March or October'."
        )
    )

class DestinationTravelAnswer(BaseModel):
    destination: str = Field(
        description="The destination described by this answer."
    )
    best_periods: List[TravelPeriod] = Field(
        description=(
            "Periods explicitly presented as best times to visit, "
            "preserving complete ranges and purposes."
        )
    )

    cheapest_periods: List[TravelPeriod] = Field(
        description=(
            "Periods explicitly related to lower prices, fair prices, "
            "cheaper shoulder-season options, or the most economical time. "
            "Preserve the distinction between these price categories."
        )
    )

    source_files: List[str] = Field(
        description="PDF filenames that directly support the answer."
    )
    source_pages: List[int] = Field(
        description=(
            "Only the page numbers that directly support the returned periods."
        )
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description=(
            "Information requested by the user but not explicitly available "
            "in the retrieved context."
        )
    )

class TravelGuideAnswer(BaseModel):
    destinations: List[DestinationTravelAnswer]

class AskAIResult(BaseModel):
    intent: IntentAnalysis
    answer: TravelGuideAnswer