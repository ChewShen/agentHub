## V0 — Foundation
1. What is built
- For this v0, is just scaffolding, foundation setup and the dcoker for containerize setup. No feature is built yet.
- By doing `curl http://localhost:8000/health`, the status of the server can be check on

2. Why all the services?
- The services like postgreSQL and Qdrant are planned to be add on in future, its added now is to laid the foundation so it wont messed up during the future implementation. Since it was planned, why not just add it if can.

3. Trade-Off
- There are no fancy folder yet is to minimise and reduce the complexity of the project. Too many unused folder will often lead to messy implementation and the losing track of the actual progress/milestone.

## V1 — AI Chat
1. What is built
- Added Gemini API endpoint, can make some communication between user and gemini. Using the model `gemini-3.1-flash-lite`

2. Why Gemini and why this version?
- Why choose Gemini can be look through 2 perspective, budget and limitation. 
- From budget, out of many other more reputable company, as OpenAI and Anthropic does not provide free tier, Groq itself is fast but suitable for this project as it have a super small context window and can only process pure text compare to Gemini's multimodal.
- From technical perspective, Gemini have a large context window and better integration and image handling that can be done through the api directly so we dont need to extract the text from the image before processing.

3. Trade-Offs & Tech Debt
- Free tier API itself is a trade off as there are hard rate limit per minute/day.
- While everything is too depending on Google/Gemini itself, if the API somehow out of service, then the whole project is stalled.

4. What happend if you skip this version?
- The whole RAG/process cannot be continue as there is no service to handle all the input and output and processing itself, it losses the point.

## V2 — AI Reads One Document
1. What is built/added
- a upload file feature/endpoint is added through `localhost:8000/documents/upload`, and a context for the llm to answer only the content in the context using the document uploaded.
  
2. Why uploading whole one document instead of separating it out?
- The purpose for this version are just for single small pdf file upload. No chunking the context yet at this point.

3. Trade-off
- At this point, the api itself does not have the capability to process large amount of data accurately due to its context window, chucking the context out or put them into smaller piece which specific task that the LLMs itself can refer to is the point of the whole RAG.
  
4. What happend if you skip this version?
- Files cannot be upload for the LLM to read/refering/grounding to, making a higher chance of hallucination and losses the point of the whole RAG project.

## V3 -  Chunking
1. What is built/added
- Chucking is added. Chunking is a way to separate a file, depending on the chunking size to let the separate chunk can be store in the vector database. So if a large text can be chunked down to some specific part, and when question or propmt is asked, it try to get the best possible match of the vector for both question and from the chunked document at database to provide the specific answer according to the question so it does not waste resources to scan the full documents every time.

2. Why split the upload and chat into two separate endpoints?
- In V2, uploading the file and asking a question happened in one single request. In V3, we split them so that a document is uploaded and chunked *once* (Phase 1), and then you can ask as many questions as you want using the `document_id` (Phase 2). This prevents having to re-upload the same heavy PDF every time you want to ask a follow-up question.
   
3. Trade-off
- Since the message and the document upload is now separate, now we will have 2 api call and frontend need to fetch the data from the database first then handle the message, which may introduce latency and more bugs.
- We have different since of chunk as we are not hard cutting them, instead separate them using paragraph or natural boundary, which may affect how we score them later
 
4. What happend if you skip this version?
- It will become back to the normal chatbot style as you need to reupload the document everytime if you wanted to ask the same topic from the same document.

## V4 - Embeddings & Semantic Retrieval
1. What is built/added
- Embedding is added to save the resources by matching the highest score from the chunk saved at database. Only the top score that are matched are used for the llm as grounding/reasoning to the specific question, so it wont scan the whole document again after each question is asked.

2. Why did we switch the /chat endpoint from returning a streaming text response (like ChatGPT) to returning a structured JSON response?
- We used json response because json respond provide a better structer and cleaner format, in the cost of UX, while it can be solve by retrieving the key and it value in the future.
  
3. Why did we make the top_k value (the number of chunks retrieved) a configurable parameter in the request body, instead of just hardcoding it to always fetch 5 chunks?
- Making it configurable does not really bring any down side as just it basically just change from hardcoded to a input format. It also bring a benefit of the ease when we wanted to change the value incase in future if there is larger file is being uploaded and more chunk size and we need more reference for better accuracy in future.

4. Trade off/ Tech debt
- By doing so, that mean the api always fetch all the chunk available in the database. Which mean if there are 10000 of chunk, it read and compare all before moving to give any respond, which lead to heavy usage of RAM and in increasing of run time which is a nightmare.
- The current version does not really remember any conversation so continous conversation is not possible yet. (Will be solve in future).
- Before V4, debugging was easy because every chunk was used. Now, if the LLM gives a wrong answer, we have to figure out whether the retrieval picked the wrong chunks or the LLM misinterpreted the right chunks.

5. What happend if this version is skipped?
- If this version is skipped, thats mean no embedding is available. That will lead to the conversation/message is now heavily rely on keyword instead of matching "vibe". This may and will decrease the accuracy of the result, which lose the whole point of the RAG again.