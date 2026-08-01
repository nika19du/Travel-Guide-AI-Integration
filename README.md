# Tour Guide AI

An AI-powered travel assistant built in **Google Colab** that answers travel questions using **Retrieval-Augmented Generation (RAG)** over indexed PDF travel guides. The assistant supports text responses, AI-generated travel images, and narrated audio travel guides.

---

## Features

- PDF ingestion and indexing
- Retrieval-Augmented Generation (RAG)
- OpenAI Responses API
- Tool calling
- Structured outputs with Pydantic
- Travel-specific intent detection
- Image generation with Gemini
- Audio generation with ElevenLabs
- Source attribution (PDF files and page numbers)
- Automatic normalization of duplicate destinations

---

## Technologies

| Technology | Purpose |
|------------|---------|
| Python | Application |
| Google Colab | Development environment |
| OpenAI Responses API | Intent detection, tool calling and RAG orchestration |
| ChromaDB | Vector database |
| Pydantic | Structured outputs |
| Gemini | Image generation |
| ElevenLabs | Text-to-speech |
| PyMuPDF | PDF processing |
| Rich | Console output |

---

## Notebook Structure

The entire application is implemented in a single Google Colab notebook and is organised into the following sections:

1. Installation
2. Imports
3. API Clients
4. Data Models
5. PDF Processing
6. Vector Store
7. Tool Definitions
8. System Prompts
9. Shared Retrieval Utilities
10. Retrieval Strategies
    - CAG-style retrieval
    - Tool-based RAG
11. AI Orchestration
12. Image Generation
13. Audio Generation
14. Wrapper Functions
15. Console Output
16. Retrieval Strategy Comparison
17. Test Cases

---

## Workflow

The assistant first analyses the user request and extracts:

- the factual question that should be answered from the PDF guides;
- the requested output format: text, image, or audio.

The application uses tool-based RAG as its default retrieval strategy.

```text
User Question
      │
      ▼
Intent Analysis
(OpenAI Structured Output)
      │
      ├── Extracted travel question
      └── Requested format
            text / image / audio
      │
      ▼
Retrieval Strategy
      │
      ├── CAG-style retrieval
      │     ChromaDB search
      │          │
      │          ▼
      │     Fixed retrieved context
      │
      └── Tool-based RAG (default)
            OpenAI tool calling
                  │
                  ▼
            One or more ChromaDB searches
      │
      ▼
Structured TravelGuideAnswer
      │
      ▼
Answer Normalization
      │
      ├── Remove synthetic destinations
      ├── Merge duplicate destinations
      └── Remove duplicate information
      │
      ▼
Output Generation
      │
      ├── Text response
      ├── Gemini travel image
      └── ElevenLabs audio narration
      │
      ▼
Colab Output
```

---

## Retrieval Strategies

### CAG-Style Retrieval

The CAG-style strategy performs semantic search before calling the language model. A fixed set of relevant PDF chunks is retrieved from ChromaDB and passed directly to the model as context.

This approach is:

- simple;
- concise;
- predictable;
- based on a fixed retrieved context.

### Tool-Based RAG

The tool-based RAG strategy allows the language model to call the travel-guide search tool and decide:

- which destination to search;
- which semantic query to use;
- how many searches are needed;
- whether separate searches are required for comparisons.

This approach is:

- more flexible;
- capable of retrieving broader information;
- suitable for multi-destination comparisons;
- potentially more verbose than the CAG-style approach.

Tool-based RAG is the default strategy used by the public `ask_ai()` and `retrieve_information()` functions.

---

## CAG vs Tool-Based RAG

The CAG-style approach retrieves a fixed set of relevant chunks before calling the language model. This usually produces a concise and predictable answer.

The tool-based RAG approach allows the model to decide which searches to perform. In the public-transport comparison example, it retrieved additional information about airport transport, taxis, and car rental.

Neither strategy is always better:

| Strategy | Advantages | Trade-offs |
|---|---|---|
| CAG-style retrieval | Simpler, concise, predictable | Limited to the initially retrieved context |
| Tool-based RAG | Flexible, broader retrieval, supports comparisons | More API steps and potentially more verbose output |

---

## Public Functions

The required project functions keep the signatures defined in the assignment:

```python
def retrieve_information(prompt: str) -> str:
    ...
```

```python
def ask_ai(question: str) -> AskAIResult:
    ...
```

Both functions use tool-based RAG by default.

A separate internal function allows the two retrieval strategies to be tested and compared:

```python
retrieve_information_by_strategy(
    prompt=question,
    vector_store=vector_store,
    strategy="cag"
)
```

```python
retrieve_information_by_strategy(
    prompt=question,
    vector_store=vector_store,
    strategy="rag"
)
```
---

## Example Questions

### Text

```text
What are the top attractions in Prague?
```

```text
When is the best time to visit Malaga?
```

### Image

```text
Generate a realistic travel poster of Malaga.
```

```text
Create an image of the beaches in Malaga.
```

### Audio

```text
Create an audio travel guide for Malaga.
```

```text
Tell me about Malaga public transport as audio.
```

---

## Supported Destinations

- Prague
- Malaga

---

## References

| Resource | Purpose |
|----------|---------|
| https://platform.openai.com/ | OpenAI Responses API |
| https://platform.openai.com/docs | OpenAI Documentation |
| https://ai.google.dev/gemini-api/docs | Gemini API |
| https://elevenlabs.io/docs | ElevenLabs |
| https://docs.trychroma.com/ | ChromaDB |

