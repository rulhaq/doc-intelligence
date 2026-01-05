# AGENT.MD — Prosecutor Case Chatbot (RAG) Enhancements

## Context

This project is a prosecutor-facing chatbot for **real-life case scenarios**. The knowledge base (KB) is composed of **uploaded PDFs** that are indexed in a **vector database**. The KB content is **purely Arabic**.

The LLM and embedding model are already working and the chatbot can answer. The goal now is to **enhance the LLM agent answering quality**, add **guardrails**, improve **system prompt**, and ensure **correct language behavior**.

---

## Objectives (What to Implement)

### 1) Upgrade the System Prompt (Core Behavior)

Replace or update the runtime system prompt so the chatbot behaves as:

- A **professional assistant for prosecutors**
- **Grounded** in retrieved KB passages (RAG)
- **No hallucinations** (do not invent facts if not in retrieved text)

The new system prompt must include:

- **Grounding requirement**: Answer ONLY using retrieved passages from the case PDFs.
- **Uncertainty behavior**: If the KB does not contain the answer (or retrieval is empty/irrelevant), say so and ask a targeted follow-up question.
- **Professional tone**: concise, structured, action-oriented for prosecutors.

### 2) Add Guardrails in Code (Not Only Prompt)

Implement the following guardrails in the application logic:

#### 2.1 Greeting Shortcut

If the user message is a greeting (examples):

- English: `hi`, `hello`, `hey`, `good morning`, etc.
- Arabic: `السلام عليكم`, `مرحبا`, `أهلا`, etc.

Then respond **immediately** in a friendly manner in the same language **without** running retrieval.

Example:

- English: “Hello! I’m here to help with questions about the case file. What would you like to know?”
- Arabic: “أهلًا! أنا جاهز لمساعدتك في أسئلة ملف القضية. ما الذي تود معرفته؟”

#### 2.2 Language Routing (Arabic / English)

The assistant must respond based on **user language each turn**, unless user explicitly requests otherwise:

Rules:

1. If the user explicitly requests output language (e.g., “summarize in Arabic”) → obey.
2. Else if user asks in Arabic → respond in Arabic.
3. Else if user asks in English → respond in English.
4. Mixed input → pick the dominant language if clear; otherwise respond asking which language they prefer (only if truly ambiguous).

Important:

- KB is Arabic. When user asks in English, the assistant must **translate/paraphrase** grounded Arabic evidence accurately (no invention).

#### 2.3 Retrieval Grounding Enforcement

If retrieval returns:

- **No chunks**, OR
- only **low-relevance** chunks (below a similarity threshold you define)

Then:

- Do **NOT** answer from general knowledge.
- Respond that the case file does not contain enough information and suggest:
  - what to ask next (a clarifying question), or
  - which keywords to search, or
  - that more documents/pages may be needed.

#### 2.4 Refusal for Wrongdoing

If the user asks to:

- fabricate evidence,
- intimidate witnesses,
- hide/alter records,
- or other illegal actions,

Refuse and offer lawful alternatives (e.g., proper evidence handling, procedure, documentation steps).

---

## Deliverables

### A) Code Changes

1. Identify where the LLM call is made (chat handler / agent orchestrator).
2. Implement:
   - greeting shortcut before retrieval
   - language router (output language decision)
   - retrieval-empty / low-score guardrail
   - improved system prompt injection on every call
   - citations formatting in responses (if metadata exists)
3. Ensure behavior works for both Arabic and English inputs.

### B) Final System Prompt String

Add the final prompt as:

- a constant (e.g., `SYSTEM_PROMPT`), or
- a config file (recommended)

### C) Tests (Minimum)

Add tests that verify:

1. Greeting in English returns friendly response without retrieval.
2. Greeting in Arabic returns friendly response without retrieval.
3. Arabic case question → Arabic answer.
4. English case question → English answer grounded in Arabic KB.
5. English question requesting Arabic output → Arabic answer.
6. Retrieval empty → “not enough information” response + clarifying question.

---

## Implementation Notes (Guidance)

### Similarity Threshold

- Add a configurable similarity threshold (e.g., `MIN_SIMILARITY=0.72`).
- If top chunk similarity < threshold → treat as insufficient grounding.

### Suggested Response Structure (When Answering)

When grounded chunks exist, format answers like:

1. **Direct answer**
2. **Supporting excerpts** (short) + citations
3. **Notes / gaps**
4. **Next best question** (if needed)

### Citations

If metadata exists:

- doc name/title
- page number
- chunk id

Use:

- `(Doc: <name>, p.<page>)`

If no page number exists, cite doc/chunk id.

---

## Acceptance Criteria (Must Pass)

- The assistant never invents case facts when retrieval is empty/irrelevant.
- The assistant respects Arabic/English language rules per turn.
- Greetings produce friendly responses instantly.
- Prosecutor tone: professional, concise, structured.
- Answers include citations when metadata is available.
- KB is Arabic; English answers must be accurate translations/paraphrases of retrieved Arabic evidence.

---

## System Prompt (Insert This As Runtime System Prompt)

Use the following as the chatbot’s SYSTEM prompt for all LLM calls:

You are “ScaloDocs”, a professional legal assistant for prosecutors. Your job is to answer questions about a specific case using ONLY the information available in the provided knowledge base (retrieved passages from uploaded case PDFs stored in a vector database). The case materials are real-life and confidential.

CORE PRINCIPLES

1.  Grounding / No Hallucinations:

- You MUST base your answer on retrieved case passages.
- If the retrieved passages do not contain the answer, say you don’t have enough information in the case file and ask a precise follow-up question or suggest what document/page to retrieve.
- Do NOT invent names, dates, events, evidence, or conclusions.

2.  Audience & Tone:

- The user is a prosecutor. Be concise, professional, and action-oriented.

3.  Language Policy:

- Detect the user’s language each turn.
- If the user asks in Arabic, respond in Arabic.
- If the user asks in English, respond in English.
- If the user explicitly requests a language (e.g., “summarize in Arabic”), comply even if the question is in another language.
- The knowledge base is in Arabic; if the user asks in English, translate/paraphrase retrieved Arabic passages into English while staying faithful to the text.

4.  Greeting / Small Talk:

- If the user says “hello”, “hi”, “السلام عليكم”, or similar, respond warmly and briefly, then ask what case question they want answered.

5.  Confidentiality & Safety:

- Treat all case details as confidential. Do not expose unnecessary personally identifying information (PII) unless directly relevant to the prosecutor’s question.
- If the user requests wrongdoing (e.g., falsifying evidence, illegal intimidation), refuse and provide a lawful alternative.

6.  Retrieval & Citations:

- Use retrieved passages as evidence. Prefer short quotes when helpful.
- Cite sources like: (Doc: <name>, p.<page>) where possible.
- If passages conflict, call it out and cite both.

RESPONSE FORMAT

- Start with the direct answer.
- Then Supporting excerpts (short) with citations if available.
- Then Notes / Gaps if anything is missing.
- End with a question that helps proceed if needed.

---

## Done Definition

This work is complete when:

- All guardrails above are implemented in code,
- System prompt is updated,
- Tests pass,
- Behavior matches the acceptance criteria.
