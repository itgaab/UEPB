"""Rotina típica de cada curso ("Um dia na vida").

Descrições gerais, escritas para dar uma ideia do dia a dia. A rotina real varia conforme o campus,
o período do curso e o local de trabalho. A chave é "Nome" ou "Nome|Grau" quando o bacharelado e a
licenciatura do mesmo curso são diferentes. Para editar, mude o texto de "aluno" ou "prof".
"""

DIA_A_DIA = {
    "Administração": {
        "aluno": "Aulas de contabilidade, marketing e gestão de pessoas, estudos de caso de empresas reais e muitos trabalhos em grupo.",
        "prof": "Planeja orçamentos, organiza equipes, analisa resultados e negocia com clientes e fornecedores.",
    },
    "Agroecologia": {
        "aluno": "Aulas em sala e em campo, manejo de solo e plantio, visitas a propriedades e projetos com agricultores familiares.",
        "prof": "Orienta produtores, planeja sistemas de produção que respeitam o ambiente e faz assistência técnica no campo.",
    },
    "Agronomia": {
        "aluno": "Química, solos e produção vegetal em sala, aulas práticas em lavouras e laboratórios e estágios no campo.",
        "prof": "Visita propriedades, recomenda cultivo e adubação, controla pragas e acompanha safras.",
    },
    "Arquivologia": {
        "aluno": "Organização de documentos, preservação, gestão da informação e sistemas digitais, com práticas em arquivos reais.",
        "prof": "Organiza, classifica e preserva documentos de órgãos públicos e empresas e cuida de arquivos digitais.",
    },
    "Ciências Biológicas|Bacharelado": {
        "aluno": "Genética, ecologia e microbiologia em sala, laboratório e saídas de campo para coleta e observação.",
        "prof": "Faz pesquisa em laboratório e no campo, analisa amostras, elabora laudos e projetos de conservação.",
    },
    "Ciências Biológicas|Licenciatura": {
        "aluno": "Estuda biologia e também como ensiná-la: didática, estágios em escolas e feiras de ciências.",
        "prof": "Dá aulas de ciências e biologia, prepara experimentos e acompanha turmas na escola.",
    },
    "Ciências Contábeis": {
        "aluno": "Contabilidade, impostos, auditoria e legislação, com muitos exercícios práticos e programas de contabilidade.",
        "prof": "Fecha balanços, calcula tributos, orienta empresas e audita contas.",
    },
    "Ciência da Computação": {
        "aluno": "Programação, estruturas de dados, algoritmos e matemática, com muitos projetos e laboratórios de código.",
        "prof": "Desenvolve sistemas, resolve problemas com código, trabalha em equipe e aprende tecnologias novas o tempo todo.",
    },
    "Direito": {
        "aluno": "Leitura de leis e casos, debates, redação de peças e prática em núcleos de assistência jurídica.",
        "prof": "Analisa casos, redige petições, negocia acordos e atua em audiências ou em órgãos públicos.",
    },
    "Educação Física|Bacharelado": {
        "aluno": "Anatomia, fisiologia e treinamento, com aulas práticas de esportes e avaliações físicas.",
        "prof": "Monta treinos, avalia condicionamento e acompanha pessoas em academias, clubes e projetos de saúde.",
    },
    "Educação Física|Licenciatura": {
        "aluno": "Estuda o corpo e o movimento e como ensinar esporte e cultura corporal, com estágios em escolas.",
        "prof": "Dá aulas de educação física, organiza atividades e jogos e acompanha o desenvolvimento dos alunos.",
    },
    "Enfermagem": {
        "aluno": "Anatomia e cuidado ao paciente, laboratórios de simulação e estágios em hospitais e unidades de saúde.",
        "prof": "Cuida de pacientes, administra medicações, coordena a equipe e orienta as famílias.",
    },
    "Engenharia Civil": {
        "aluno": "Cálculo, física, estruturas e materiais, com projetos, laboratórios e visitas a obras.",
        "prof": "Projeta e acompanha obras, calcula estruturas, faz orçamentos e fiscaliza a execução.",
    },
    "Engenharia Sanitária e Ambiental": {
        "aluno": "Química, hidráulica e ecologia, com aulas de laboratório e visitas a estações de tratamento.",
        "prof": "Projeta sistemas de água e esgoto, avalia impactos ambientais e cuida de licenciamento e resíduos.",
    },
    "Estatística": {
        "aluno": "Matemática, probabilidade e programação, com análise de dados reais no computador e muito uso de R ou Python.",
        "prof": "Coleta e analisa dados, constrói modelos e ajuda empresas e pesquisas a decidir com base em evidências.",
    },
    "Estatística e Ciência de Dados": {
        "aluno": "Estatística, programação e aprendizado de máquina, com projetos de análise de dados do início ao fim.",
        "prof": "Limpa e analisa grandes bases de dados, cria modelos e painéis e explica os resultados para quem decide.",
    },
    "Farmácia": {
        "aluno": "Química, farmacologia e análises clínicas, com muitas aulas de laboratório.",
        "prof": "Prepara e dispensa medicamentos, orienta pacientes, faz análises ou trabalha em indústrias e hospitais.",
    },
    "Filosofia": {
        "aluno": "Leitura e discussão de textos, lógica, ética e história das ideias, além de didática e estágios.",
        "prof": "Dá aulas, pesquisa, escreve e conduz debates sobre ética, política e conhecimento.",
    },
    "Física": {
        "aluno": "Cálculo, mecânica, eletricidade e experimentos, mais didática e estágios em escolas.",
        "prof": "Dá aulas de física e matemática, prepara experimentos e pode seguir para a pesquisa.",
    },
    "Fisioterapia": {
        "aluno": "Anatomia, biomecânica e técnicas de reabilitação, com atendimentos supervisionados em clínicas-escola.",
        "prof": "Avalia pacientes, monta planos de reabilitação e acompanha a evolução em clínicas e hospitais.",
    },
    "Geografia": {
        "aluno": "Território, clima, população e mapas, com trabalhos de campo e uso de geoprocessamento.",
        "prof": "Dá aulas, analisa território e meio ambiente e trabalha com mapas e planejamento urbano e rural.",
    },
    "História": {
        "aluno": "Leitura de fontes e textos, debates, pesquisa em arquivos e didática com estágios em escolas.",
        "prof": "Dá aulas, pesquisa e trabalha em museus, arquivos e projetos de patrimônio.",
    },
    "Jornalismo": {
        "aluno": "Redação, apuração, fotografia e vídeo, com produção de reportagens, rádio e conteúdo digital.",
        "prof": "Apura fatos, entrevista, escreve e edita reportagens para jornais, TV, rádio e internet.",
    },
    "Letras Espanhol": {
        "aluno": "Língua, literatura e cultura dos países hispânicos, prática de conversação e didática.",
        "prof": "Dá aulas de espanhol, traduz textos e produz conteúdo em outro idioma.",
    },
    "Letras Inglês": {
        "aluno": "Língua, literatura e cultura dos países de língua inglesa, prática de conversação e didática.",
        "prof": "Dá aulas de inglês, traduz textos e produz conteúdo em outro idioma.",
    },
    "Letras Português": {
        "aluno": "Gramática, literatura, produção de textos e didática, com leitura intensa e estágios em escolas.",
        "prof": "Dá aulas de língua e literatura, revisa e produz textos e trabalha com cultura e educação.",
    },
    "Matemática": {
        "aluno": "Cálculo, álgebra e geometria, muita resolução de problemas e didática com estágios em escolas.",
        "prof": "Dá aulas de matemática, prepara turmas para provas e pode seguir para a pesquisa ou a análise de dados.",
    },
    "Odontologia": {
        "aluno": "Anatomia, materiais e técnicas, com laboratórios e atendimento supervisionado em clínicas-escola.",
        "prof": "Atende pacientes, faz diagnósticos e tratamentos e administra o consultório.",
    },
    "Pedagogia": {
        "aluno": "Psicologia da aprendizagem, didática e gestão escolar, com estágios em creches e escolas.",
        "prof": "Dá aulas na educação infantil e nos anos iniciais, planeja atividades e apoia a gestão da escola.",
    },
    "Psicologia": {
        "aluno": "Teorias do comportamento, desenvolvimento humano e métodos de pesquisa, com estágios e atendimento supervisionado.",
        "prof": "Escuta, avalia e acompanha pessoas em clínicas, escolas, empresas ou serviços de saúde.",
    },
    "Química": {
        "aluno": "Química geral e orgânica, laboratórios e didática, com estágios em escolas.",
        "prof": "Dá aulas de química, prepara experimentos e pode seguir para a pesquisa.",
    },
    "Química Industrial": {
        "aluno": "Química, processos e laboratórios, com análise de amostras e visão de produção industrial.",
        "prof": "Controla a qualidade, otimiza processos e analisa materiais em indústrias e laboratórios.",
    },
    "Relações Internacionais": {
        "aluno": "Política internacional, economia, história e idiomas, com debates e simulações de organismos como a ONU.",
        "prof": "Analisa cenários globais e atua em comércio exterior, organizações e órgãos públicos.",
    },
    "Serviço Social": {
        "aluno": "Políticas públicas, direitos, sociologia e ética, com estágios em serviços sociais.",
        "prof": "Atende famílias, orienta sobre direitos e benefícios e atua em políticas de assistência, saúde e educação.",
    },
    "Sociologia": {
        "aluno": "Teoria social, pesquisa e debates sobre desigualdade e cultura, com didática e estágios.",
        "prof": "Dá aulas, pesquisa a sociedade e trabalha com pesquisa social e políticas públicas.",
    },
    "Tecnologia em Análise e Desenvolvimento de Sistemas": {
        "aluno": "Programação, bancos de dados e desenvolvimento web e mobile, com muita prática em projetos.",
        "prof": "Desenvolve e mantém sistemas, sites e aplicativos e dá suporte a equipes e clientes.",
    },
    "Tecnologia em Ciência de Dados": {
        "aluno": "Programação, estatística e análise de dados, com projetos práticos e ferramentas usadas no mercado.",
        "prof": "Prepara e analisa dados, cria relatórios e painéis e apoia as decisões de empresas.",
    },
    "Tecnologia em Sistemas de Energias Renováveis": {
        "aluno": "Eletricidade, energia solar e eólica, com aulas práticas e visitas a usinas e instalações.",
        "prof": "Projeta e instala sistemas de energia solar e eólica e cuida da manutenção e da eficiência energética.",
    },
}
