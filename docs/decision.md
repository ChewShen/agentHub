## V0 — Foundation
1. What is built
- For this v0, is just scaffolding, foundation setup and the dcoker for containerize setup. No feature is built yet.
- By doing `curl http://localhost:8000/health`, the status of the server can be check on

2. Why all the services?
- The services like postgreSQL and Qdrant are planned to be add on in future, its added now is to laid the foundation so it wont messed up during the future implementation. Since it was planned, why not just add it if can.

3. Trade-Off
- There are no fancy folder yet is to minimise and reduce the complexity of the project. Too many unused folder will often lead to messy implementation and the losing track of the actual progress/milestone.