  Encontrar receitas usando apenas os ingredientes que temos em casa costuma ser limitado e literal: sistemas tradicionais só buscam palavras-chave.
O SmartCook resolve isso com busca semântica, permitindo que o usuário descreva seus ingredientes em linguagem natural e receba recomendações relevantes e explicadas, como faria um chef humano.

**Pipeline técnico:**

1. **PostgreSQL**  
   - Base relacional das receitas (ingredientes, calorias, tipo de cozinha)  
   - Fonte única de verdade para dados estruturados  

2. **Sentence Transformers**  
   - Criação de embeddings das receitas  
   - Normalização para busca por similaridade (cosine similarity)  

3. **Neo4j**  
   - Armazena embeddings como nós no grafo  
   - Permite **busca vetorial eficiente** diretamente no grafo  

4. **RAG (Retrieval-Augmented Generation)**  
   - Recupera receitas semanticamente próximas  
   - Injeta contexto real no prompt antes da geração pelo LLM  

5. **Gemini (LLM)**  
   - Recomenda a melhor receita para os ingredientes do usuário  
   - Explica o motivo da escolha  
   - Sugere variações personalizadas
  
**Demonstração:**

![Descrição da imagem 1](image1.png)
![Descrição da imagem 2](image2.png)
![Descrição da imagem 3](image3.png)
![Descrição da imagem 4](image4.png)
