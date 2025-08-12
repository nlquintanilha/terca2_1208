import sqlite3
import pandas as pd
from datetime import datetime, date

def popular_banco_completo():
    """
    Popula o banco de dados com exemplos reais de genes, marcadores e pacientes
    relevantes para nutrigenética e medicina personalizada.
    """
    
    # Conectar ao banco
    conn = sqlite3.connect("nutrigenetica.db")
    cursor = conn.cursor()
    
    print("🧬 Populando banco com dados de exemplo...")
    
    # ========== GENES DE EXEMPLO ==========
    genes_nutrigenetica = [
        # Gene, Descrição, Função Biológica
        ("MTHFR", 
         "Metilenotetraidrofolato redutase - Gene crucial para o metabolismo do folato",
         "Codifica enzima que converte 5,10-metilenotetraidrofolato em 5-metiltetraidrofolato, forma ativa do folato. Essencial para síntese de DNA, metilação e metabolismo da homocisteína."),
        
        ("COMT", 
         "Catecol-O-metiltransferase - Metabolismo de neurotransmissores e estrógenos",
         "Degrada dopamina, norepinefrina e epinefrina. Também metaboliza catecolestrógenos. Importante para função cognitiva e metabolismo hormonal."),
        
        ("CYP1A2", 
         "Citocromo P450 1A2 - Principal enzima metabolizadora da cafeína",
         "Responsável pelo metabolismo de ~95% da cafeína consumida. Também metaboliza outros xenobióticos e medicamentos. Determina tolerância individual à cafeína."),
        
        ("APOE", 
         "Apolipoproteína E - Transporte lipídico e metabolismo do colesterol",
         "Proteína essencial para transporte de lipídios no plasma e cérebro. Influencia níveis de colesterol, resposta a dietas e risco cardiovascular e neurodegenerativo."),
        
        ("FTO", 
         "Fat mass and obesity-associated protein - Regulação do peso corporal",
         "Gene associado à obesidade e diabetes tipo 2. Regula o apetite, saciedade e gasto energético. Influencia resposta a diferentes tipos de dieta."),
        
        ("PPARA", 
         "Receptor ativado por proliferadores de peroxissoma alfa",
         "Fator de transcrição que regula metabolismo de ácidos graxos, gluconeogênese e inflamação. Importante para resposta a ácidos graxos ômega-3."),
        
        ("TCF7L2", 
         "Transcription factor 7-like 2 - Regulação da glicemia",
         "Fator de transcrição envolvido na via de sinalização Wnt. Crucial para homeostase da glicose e função das células beta pancreáticas."),
        
        ("MC4R", 
         "Receptor de melanocortina 4 - Regulação do apetite",
         "Receptor hipotalâmico que regula ingestão alimentar e gasto energético. Mutações causam obesidade severa e resistência à leptina."),
        
        ("FADS1", 
         "Fatty acid desaturase 1 - Síntese de ácidos graxos poli-insaturados",
         "Enzima que converte ácidos graxos essenciais em derivados de cadeia longa. Crucial para síntese de ácido araquidônico e DHA."),
        
        ("ALDH2", 
         "Aldeído desidrogenase 2 - Metabolismo do álcool",
         "Segunda enzima na via de metabolização do etanol. Variantes deficientes causam acúmulo de acetaldeído e intolerância ao álcool.")
    ]
    
    # Inserir genes
    for gene_data in genes_nutrigenetica:
        try:
            cursor.execute('''
                INSERT INTO genes (nome_gene, descricao, funcao_biologica)
                VALUES (?, ?, ?)
            ''', gene_data)
            print(f"✅ Gene {gene_data[0]} inserido")
        except sqlite3.IntegrityError:
            print(f"⚠️ Gene {gene_data[0]} já existe")
    
    conn.commit()
    
    # ========== MARCADORES SNP DE EXEMPLO ==========
    marcadores_snp = [
        # (gene_id, rs_number, tipo_variante, alelos, descricao, nivel_evidencia, score, pmids)
        
        # MTHFR (gene_id = 1)
        (1, "rs1801133", "missense", "C/T", 
         "Variante C677T (Ala222Val) - Reduz atividade enzimática em 35% (CT) a 70% (TT). Associada a níveis elevados de homocisteína, especialmente com baixo folato. Aumenta necessidade de folato e B12.",
         "Forte", 9.2, "17519439,18203168,19303062"),
        
        (1, "rs1801131", "missense", "A/C", 
         "Variante A1298C (Glu429Ala) - Reduz atividade enzimática em ~25%. Efeito sinérgico com C677T. Associada a níveis de folato e resposta a suplementação.",
         "Moderada", 7.8, "17519439,19303062,15389643"),
        
        # COMT (gene_id = 2)
        (2, "rs4680", "missense", "G/A", 
         "Variante Val158Met - Met/Met (AA) tem atividade enzimática 3-4x menor. Afeta degradação de dopamina no córtex pré-frontal. Influencia função cognitiva, estresse e metabolismo de estrógenos.",
         "Forte", 8.9, "16648218,17992266,18165968"),
        
        # CYP1A2 (gene_id = 3)
        (3, "rs762551", "upstream", "A/C", 
         "Variante -163C>A na região promotora. AA são metabolizadores rápidos de cafeína (~1A), CC são lentos (~1F). Determina tolerância à cafeína e risco cardiovascular associado.",
         "Forte", 8.7, "15832849,17035307,19664148"),
        
        (3, "rs2069514", "intron", "G/A", 
         "Variante intrônica em ligação com rs762551. Afeta expressão da CYP1A2. Relacionado à velocidade de metabolização da cafeína e outros substratos.",
         "Moderada", 6.8, "19664148,21270894"),
        
        # APOE (gene_id = 4)
        (4, "rs429358", "missense", "T/C", 
         "Variante que define alelo ε4 (junto com rs7412). ε4/ε4 tem níveis mais altos de colesterol LDL, maior risco cardiovascular e de Alzheimer. Responde melhor a dietas com baixo teor de gordura saturada.",
         "Forte", 9.5, "17173050,19060906,22677642"),
        
        (4, "rs7412", "missense", "C/T", 
         "Variante que define alelo ε2. ε2/ε2 tem níveis mais baixos de colesterol, proteção cardiovascular. Pode ter deficiência de vitamina E.",
         "Forte", 9.1, "17173050,19060906,22677642"),
        
        # FTO (gene_id = 5)
        (5, "rs9939609", "intron", "A/T", 
         "Variante mais estudada do FTO. AA têm 1.7x maior risco de obesidade, maior IMC (~1.2 kg/m²), maior ingestão calórica. Respondem melhor a dietas hipocalóricas e exercícios.",
         "Forte", 8.4, "17434869,18454148,19079260"),
        
        (5, "rs1558902", "intron", "A/T", 
         "Variante em ligação com rs9939609. AA associados a maior IMC, gordura corporal e ingestão energética. Interação significativa com atividade física.",
         "Moderada", 7.6, "18454148,19079260"),
        
        # PPARA (gene_id = 6)
        (6, "rs1800206", "missense", "G/C", 
         "Variante Leu162Val. CC têm maior resposta a ácidos graxos ômega-3, melhor perfil lipídico com suplementação. Associado à sensibilidade aos efeitos anti-inflamatórios dos ômega-3.",
         "Moderada", 7.2, "12730120,16720698,18178378"),
        
        # TCF7L2 (gene_id = 7)
        (7, "rs7903146", "intron", "C/T", 
         "Variante mais forte para diabetes tipo 2. TT têm 2x maior risco, pior função de células beta, maior glicemia pós-prandial. Respondem melhor a dietas com baixo índice glicêmico.",
         "Forte", 9.3, "16415884,17463246,18372903"),
        
        (7, "rs12255372", "intron", "G/T", 
         "Em ligação com rs7903146. TT associados a diabetes tipo 2, pior tolerância à glicose. Interação com carboidratos refinados.",
         "Forte", 8.8, "16415884,17463246"),
        
        # MC4R (gene_id = 8)
        (8, "rs17782313", "upstream", "T/C", 
         "Variante na região promotora. CC associados a maior IMC, circunferência da cintura, ingestão energética. Resposta diferencial a restrição calórica.",
         "Moderada", 7.1, "18454148,19079261,20376003"),
        
        # FADS1 (gene_id = 9)
        (9, "rs174547", "intron", "G/T", 
         "Variante que afeta atividade da FADS1. TT têm menor eficiência na conversão de ácido linoleico para araquidônico. Maior benefício com ômega-3 EPA/DHA pré-formado.",
         "Moderada", 7.4, "19148276,20565855,21829393"),
        
        # ALDH2 (gene_id = 10)
        (10, "rs671", "missense", "G/A", 
         "Variante Glu487Lys. AA têm deficiência completa da ALDH2, GA parcial. Causa síndrome de rubor facial com álcool. Proteção contra alcoolismo, mas maior risco de câncer esofágico.",
         "Forte", 9.8, "19244658,20691043,22051089")
    ]
    
    # Inserir marcadores
    for marcador_data in marcadores_snp:
        try:
            cursor.execute('''
                INSERT INTO marcadores 
                (gene_id, rs_number, tipo_variante, alelos, descricao_marcador, 
                 nivel_evidencia, score_evidencia, referencias_pmid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', marcador_data)
            print(f"✅ Marcador {marcador_data[1]} inserido")
        except sqlite3.IntegrityError:
            print(f"⚠️ Marcador {marcador_data[1]} já existe")
    
    conn.commit()
    
    # ========== PACIENTES DE EXEMPLO ==========
    pacientes_exemplo = [
        # (nome, cpf, data_nascimento, sexo)
        ("Maria Silva Santos", "123.456.789-01", "1985-03-15", "F"),
        ("João Carlos Oliveira", "987.654.321-02", "1978-11-22", "M"),
        ("Ana Paula Costa", "456.789.123-03", "1992-07-08", "F")
    ]
    
    # Inserir pacientes
    pacientes_ids = []
    for paciente_data in pacientes_exemplo:
        try:
            cursor.execute('''
                INSERT INTO pacientes (nome_paciente, cpf, data_nascimento, sexo)
                VALUES (?, ?, ?, ?)
            ''', paciente_data)
            paciente_id = cursor.lastrowid
            pacientes_ids.append(paciente_id)
            print(f"✅ Paciente {paciente_data[0]} inserido (ID: {paciente_id})")
        except sqlite3.IntegrityError:
            print(f"⚠️ Paciente {paciente_data[0]} já existe")
    
    conn.commit()
    
    # ========== RESULTADOS DE ANÁLISES ==========
    # Vamos criar análises para os 3 pacientes com perfis genéticos diferentes
    
    resultados_analises = [
        # Paciente 1: Maria Silva Santos - Perfil: Metabolizadora lenta, risco cardiovascular moderado
        # (paciente_id, marcador_id, genotipo, interpretacao, recomendacao, nivel_risco, observacoes)
        
        # MTHFR C677T - Homozigota variante
        (pacientes_ids[0] if pacientes_ids else 1, 1, "TT", 
         "Homozigota para variante C677T com redução de ~70% na atividade da MTHFR. Risco elevado de hiperhomocisteinemia, especialmente com deficiência de folato/B12.",
         "Suplementação com 5-metiltetraidrofolato (800-1000 mcg/dia), vitamina B12 (500-1000 mcg/dia) e vitamina B6 (25-50 mg/dia). Aumentar consumo de folatos naturais (vegetais verde-escuros).", 
         "Alto", "Monitorar níveis de homocisteína sérica anualmente"),
        
        # COMT Val158Met - Heterozigota
        (pacientes_ids[0] if pacientes_ids else 1, 3, "GA", 
         "Heterozigota para variante Val158Met com atividade intermediária da COMT. Degradação moderada de dopamina e catecolestrógenos.",
         "Suporte nutricional para neurotransmissores: magnésio (400 mg/dia), vitaminas do complexo B, antioxidantes (vitamina E, C). Evitar excesso de café (máximo 2 xícaras/dia).", 
         "Moderado", "Perfil equilibrado para função cognitiva"),
        
        # CYP1A2 - Metabolizadora lenta de cafeína
        (pacientes_ids[0] if pacientes_ids else 1, 4, "CC", 
         "Homozigota CC - metabolizadora lenta da cafeína. Maior meia-vida da cafeína (~6-8h vs 3-4h). Maior risco cardiovascular com consumo elevado.",
         "Limitar cafeína a 100-200 mg/dia (1-2 xícaras de café). Evitar cafeína após 14h. Preferir chás com menor teor de cafeína. Aumentar antioxidantes (polifenóis).", 
         "Moderado", "Sensibilidade aumentada aos efeitos da cafeína"),
        
        # APOE - Perfil protetor
        (pacientes_ids[0] if pacientes_ids else 1, 6, "CT", 
         "Heterozigota portando alelo ε2 (protetor). Níveis mais baixos de colesterol LDL, menor risco cardiovascular. Possível menor absorção de vitamina E.",
         "Dieta mediterrânea com ênfase em ômega-3, azeite extra virgem, nozes. Suplementar vitamina E (400 UI/dia). Manter atividade física regular.", 
         "Baixo", "Perfil genético favorável para longevidade"),
        
        # Paciente 2: João Carlos Oliveira - Perfil: Metabolizador rápido, predisposição à obesidade
        
        # FTO - Homozigota de risco
        (pacientes_ids[1] if len(pacientes_ids) > 1 else 2, 7, "AA", 
         "Homozigota AA com maior predisposição à obesidade. Aumento de ~3 kg no peso corporal, maior apetite e preferência por alimentos calóricos.",
         "Dieta hipocalórica estruturada (déficit 500-750 kcal/dia), exercícios regulares (150 min/semana moderado + 75 min intenso). Proteína 1.2-1.6 g/kg. Controle de porções rigoroso.", 
         "Alto", "Necessita acompanhamento nutricional intensivo"),
        
        # TCF7L2 - Heterozigota para diabetes
        (pacientes_ids[1] if len(pacientes_ids) > 1 else 2, 9, "CT", 
         "Heterozigota CT com risco aumentado (40%) para diabetes tipo 2. Pior função das células beta pancreáticas e maior glicemia pós-prandial.",
         "Dieta com baixo índice glicêmico, carboidratos complexos, fibras >30g/dia. Evitar açúcares refinados e bebidas açucaradas. Exercícios pós-prandiais. Cromo picolinato (200-400 mcg/dia).", 
         "Alto", "Monitorar glicemia e HbA1c semestralmente"),
        
        # CYP1A2 - Metabolizador rápido
        (pacientes_ids[1] if len(pacientes_ids) > 1 else 2, 4, "AA", 
         "Homozigota AA - metabolizador rápido da cafeína. Menor risco cardiovascular associado ao consumo de café. Possível efeito protetor com consumo moderado.",
         "Pode consumir até 400 mg cafeína/dia (4 xícaras de café) com segurança. Aproveitar benefícios antioxidantes do café. Manter hidratação adequada.", 
         "Baixo", "Tolerância aumentada à cafeína - pode usar como ergogênico"),
        
        # ALDH2 - Função normal
        (pacientes_ids[1] if len(pacientes_ids) > 1 else 2, 14, "GG", 
         "Homozigota GG com função normal da ALDH2. Metabolização eficiente do álcool sem acúmulo de acetaldeído.",
         "Consumo moderado de álcool se desejado (máximo 2 doses/dia). Priorizar vinhos tintos pelos antioxidantes. Sempre com alimentos para reduzir absorção.", 
         "Baixo", "Sem restrições genéticas para metabolismo do álcool"),
        
        # Paciente 3: Ana Paula Costa - Perfil: Jovem, necessidades específicas de ômega-3
        
        # FADS1 - Baixa eficiência de conversão
        (pacientes_ids[2] if len(pacientes_ids) > 2 else 3, 13, "TT", 
         "Homozigota TT com baixa atividade da FADS1. Conversão reduzida (50-70%) de ácido linoleico para araquidônico e de ALA para EPA/DHA.",
         "Suplementação com ômega-3 EPA/DHA pré-formado (1-2g/dia). Reduzir ômega-6 (óleos vegetais refinados). Preferir peixes gordos 3x/semana ou suplemento de óleo de peixe.", 
         "Moderado", "Dependência aumentada de ômega-3 de origem marinha"),
        
        # PPARA - Boa resposta a ômega-3
        (pacientes_ids[2] if len(pacientes_ids) > 2 else 3, 8, "CC", 
         "Homozigota CC com maior sensibilidade aos efeitos benéficos dos ácidos graxos ômega-3. Melhor resposta anti-inflamatória e no perfil lipídico.",
         "Maximizar consumo de ômega-3: peixes gordos, nozes, linhaça, chia. Suplemento EPA/DHA 1-2g/dia. Azeite extra virgem como gordura principal. Abacate, azeitonas.", 
         "Baixo", "Perfil genético favorável para benefícios dos ômega-3"),
        
        # MTHFR A1298C - Heterozigota
        (pacientes_ids[2] if len(pacientes_ids) > 2 else 3, 2, "AC", 
         "Heterozigota AC com redução moderada (25%) na atividade da MTHFR. Metabolismo do folato levemente comprometido, especialmente em mulheres em idade reprodutiva.",
         "Suplementação preventiva com metilfolato (400-800 mcg/dia), especialmente se planeja gravidez. Vitamina B12 (250 mcg/dia). Dieta rica em folatos naturais.", 
         "Moderado", "Importante para planejamento reprodutivo"),
        
        # MC4R - Heterozigota
        (pacientes_ids[2] if len(pacientes_ids) > 2 else 3, 12, "TC", 
         "Heterozigota TC com risco moderadamente aumentado para ganho de peso. Regulação do apetite e saciedade levemente comprometida.",
         "Dieta equilibrada com proteína adequada (1.0-1.2 g/kg), fibras >25g/dia para saciedade. Exercícios regulares. Atenção aos sinais de saciedade. Evitar alimentos ultraprocessados.", 
         "Moderado", "Preventivo - manter peso saudável desde jovem")
    ]
    
    # Inserir resultados das análises
    for resultado_data in resultados_analises:
        try:
            cursor.execute('''
                INSERT INTO resultados_analises 
                (paciente_id, marcador_id, genotipo_encontrado, interpretacao_clinica, 
                 recomendacao_nutricional, nivel_risco, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', resultado_data)
            print(f"✅ Análise inserida para paciente ID {resultado_data[0]}, marcador ID {resultado_data[1]}")
        except sqlite3.IntegrityError:
            print(f"⚠️ Análise já existe para paciente {resultado_data[0]}, marcador {resultado_data[1]}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Banco de dados populado com sucesso!")
    print("\n📊 Resumo dos dados inseridos:")
    print("• 10 genes relevantes para nutrigenética")
    print("• 14 marcadores SNP com evidência científica")
    print("• 3 pacientes com perfis genéticos distintos")
    print("• 12 análises genéticas completas")
    
    print("\n👥 Perfis dos Pacientes:")
    print("• Maria Silva Santos: Metabolizadora lenta, risco cardiovascular moderado")
    print("• João Carlos Oliveira: Predisposição à obesidade e diabetes, metabolizador rápido de cafeína")
    print("• Ana Paula Costa: Necessidades específicas de ômega-3, perfil reprodutivo")

def mostrar_estatisticas_banco():
    """
    Mostra estatísticas do banco de dados após população.
    """
    conn = sqlite3.connect("nutrigenetica.db")
    
    print("\n📈 Estatísticas do Banco de Dados:")
    print("=" * 50)
    
    # Genes por nível de evidência dos marcadores
    df_evidencia = pd.read_sql_query('''
        SELECT 
            m.nivel_evidencia,
            COUNT(*) as quantidade,
            AVG(m.score_evidencia) as score_medio
        FROM marcadores m
        GROUP BY m.nivel_evidencia
        ORDER BY score_medio DESC
    ''', conn)
    
    print("\n🧬 Marcadores por Nível de Evidência:")
    print(df_evidencia.to_string(index=False))
    
    # Análises por nível de risco
    df_risco = pd.read_sql_query('''
        SELECT 
            r.nivel_risco,
            COUNT(*) as quantidade
        FROM resultados_analises r
        GROUP BY r.nivel_risco
        ORDER BY 
            CASE r.nivel_risco 
                WHEN 'Alto' THEN 3 
                WHEN 'Moderado' THEN 2 
                ELSE 1 
            END DESC
    ''', conn)
    
    print("\n⚠️ Análises por Nível de Risco:")
    print(df_risco.to_string(index=False))
    
    # Genes mais analisados
    df_genes = pd.read_sql_query('''
        SELECT 
            g.nome_gene,
            COUNT(r.resultado_id) as total_analises
        FROM genes g
        LEFT JOIN marcadores m ON g.gene_id = m.gene_id
        LEFT JOIN resultados_analises r ON m.marcador_id = r.marcador_id
        GROUP BY g.nome_gene
        HAVING total_analises > 0
        ORDER BY total_analises DESC
    ''', conn)
    
    print("\n🏆 Genes Mais Analisados:")
    print(df_genes.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    # Execute esta função para popular o banco de dados
    popular_banco_completo()
    
    # Mostre estatísticas
    mostrar_estatisticas_banco()
    
    print("\n🚀 Agora você pode executar o sistema principal:")
    print("streamlit run nutrigenetica.py")