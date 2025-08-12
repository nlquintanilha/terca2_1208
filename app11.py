import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import hashlib

# Configuração da página Streamlit
st.set_page_config(
    page_title="Sistema de Nutrigenética",
    page_icon="🧬",
    layout="wide"
)

class DatabaseManager:
    """
    Classe responsável por gerenciar todas as operações do banco de dados SQLite.
    Centraliza a criação de tabelas e operações CRUD (Create, Read, Update, Delete).
    """
    
    def __init__(self, db_name="nutrigenetica.db"):
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_name (str): Nome do arquivo do banco de dados SQLite
        """
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """
        Cria e retorna uma conexão com o banco de dados SQLite.
        
        Returns:
            sqlite3.Connection: Objeto de conexão com o banco
        """
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """
        Inicializa o banco de dados criando todas as tabelas necessárias.
        Executa apenas se as tabelas não existirem (IF NOT EXISTS).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela GENES - Armazena informações sobre genes estudados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genes (
                gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_gene TEXT NOT NULL UNIQUE,
                descricao TEXT,
                funcao_biologica TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela MARCADORES - Polimorfismos SNP com nível de evidência
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marcadores (
                marcador_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gene_id INTEGER NOT NULL,
                rs_number TEXT NOT NULL UNIQUE,
                tipo_variante TEXT,
                alelos TEXT,
                descricao_marcador TEXT,
                nivel_evidencia TEXT CHECK (nivel_evidencia IN ('Forte', 'Moderada', 'Limitada', 'Insuficiente')),
                score_evidencia REAL CHECK (score_evidencia >= 0 AND score_evidencia <= 10),
                referencias_pmid TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gene_id) REFERENCES genes (gene_id)
            )
        ''')
        
        # Tabela PACIENTES - Dados dos pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                paciente_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_paciente TEXT NOT NULL,
                cpf TEXT UNIQUE,
                data_nascimento DATE,
                sexo TEXT CHECK (sexo IN ('M', 'F')),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela RESULTADOS_ANALISES - Liga pacientes aos marcadores com interpretações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados_analises (
                resultado_id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                marcador_id INTEGER NOT NULL,
                genotipo_encontrado TEXT NOT NULL,
                interpretacao_clinica TEXT,
                recomendacao_nutricional TEXT,
                nivel_risco TEXT CHECK (nivel_risco IN ('Baixo', 'Moderado', 'Alto')),
                data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (paciente_id),
                FOREIGN KEY (marcador_id) REFERENCES marcadores (marcador_id),
                UNIQUE(paciente_id, marcador_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def inserir_gene(self, nome_gene, descricao, funcao_biologica):
        """
        Insere um novo gene no banco de dados.
        
        Args:
            nome_gene (str): Nome do gene (ex: MTHFR)
            descricao (str): Descrição do gene
            funcao_biologica (str): Função biológica do gene
            
        Returns:
            bool: True se inserido com sucesso, False caso contrário
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO genes (nome_gene, descricao, funcao_biologica)
                VALUES (?, ?, ?)
            ''', (nome_gene, descricao, funcao_biologica))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def inserir_marcador(self, gene_id, rs_number, tipo_variante, alelos, 
                        descricao_marcador, nivel_evidencia, score_evidencia, referencias_pmid):
        """
        Insere um novo marcador SNP no banco de dados.
        
        Args:
            gene_id (int): ID do gene associado
            rs_number (str): Número RS do SNP (ex: rs1801133)
            tipo_variante (str): Tipo de variante (ex: missense)
            alelos (str): Alelos possíveis (ex: C/T)
            descricao_marcador (str): Descrição do marcador
            nivel_evidencia (str): Nível de evidência científica
            score_evidencia (float): Score numérico da evidência (0-10)
            referencias_pmid (str): PMIDs das referências científicas
            
        Returns:
            bool: True se inserido com sucesso, False caso contrário
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO marcadores (gene_id, rs_number, tipo_variante, alelos, 
                                      descricao_marcador, nivel_evidencia, score_evidencia, referencias_pmid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (gene_id, rs_number, tipo_variante, alelos, descricao_marcador, 
                  nivel_evidencia, score_evidencia, referencias_pmid))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def inserir_paciente(self, nome_paciente, cpf, data_nascimento, sexo):
        """
        Insere um novo paciente no banco de dados.
        
        Args:
            nome_paciente (str): Nome completo do paciente
            cpf (str): CPF do paciente
            data_nascimento (date): Data de nascimento
            sexo (str): Sexo (M/F)
            
        Returns:
            int or None: ID do paciente inserido ou None se erro
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pacientes (nome_paciente, cpf, data_nascimento, sexo)
                VALUES (?, ?, ?, ?)
            ''', (nome_paciente, cpf, data_nascimento, sexo))
            conn.commit()
            paciente_id = cursor.lastrowid
            conn.close()
            return paciente_id
        except sqlite3.IntegrityError:
            return None
    
    def inserir_resultado_analise(self, paciente_id, marcador_id, genotipo_encontrado, 
                                 interpretacao_clinica, recomendacao_nutricional, 
                                 nivel_risco, observacoes=""):
        """
        Insere um resultado de análise genética no banco de dados.
        
        Args:
            paciente_id (int): ID do paciente
            marcador_id (int): ID do marcador analisado
            genotipo_encontrado (str): Genótipo encontrado no paciente
            interpretacao_clinica (str): Interpretação clínica do resultado
            recomendacao_nutricional (str): Recomendação nutricional
            nivel_risco (str): Nível de risco (Baixo/Moderado/Alto)
            observacoes (str): Observações adicionais
            
        Returns:
            bool: True se inserido com sucesso, False caso contrário
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO resultados_analises 
                (paciente_id, marcador_id, genotipo_encontrado, interpretacao_clinica, 
                 recomendacao_nutricional, nivel_risco, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (paciente_id, marcador_id, genotipo_encontrado, interpretacao_clinica, 
                  recomendacao_nutricional, nivel_risco, observacoes))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_genes(self):
        """
        Recupera todos os genes cadastrados no banco de dados.
        
        Returns:
            pandas.DataFrame: DataFrame com informações dos genes
        """
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM genes ORDER BY nome_gene", conn)
        conn.close()
        return df
    
    def get_marcadores_por_gene(self, gene_id):
        """
        Recupera todos os marcadores de um gene específico.
        
        Args:
            gene_id (int): ID do gene
            
        Returns:
            pandas.DataFrame: DataFrame com marcadores do gene
        """
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT m.*, g.nome_gene 
            FROM marcadores m 
            JOIN genes g ON m.gene_id = g.gene_id 
            WHERE m.gene_id = ?
            ORDER BY m.rs_number
        ''', conn, params=(gene_id,))
        conn.close()
        return df
    
    def get_marcadores(self):
        """
        Recupera todos os marcadores com informações dos genes associados.
        
        Returns:
            pandas.DataFrame: DataFrame com todos os marcadores
        """
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT m.*, g.nome_gene 
            FROM marcadores m 
            JOIN genes g ON m.gene_id = g.gene_id 
            ORDER BY g.nome_gene, m.rs_number
        ''', conn)
        conn.close()
        return df
    
    def get_pacientes(self):
        """
        Recupera todos os pacientes cadastrados.
        
        Returns:
            pandas.DataFrame: DataFrame com informações dos pacientes
        """
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM pacientes ORDER BY nome_paciente", conn)
        conn.close()
        return df
    
    def get_relatorio_paciente(self, paciente_id):
        """
        Gera relatório completo de um paciente com todas suas análises.
        
        Args:
            paciente_id (int): ID do paciente
            
        Returns:
            pandas.DataFrame: DataFrame com relatório completo
        """
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT 
                p.nome_paciente,
                p.cpf,
                p.data_nascimento,
                p.sexo,
                g.nome_gene,
                m.rs_number,
                m.descricao_marcador,
                m.nivel_evidencia,
                m.score_evidencia,
                r.genotipo_encontrado,
                r.interpretacao_clinica,
                r.recomendacao_nutricional,
                r.nivel_risco,
                r.data_analise,
                r.observacoes
            FROM resultados_analises r
            JOIN pacientes p ON r.paciente_id = p.paciente_id
            JOIN marcadores m ON r.marcador_id = m.marcador_id
            JOIN genes g ON m.gene_id = g.gene_id
            WHERE p.paciente_id = ?
            ORDER BY g.nome_gene, m.rs_number
        ''', conn, params=(paciente_id,))
        conn.close()
        return df

# Função principal do Streamlit
def main():
    """
    Função principal da aplicação Streamlit.
    Gerencia a interface do usuário e a navegação entre páginas.
    """
    
    # Inicializa o gerenciador do banco de dados
    db = DatabaseManager()
    
    # Título principal da aplicação
    st.title("🧬 Sistema de Nutrigenética")
    st.markdown("### Análise de Polimorfismos SNP para Medicina Personalizada")
    
    # Sidebar para navegação entre funcionalidades
    st.sidebar.title("Navegação")
    opcao = st.sidebar.selectbox(
        "Escolha uma funcionalidade:",
        ["🏠 Home", "🧬 Cadastrar Gene", "📍 Cadastrar Marcador", 
         "👤 Cadastrar Paciente", "🔬 Registrar Análise", 
         "📊 Consultar Resultados", "📋 Relatórios"]
    )
    
    # Página inicial com informações sobre o sistema
    if opcao == "🏠 Home":
        st.markdown("""
        ## Bem-vindo ao Sistema de Nutrigenética!
        
        Este sistema foi desenvolvido para auxiliar profissionais da saúde na análise de 
        polimorfismos genéticos relacionados à nutrição e metabolismo.
        
        ### Funcionalidades:
        - **Cadastrar Genes**: Registre genes de interesse para estudos nutrigenéticos
        - **Cadastrar Marcadores**: Adicione polimorfismos SNP com níveis de evidência científica
        - **Cadastrar Pacientes**: Registre informações básicas dos pacientes
        - **Registrar Análises**: Insira resultados genéticos dos pacientes
        - **Consultar Resultados**: Visualize e compare resultados com evidências científicas
        - **Relatórios**: Gere relatórios completos por paciente
        
        ### Níveis de Evidência Científica:
        - **Forte**: Evidência robusta com múltiplos estudos confirmando a associação
        - **Moderada**: Evidência consistente, mas com algumas limitações
        - **Limitada**: Evidência preliminar que necessita confirmação
        - **Insuficiente**: Evidência inadequada para conclusões clínicas
        """)
        
        # Estatísticas básicas do banco de dados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            genes_count = len(db.get_genes())
            st.metric("Genes Cadastrados", genes_count)
        
        with col2:
            marcadores_count = len(db.get_marcadores())
            st.metric("Marcadores Cadastrados", marcadores_count)
        
        with col3:
            pacientes_count = len(db.get_pacientes())
            st.metric("Pacientes Cadastrados", pacientes_count)
        
        with col4:
            conn = db.get_connection()
            resultados_count = pd.read_sql_query("SELECT COUNT(*) as count FROM resultados_analises", conn).iloc[0]['count']
            conn.close()
            st.metric("Análises Realizadas", resultados_count)
    
    # Página para cadastro de genes
    elif opcao == "🧬 Cadastrar Gene":
        st.header("Cadastrar Novo Gene")
        
        with st.form("form_gene"):
            nome_gene = st.text_input("Nome do Gene*", placeholder="Ex: MTHFR")
            descricao = st.text_area("Descrição do Gene*", placeholder="Descreva a função e importância do gene")
            funcao_biologica = st.text_area("Função Biológica*", placeholder="Detalhe os processos biológicos envolvidos")
            
            submitted = st.form_submit_button("Cadastrar Gene")
            
            if submitted:
                if nome_gene and descricao and funcao_biologica:
                    if db.inserir_gene(nome_gene.upper(), descricao, funcao_biologica):
                        st.success(f"Gene {nome_gene} cadastrado com sucesso!")
                    else:
                        st.error("Gene já existe no banco de dados!")
                else:
                    st.error("Todos os campos são obrigatórios!")
        
        # Exibe genes já cadastrados
        st.subheader("Genes Cadastrados")
        genes_df = db.get_genes()
        if not genes_df.empty:
            st.dataframe(genes_df, use_container_width=True)
        else:
            st.info("Nenhum gene cadastrado ainda.")
    
    # Página para cadastro de marcadores SNP
    elif opcao == "📍 Cadastrar Marcador":
        st.header("Cadastrar Marcador SNP")
        
        genes_df = db.get_genes()
        if genes_df.empty:
            st.warning("É necessário cadastrar genes antes de adicionar marcadores!")
            return
        
        with st.form("form_marcador"):
            # Seleção do gene
            gene_opcoes = {row['nome_gene']: row['gene_id'] for _, row in genes_df.iterrows()}
            gene_selecionado = st.selectbox("Gene*", options=list(gene_opcoes.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                rs_number = st.text_input("Número RS*", placeholder="Ex: rs1801133")
                tipo_variante = st.selectbox("Tipo de Variante*", 
                                           ["missense", "nonsense", "silent", "splice site", "frameshift", "indel"])
                alelos = st.text_input("Alelos*", placeholder="Ex: C/T")
            
            with col2:
                nivel_evidencia = st.selectbox("Nível de Evidência*", 
                                             ["Forte", "Moderada", "Limitada", "Insuficiente"])
                score_evidencia = st.slider("Score de Evidência (0-10)*", 0.0, 10.0, 5.0, 0.1)
                referencias_pmid = st.text_input("PMIDs (separados por vírgula)", placeholder="Ex: 12345678, 87654321")
            
            descricao_marcador = st.text_area("Descrição do Marcador*", 
                                            placeholder="Descreva o impacto funcional e associações clínicas")
            
            submitted = st.form_submit_button("Cadastrar Marcador")
            
            if submitted:
                if all([gene_selecionado, rs_number, tipo_variante, alelos, descricao_marcador]):
                    gene_id = gene_opcoes[gene_selecionado]
                    if db.inserir_marcador(gene_id, rs_number, tipo_variante, alelos, 
                                         descricao_marcador, nivel_evidencia, score_evidencia, referencias_pmid):
                        st.success(f"Marcador {rs_number} cadastrado com sucesso!")
                    else:
                        st.error("Marcador já existe no banco de dados!")
                else:
                    st.error("Campos obrigatórios devem ser preenchidos!")
        
        # Exibe marcadores cadastrados
        st.subheader("Marcadores Cadastrados")
        marcadores_df = db.get_marcadores()
        if not marcadores_df.empty:
            st.dataframe(marcadores_df[['nome_gene', 'rs_number', 'tipo_variante', 'alelos', 
                                      'nivel_evidencia', 'score_evidencia']], use_container_width=True)
        else:
            st.info("Nenhum marcador cadastrado ainda.")
    
    # Página para cadastro de pacientes
    elif opcao == "👤 Cadastrar Paciente":
        st.header("Cadastrar Paciente")
        
        with st.form("form_paciente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_paciente = st.text_input("Nome Completo*", placeholder="Nome completo do paciente")
                cpf = st.text_input("CPF", placeholder="000.000.000-00")
            
            with col2:
                data_nascimento = st.date_input("Data de Nascimento*", 
                                              min_value=date(1920, 1, 1), 
                                              max_value=date.today())
                sexo = st.selectbox("Sexo*", ["M", "F"])
            
            submitted = st.form_submit_button("Cadastrar Paciente")
            
            if submitted:
                if nome_paciente and data_nascimento and sexo:
                    paciente_id = db.inserir_paciente(nome_paciente, cpf, data_nascimento, sexo)
                    if paciente_id:
                        st.success(f"Paciente {nome_paciente} cadastrado com sucesso! ID: {paciente_id}")
                    else:
                        st.error("CPF já existe no banco de dados!")
                else:
                    st.error("Campos obrigatórios devem ser preenchidos!")
        
        # Exibe pacientes cadastrados
        st.subheader("Pacientes Cadastrados")
        pacientes_df = db.get_pacientes()
        if not pacientes_df.empty:
            st.dataframe(pacientes_df[['paciente_id', 'nome_paciente', 'cpf', 
                                     'data_nascimento', 'sexo', 'data_cadastro']], use_container_width=True)
        else:
            st.info("Nenhum paciente cadastrado ainda.")
    
    # Página para registrar análises genéticas
    elif opcao == "🔬 Registrar Análise":
        st.header("Registrar Análise Genética")
        
        pacientes_df = db.get_pacientes()
        marcadores_df = db.get_marcadores()
        
        if pacientes_df.empty or marcadores_df.empty:
            st.warning("É necessário ter pacientes e marcadores cadastrados para registrar análises!")
            return
        
        with st.form("form_analise"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleção do paciente
                paciente_opcoes = {f"{row['nome_paciente']} (ID: {row['paciente_id']})": row['paciente_id'] 
                                 for _, row in pacientes_df.iterrows()}
                paciente_selecionado = st.selectbox("Paciente*", options=list(paciente_opcoes.keys()))
                
                # Seleção do marcador
                marcador_opcoes = {f"{row['nome_gene']} - {row['rs_number']}": row['marcador_id'] 
                                 for _, row in marcadores_df.iterrows()}
                marcador_selecionado = st.selectbox("Marcador*", options=list(marcador_opcoes.keys()))
                
                genotipo_encontrado = st.text_input("Genótipo Encontrado*", placeholder="Ex: CC, CT, TT")
                nivel_risco = st.selectbox("Nível de Risco*", ["Baixo", "Moderado", "Alto"])
            
            with col2:
                interpretacao_clinica = st.text_area("Interpretação Clínica*", 
                                                   placeholder="Interpretação baseada na literatura científica")
                recomendacao_nutricional = st.text_area("Recomendação Nutricional*", 
                                                       placeholder="Recomendações específicas baseadas no genótipo")
                observacoes = st.text_area("Observações", placeholder="Observações adicionais (opcional)")
            
            submitted = st.form_submit_button("Registrar Análise")
            
            if submitted:
                if all([paciente_selecionado, marcador_selecionado, genotipo_encontrado, 
                       interpretacao_clinica, recomendacao_nutricional, nivel_risco]):
                    
                    paciente_id = paciente_opcoes[paciente_selecionado]
                    marcador_id = marcador_opcoes[marcador_selecionado]
                    
                    if db.inserir_resultado_analise(paciente_id, marcador_id, genotipo_encontrado, 
                                                   interpretacao_clinica, recomendacao_nutricional, 
                                                   nivel_risco, observacoes):
                        st.success("Análise registrada com sucesso!")
                    else:
                        st.error("Já existe uma análise para este paciente e marcador!")
                else:
                    st.error("Todos os campos obrigatórios devem ser preenchidos!")
    
    # Página para consulta de resultados
    elif opcao == "📊 Consultar Resultados":
        st.header("Consultar Resultados de Análises")
        
        pacientes_df = db.get_pacientes()
        if pacientes_df.empty:
            st.info("Nenhum paciente cadastrado ainda.")
            return
        
        # Seleção do paciente para consulta
        paciente_opcoes = {f"{row['nome_paciente']} (ID: {row['paciente_id']})": row['paciente_id'] 
                         for _, row in pacientes_df.iterrows()}
        paciente_selecionado = st.selectbox("Selecione um Paciente:", options=list(paciente_opcoes.keys()))
        
        if paciente_selecionado:
            paciente_id = paciente_opcoes[paciente_selecionado]
            relatorio = db.get_relatorio_paciente(paciente_id)
            
            if not relatorio.empty:
                # Informações do paciente
                st.subheader("Informações do Paciente")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Nome", relatorio.iloc[0]['nome_paciente'])
                with col2:
                    st.metric("CPF", relatorio.iloc[0]['cpf'] or "Não informado")
                with col3:
                    st.metric("Data Nasc.", relatorio.iloc[0]['data_nascimento'])
                with col4:
                    st.metric("Sexo", "Masculino" if relatorio.iloc[0]['sexo'] == 'M' else "Feminino")
                
                st.subheader("Resultados das Análises")
                
                # Para cada análise, mostra informações detalhadas
                for _, row in relatorio.iterrows():
                    with st.expander(f"🧬 {row['nome_gene']} - {row['rs_number']} | Risco: {row['nivel_risco']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Informações do Marcador:**")
                            st.write(f"**Gene:** {row['nome_gene']}")
                            st.write(f"**SNP:** {row['rs_number']}")
                            st.write(f"**Genótipo:** {row['genotipo_encontrado']}")
                            st.write(f"**Nível de Evidência:** {row['nivel_evidencia']}")
                            st.write(f"**Score de Evidência:** {row['score_evidencia']}/10")
                        
                        with col2:
                            st.markdown("**Resultado Clínico:**")
                            st.write(f"**Nível de Risco:** {row['nivel_risco']}")
                            st.write(f"**Data da Análise:** {row['data_analise']}")
                        
                        st.markdown("**Descrição do Marcador:**")
                        st.write(row['descricao_marcador'])
                        
                        st.markdown("**Interpretação Clínica:**")
                        st.write(row['interpretacao_clinica'])
                        
                        st.markdown("**Recomendação Nutricional:**")
                        st.write(row['recomendacao_nutricional'])
                        
                        if row['observacoes']:
                            st.markdown("**Observações:**")
                            st.write(row['observacoes'])
                
                # Resumo estatístico
                st.subheader("Resumo Estatístico")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_analises = len(relatorio)
                    st.metric("Total de Análises", total_analises)
                
                with col2:
                    risco_alto = len(relatorio[relatorio['nivel_risco'] == 'Alto'])
                    st.metric("Marcadores Alto Risco", risco_alto)
                
                with col3:
                    evidencia_forte = len(relatorio[relatorio['nivel_evidencia'] == 'Forte'])
                    st.metric("Evidência Forte", evidencia_forte)
                
            else:
                st.info("Nenhuma análise encontrada para este paciente.")
    
    # Página para relatórios gerais
    elif opcao == "📋 Relatórios":
        st.header("Relatórios do Sistema")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Genes", "Marcadores", "Pacientes", "Análises"])
        
        with tab1:
            st.subheader("Relatório de Genes")
            genes_df = db.get_genes()
            if not genes_df.empty:
                st.dataframe(genes_df, use_container_width=True)
                
                # Gráfico de genes por data de criação
                if len(genes_df) > 1:
                    genes_df['data_criacao'] = pd.to_datetime(genes_df['data_criacao'])
                    genes_por_mes = genes_df.groupby(genes_df['data_criacao'].dt.to_period('M')).size()
                    st.line_chart(genes_por_mes)
            else:
                st.info("Nenhum gene cadastrado.")
        
        with tab2:
            st.subheader("Relatório de Marcadores")
            marcadores_df = db.get_marcadores()
            if not marcadores_df.empty:
                st.dataframe(marcadores_df, use_container_width=True)
                
                # Distribuição por nível de evidência
                col1, col2 = st.columns(2)
                with col1:
                    evidencia_dist = marcadores_df['nivel_evidencia'].value_counts()
                    st.bar_chart(evidencia_dist)
                
                with col2:
                    # Score médio de evidência por gene
                    score_por_gene = marcadores_df.groupby('nome_gene')['score_evidencia'].mean().sort_values(ascending=False)
                    st.bar_chart(score_por_gene)
            else:
                st.info("Nenhum marcador cadastrado.")
        
        with tab3:
            st.subheader("Relatório de Pacientes")
            pacientes_df = db.get_pacientes()
            if not pacientes_df.empty:
                st.dataframe(pacientes_df, use_container_width=True)
                
                # Distribuição por sexo
                col1, col2 = st.columns(2)
                with col1:
                    sexo_dist = pacientes_df['sexo'].value_counts()
                    sexo_dist.index = ['Feminino' if x == 'F' else 'Masculino' for x in sexo_dist.index]
                    st.bar_chart(sexo_dist)
                
                with col2:
                    # Pacientes por mês de cadastro
                    pacientes_df['data_cadastro'] = pd.to_datetime(pacientes_df['data_cadastro'])
                    pacientes_por_mes = pacientes_df.groupby(pacientes_df['data_cadastro'].dt.to_period('M')).size()
                    if len(pacientes_por_mes) > 1:
                        st.line_chart(pacientes_por_mes)
            else:
                st.info("Nenhum paciente cadastrado.")
        
        with tab4:
            st.subheader("Relatório de Análises")
            conn = db.get_connection()
            
            # Query para estatísticas das análises
            analises_stats = pd.read_sql_query('''
                SELECT 
                    g.nome_gene,
                    m.rs_number,
                    m.nivel_evidencia,
                    r.nivel_risco,
                    COUNT(*) as total_analises
                FROM resultados_analises r
                JOIN marcadores m ON r.marcador_id = m.marcador_id
                JOIN genes g ON m.gene_id = g.gene_id
                GROUP BY g.nome_gene, m.rs_number, m.nivel_evidencia, r.nivel_risco
                ORDER BY total_analises DESC
            ''', conn)
            
            if not analises_stats.empty:
                st.dataframe(analises_stats, use_container_width=True)
                
                # Distribuição de risco
                risco_total = pd.read_sql_query('''
                    SELECT nivel_risco, COUNT(*) as total
                    FROM resultados_analises
                    GROUP BY nivel_risco
                ''', conn)
                
                if not risco_total.empty:
                    st.subheader("Distribuição de Níveis de Risco")
                    risco_chart = risco_total.set_index('nivel_risco')['total']
                    st.bar_chart(risco_chart)
            else:
                st.info("Nenhuma análise registrada ainda.")
            
            conn.close()

# Função para popular o banco com dados de exemplo
def popular_dados_exemplo():
    """
    Função para popular o banco de dados com dados de exemplo.
    Útil para demonstração e testes do sistema.
    """
    db = DatabaseManager()
    
    # Inserir genes de exemplo
    genes_exemplo = [
        ("MTHFR", "Metilenotetraidrofolato redutase", "Metabolismo do folato e homocisteína"),
        ("COMT", "Catecol-O-metiltransferase", "Metabolismo da dopamina e estrógenos"),
        ("APOE", "Apolipoproteína E", "Metabolismo lipídico e transporte de colesterol"),
        ("CYP1A2", "Citocromo P450 1A2", "Metabolismo da cafeína e xenobióticos"),
        ("FTO", "Fat mass and obesity-associated protein", "Regulação do apetite e metabolismo energético")
    ]
    
    for nome, desc, func in genes_exemplo:
        db.inserir_gene(nome, desc, func)
    
    # Inserir marcadores de exemplo
    marcadores_exemplo = [
        (1, "rs1801133", "missense", "C/T", "Variante C677T associada à redução da atividade enzimática", "Forte", 8.5, "17519439,18203168"),
        (1, "rs1801131", "missense", "A/C", "Variante A1298C com impacto moderado na função", "Moderada", 6.8, "17519439,19303062"),
        (2, "rs4680", "missense", "G/A", "Variante Val158Met afeta a atividade da COMT", "Forte", 9.2, "16648218,17992266"),
        (3, "rs429358", "missense", "T/C", "Variante associada ao risco de Alzheimer e metabolismo lipídico", "Forte", 9.8, "17173050,19060906"),
        (4, "rs762551", "upstream", "A/C", "Polimorfismo na região promotora afetando expressão", "Moderada", 7.3, "15832849,17035307")
    ]
    
    for marcador in marcadores_exemplo:
        db.inserir_marcador(*marcador)

# Executar a aplicação
if __name__ == "__main__":
    # Descomente a linha abaixo para popular com dados de exemplo na primeira execução
    # popular_dados_exemplo()
    
    main()