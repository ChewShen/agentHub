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