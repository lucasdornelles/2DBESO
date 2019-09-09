#### 2DBESO


Ferramenta de otimização topológica utilizando os métodos de otimização estrutural evolucionária softkill (ESO softkill) e otimização estrutural evolucionária bidirecional softkill (BESO softkill) para a minimização da energia de deformação de estruturas estáticas no estado plano de tensões com restrição de volume. A ferramenta foi desenvolvida utilizando a linguagem computacional python e dividida em diversos módulos responsáveis pela definição das funções referentes as metodologias e funcionalidades implementadas. Foi implementada também, compatibilidade com malhas geradas pelo programa open-source Gmsh e um modelo de malha em txt foi desenvolvido para dar mais versatilidade a ferramenta.


##### Dependencias

Ultima versão verificada dos pacotes do qual o aplicativo é dependente:

* scipy 1.0.1
* numpy 1.14.2
* matplotlib 2.2.2
* scikit-umfpack 0.3.1
* tqdm 4.25.0


##### Utilization

Para utilizar a ferramenta é necessário possuir um interpretador de python instalado com as bibliotecas apresentadas na seção anterior.

Dois arquivos são necessários para a execução do programa, um arquivo de malha em “.msh” ou “.txt” e um arquivo de parâmetros do problema em “.txt”. Para iniciar o programa executa-se o arquivo “main.py” e selecionasse os arquivos de malha e parâmetros do problema quando pedido pelo programa. Apos terminado o processo de otimização os resultados podem ser encontrados na pasta “results” em uma pasta nomeada pela data e hora da execução do programa.
 
A definição das condições de contorno e parâmetros do programa são realizadas em um arquivo de texto de acordo com o modelo encontrado na pasta “models” distribuída junto com o programa. Todos os parâmetros precisam ser definidos, a falta de um parâmetro no arquivo ira causar um erro no programa ao ser importado.  
Os parâmetros, tipo de variáveis e descrições são apresentadas abaixo, sendo “string” letras, “int” números inteiros e “float” números decimais utilizando “.” (ponto) como separador decimal.


* Optimizer: string, otimizador a ser utilizado, “ESO” ou “BESO” (sem aspas).
* EvolutionaryRate: float, taxa evolutiva, usualmente 0.02 para BESO e 0.01 para ESO.
* MinimumDensity: float, densidade mínima para o método de interpolação de material, usualmente 0.001.
* Penalty: float, penalização para o método de interpolação de material, usualmente 3.
* MinimumAreaRatio: float, razão de área do design final pelo design inicial, mesma restrição de volume.
* FilterRadius: float, raio do filtro de sensibilidades em metros.
* PlotType: string, tipo de mapa de cores a ser utilizado, “mises” para tensões de von Mises e “sensibilities” para sensibilidades (sem aspas).
* PrintAll: int, esta variável define se o programa deve salvar o design de todas as iterações do processo de otimização, 1 para sim e 0 para não.
* DPI: int, resolução das imagens a serem salvas em pontos por polegadas (dots per inch).
* Surfaces: lista de strings, nomes das superfícies definidas na malha, devem ser listadas todas as superfícies definidas como physical groups no programa Gmsh ou todas as superfícies listadas na seção “$Surfaces” no modelo de malha “txt”, utilizar nomes sem aspas e separados por um espaço simples.
* SurfacesType: lista de int, lista do tipo das superfícies listadas em Surfaces, devem ser definidas todas as superfícies, utilizar 0 para superfícies passivas (que não são alteradas pelo processo de otimização) e 1 para domínios de design, separar os valores por um espaço simples.
* Boundaries: lista de strings, nomes das condições de contorno do problema, devem ser listados todos os physical groups definidos no programa Gmsh que não sejam superfícies (pontos e curvas) ou todas as condições de contorno listadas na seção “$Boundaries” no modelo de malha “txt”, utilizar nomes sem aspas e separados por um espaço simples.
* BoundariesType: lista de int, lista do tipo das condições de contorno listadas em Boundaries, devem ser definidas todas as condições de contorno, utilizar 0 para condição de contorno de carregamento e 1 para deslocamento prescrito, separar valores por um espaço simples.
* BoundariesValues: lista de floats, lista dos valores das condições de contorno, são definidos 2 valores por condição de contorno, valor em x e valor em y, valores são separados por um espaço simples e podem ser agrupados utilizando colchetes (“[ ]”) para melhor visualização, utilizar “null” (sem aspas) para não definir um valor em alguma direção.
* Thickness: float, espessura dos elementos finitos.
* YoungModule: float, módulo de elasticidade do material.
* PoissonRatio: float, coeficiente de poisson do material.
* UseParalellism: int, esta variável define se o programa deve utilizar múltiplos processos para a identificação dos elementos dentro do raio do filtro de sensibilidades, 1 para sim e 0 para não.
* Treads: int, número de processos paralelos gerados pelo programa, deve ser definido mesmo que UseParalellism seja 0, utilizar “default” (sem aspas) para utilizar o número de processadores.
* Chuncksize: int, número de elementos analisados por processo, quanto maior este número mais rápido será a execução da função e menos precisa será a estimativa de tempo, esta variável deve ser definida mesmo que UseParalellism seja 0, utilizar “default” (sem aspas) para utilizar o número de elementos divido pelo número de processos.

##### Modelo de malha em txt

O modelo de malha em “txt” foi desenvolvido para permitir o uso de outros geradores de malha na ferramenta. A formatação do modelo “txt” foi inspirado pelo modelo de malha gerado pelo programa open-sourse Gmsh, contendo listas de superfícies, condições de contorno, nós e elementos. Um template e exemplo do modelo de malha podem ser encontrados na pasta “models” distribuída em conjunto com o programa. É importante notar que as tags identificadoras dos nós e elementos utilizadas no modelo não precisam ser numeradas linearmente.
