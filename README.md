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

The entire application is implemented in a single **Google Colab notebook** and is organised into the following sections:

1. Installation
2. Imports
3. OpenAI Client
4. Data Models
5. PDF Processing
6. Vector Store
7. Tool Definitions
8. System Prompts
9. RAG Service
10. Image Generation
11. Audio Generation
12. Wrapper Functions
13. Console Output
14. Test Cases

---

## Workflow

```text
User Question
      │
      ▼
Intent Analysis
(OpenAI Responses API)
      │
      ▼
Prompt Extraction
      │
      ▼
RAG Retrieval
(ChromaDB + Tool Calling)
      │
      ▼
Structured TravelGuideAnswer
      │
      ▼
Answer Normalization
      │
      ▼
Generate:
• Text
• Image
• Audio
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
