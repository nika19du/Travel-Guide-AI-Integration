from typing import List, Literal

from pydantic import  BaseModel, Field

class IntentAnalysis(BaseModel):
    prompt: str = Field(
        description="The complete factual question to answer."
    )
    format: Literal["text", "image", "audio"] = Field(
        description="Requested output format."
    )

class TravelGuideItem(BaseModel):
    title: str = Field(
        description = (
            "Short title of the retrieved recommendation, place, "
            "period, transport option, accommodation, or other result."
        )
    )

    description: str = Field(
        description= (
            "Factual description based only on the retrieved context."
        )
    )

class DestinationTravelAnswer(BaseModel):
    destination: str = Field(
        description=(
            "The unique destination described by this answer. "
            "There must be only one answer object per destination."
        )
    )

    summary: str = Field(
        description=(
            "A complete direct answer to the user's question for this "
            "destination. Combine all relevant aspects in one summary."
        )
    )

    items: List[TravelGuideItem] = Field(
        default_factory=list,
        description=(
            "All relevant facts for this destination. For example, if the "
            "source provides both the best and cheapest travel periods, "
            "include both as separate items inside this single destination "
            "object instead of creating duplicate destination objects."
        )
    )

    source_files: List[str] = Field(
        description="PDF filenames that directly support the answer."
    )

    source_pages: List[int] = Field(
        description=(
            "Only the page numbers that directly support the answer."
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
    destinations: List[DestinationTravelAnswer] =  Field(
        description=(
            "One answer object per unique destination. "
            "Never create multiple objects for the same destination. "
            "Combine all relevant information for a destination into "
            "a single object and place the individual facts in items."
        )
    )

class AskAIResult(BaseModel):
    intent: IntentAnalysis
    answer: TravelGuideAnswer